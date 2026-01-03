#!/usr/bin/env python3
"""
Validate Alembic upgrade/downgrade against a temporary schema.
"""

from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
import uuid
from contextlib import contextmanager
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Iterator, Sequence

from sqlalchemy import text
from sqlalchemy.pool import NullPool

from mnemosys_core.config.settings import load_settings_from_env
from mnemosys_core.db.engine import create_db_engine
from mnemosys_core.migrations import runner

SCHEMA_PATTERN = re.compile(r"^[a-z0-9_]+$")


@contextmanager
def temporary_environment(overrides: dict[str, str]) -> Iterator[None]:
    """Temporarily override environment variables."""
    previous_values = {key: os.getenv(key) for key in overrides}
    for key, value in overrides.items():
        os.environ[key] = value
    try:
        yield
    finally:
        for key, value in previous_values.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value


def parse_arguments(argument_list: Sequence[str] | None = None) -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Validate Alembic migrations in a temp schema.")
    parser.add_argument(
        "--schema-prefix",
        default="mnemosys_tmp",
        help="Prefix for temporary schema name.",
    )
    parser.add_argument(
        "--keep-schema",
        action="store_true",
        help="Keep the temporary schema after validation (for debugging).",
    )
    parser.add_argument(
        "--seed-script",
        default=None,
        help="Optional path to a Python seed script to run after upgrade.",
    )
    return parser.parse_args(list(argument_list) if argument_list is not None else None)


def ensure_postgres_url(database_url: str) -> None:
    """Ensure the database URL targets PostgreSQL."""
    if not database_url.startswith("postgresql"):
        raise SystemExit("Migration validation requires a PostgreSQL database URL.")


def build_schema_name(prefix: str) -> str:
    """Generate a safe temporary schema name."""
    safe_prefix = prefix.strip("_").lower()
    if not SCHEMA_PATTERN.match(safe_prefix):
        raise SystemExit("Schema prefix must use lowercase letters, digits, and underscores only.")
    random_suffix = uuid.uuid4().hex[:8]
    return f"{safe_prefix}_{random_suffix}"


def create_schema(database_url: str, schema_name: str) -> None:
    """Create a temporary schema."""
    engine = create_db_engine(database_url, poolclass=NullPool)
    with engine.begin() as connection:
        connection.execute(text(f'CREATE SCHEMA "{schema_name}"'))


def drop_schema(database_url: str, schema_name: str) -> None:
    """Drop the temporary schema."""
    engine = create_db_engine(database_url, poolclass=NullPool)
    with engine.begin() as connection:
        connection.execute(text(f'DROP SCHEMA "{schema_name}" CASCADE'))


def run_seed_script(seed_script: str | None) -> int:
    """Run the optional seed script."""
    if not seed_script:
        return 0
    result = subprocess.run([sys.executable, seed_script], check=False)
    return result.returncode


def run_validation(database_url: str, schema_name: str, environment_name: str, seed_script: str | None) -> int:
    """Run upgrade and downgrade validation against the temporary schema."""
    overrides = {
        "MNEMOSYS_ENV": environment_name,
        "DATABASE_URL": database_url,
        "MNEMOSYS_DB_SCHEMA": schema_name,
        "MNEMOSYS_DOWNGRADE_TARGET": "base",
    }
    with temporary_environment(overrides):
        upgrade_result = runner.run_upgrade(None)
        if upgrade_result != 0:
            return upgrade_result

        seed_result = run_seed_script(seed_script)
        if seed_result != 0:
            return seed_result

        downgrade_result = runner.run_downgrade(None, "base")
        if downgrade_result != 0:
            return downgrade_result

        upgrade_again_result = runner.run_upgrade(None)
        return upgrade_again_result


def main(argument_list: Sequence[str] | None = None) -> int:
    """Entry point for migration validation."""
    if not runner.validate_alembic_command_available():
        raise SystemExit("Alembic command not found on PATH.")

    arguments = parse_arguments(argument_list)
    settings = load_settings_from_env()
    environment_name = settings.environment.value
    database_url = settings.database_url

    ensure_postgres_url(database_url)

    schema_name = build_schema_name(arguments.schema_prefix)
    create_schema(database_url, schema_name)
    try:
        return run_validation(database_url, schema_name, environment_name, arguments.seed_script)
    finally:
        if not arguments.keep_schema:
            drop_schema(database_url, schema_name)


if __name__ == "__main__":
    sys.exit(main())
