"""
Postgres-backed migration validation using Testcontainers.
"""

from __future__ import annotations

import os
import subprocess
import sys
from typing import TYPE_CHECKING

import pytest
from testcontainers.postgres import PostgresContainer

if TYPE_CHECKING:
    from collections.abc import Iterator

POSTGRES_IMAGE = "postgres:16-alpine"


@pytest.fixture(scope="session")
def postgres_container() -> Iterator[PostgresContainer]:
    """Start a Postgres container for migration validation."""
    container = PostgresContainer(POSTGRES_IMAGE)
    container.start()
    try:
        yield container
    finally:
        container.stop()


def build_migration_environment(container: PostgresContainer) -> dict[str, str]:
    """Build environment variables for migration validation."""
    return {
        "MNEMOSYS_ENV": "sandbox",
        "MNEMOSYS_DB_ADMIN_DRIVERNAME": "postgresql",
        "MNEMOSYS_DB_ADMIN_USERNAME": container.username,
        "MNEMOSYS_DB_ADMIN_PASSWORD": container.password,
        "MNEMOSYS_DB_ADMIN_HOST": container.get_container_host_ip(),
        "MNEMOSYS_DB_ADMIN_PORT": str(container.get_exposed_port(5432)),
        "MNEMOSYS_DB_ADMIN_DATABASE": container.dbname,
    }


def run_migration_validation(environment: dict[str, str]) -> subprocess.CompletedProcess[str]:
    """Run the migration validation script with the provided environment."""
    return subprocess.run(
        [sys.executable, "scripts/dev/validate_migrations.py"],
        env=environment,
        capture_output=True,
        text=True,
        check=False,
    )


@pytest.mark.integration
def test_migrations_upgrade_downgrade(postgres_container: PostgresContainer) -> None:
    """Ensure migrations upgrade and downgrade cleanly on Postgres."""
    environment = os.environ.copy()
    environment.update(build_migration_environment(postgres_container))
    result = run_migration_validation(environment)
    if result.returncode == 0:
        return

    details: list[str] = []
    stdout = result.stdout.strip()
    stderr = result.stderr.strip()
    if stdout:
        details.append(f"stdout: {stdout}")
    if stderr:
        details.append(f"stderr: {stderr}")
    output = "\n".join(details) if details else "No output captured."
    pytest.fail(f"Alembic migration validation failed.\n{output}")
