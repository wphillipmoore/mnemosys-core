"""
Postgres-backed migration validation using Testcontainers.
"""

from __future__ import annotations

import os
import subprocess
import sys
import time
from dataclasses import dataclass
from typing import TYPE_CHECKING

import psycopg2
import pytest
from testcontainers.core.container import DockerContainer
from testcontainers.core.wait_strategies import LogMessageWaitStrategy

if TYPE_CHECKING:
    from collections.abc import Iterator

POSTGRES_IMAGE = "postgres:16-alpine"
POSTGRES_PASSWORD = "test"
POSTGRES_USERNAME = "test"
POSTGRES_DBNAME = "test"


@dataclass(frozen=True)
class PostgresTestContainer:
    """Container handle with Postgres connection metadata."""

    container: DockerContainer
    username: str
    password: str
    dbname: str

    def host(self) -> str:
        """Return the host for connecting to the container."""
        host = self.container.get_container_host_ip()
        if host in {"localhost", "::1"}:
            return "127.0.0.1"
        return host

    def port(self) -> str:
        """Return the exposed port for connecting to the container."""
        return str(self.container.get_exposed_port(5432))


@pytest.fixture(scope="session")
def postgres_container() -> Iterator[PostgresTestContainer]:
    """Start a Postgres container for migration validation."""
    docker_container = (
        DockerContainer(POSTGRES_IMAGE)
        .with_exposed_ports(5432)
        .with_env("POSTGRES_USER", POSTGRES_USERNAME)
        .with_env("POSTGRES_PASSWORD", POSTGRES_PASSWORD)
        .with_env("POSTGRES_DB", POSTGRES_DBNAME)
        .waiting_for(LogMessageWaitStrategy("database system is ready to accept connections"))
    )
    docker_container.start()
    postgres_container = PostgresTestContainer(
        container=docker_container,
        username=POSTGRES_USERNAME,
        password=POSTGRES_PASSWORD,
        dbname=POSTGRES_DBNAME,
    )
    try:
        wait_for_postgres(postgres_container)
        yield postgres_container
    finally:
        docker_container.stop()


def wait_for_postgres(
    container: PostgresTestContainer,
    timeout_seconds: float = 30.0,
    interval_seconds: float = 0.5,
) -> None:
    """Wait for the Postgres container to accept connections."""
    deadline = time.monotonic() + timeout_seconds
    last_error: Exception | None = None
    while time.monotonic() < deadline:
        try:
            connection = psycopg2.connect(
                dbname=container.dbname,
                user=container.username,
                password=container.password,
                host=container.host(),
                port=container.port(),
            )
            connection.close()
            return
        except psycopg2.OperationalError as error:
            last_error = error
            time.sleep(interval_seconds)
    raise RuntimeError(
        "Postgres container did not become ready before timeout. "
        f"Last error: {last_error}"
    )


def build_migration_environment(container: PostgresTestContainer) -> dict[str, str]:
    """Build environment variables for migration validation."""
    return {
        "MNEMOSYS_ENV": "sandbox",
        "MNEMOSYS_DB_ADMIN_DRIVERNAME": "postgresql",
        "MNEMOSYS_DB_ADMIN_USERNAME": container.username,
        "MNEMOSYS_DB_ADMIN_PASSWORD": container.password,
        "MNEMOSYS_DB_ADMIN_HOST": container.host(),
        "MNEMOSYS_DB_ADMIN_PORT": container.port(),
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
def test_migrations_upgrade_downgrade(postgres_container: PostgresTestContainer) -> None:
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
