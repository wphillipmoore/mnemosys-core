"""
Automated Alembic migration runners for upgrade and downgrade.
"""

from __future__ import annotations

import argparse
import logging
import os
import shutil
import subprocess
import sys
import time
from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Sequence

from sqlalchemy.engine import make_url

from mnemosys_core.config.environments import Environment
from mnemosys_core.config.settings import Settings, load_admin_settings_from_env

LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True)
class AlembicCommandResult:
    """Structured result for Alembic command execution."""

    command: list[str]
    return_code: int
    standard_output: str
    standard_error: str
    duration_seconds: float


def parse_arguments(argument_list: Sequence[str] | None = None) -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Run Alembic migration automation.")
    parser.add_argument(
        "--alembic-config",
        dest="alembic_configuration_path",
        default=None,
        help="Optional path to alembic.ini (overrides ALEMBIC_CONFIG).",
    )

    subparsers = parser.add_subparsers(dest="action", required=True)
    subparsers.add_parser("upgrade", help="Run automated Alembic upgrade.")

    downgrade_parser = subparsers.add_parser("downgrade", help="Run automated Alembic downgrade.")
    downgrade_parser.add_argument(
        "--target",
        dest="downgrade_target",
        default=None,
        help="Target revision for downgrade (overrides MNEMOSYS_DOWNGRADE_TARGET).",
    )

    return parser.parse_args(list(argument_list) if argument_list is not None else None)


def resolve_alembic_configuration_path(arguments: argparse.Namespace) -> str | None:
    """Resolve Alembic configuration path from CLI or environment."""
    return arguments.alembic_configuration_path or os.getenv("ALEMBIC_CONFIG")


def validate_required_environment() -> list[str]:
    """Return a list of missing required environment variables."""
    missing_variables: list[str] = []
    if not os.getenv("MNEMOSYS_ENV"):
        missing_variables.append("MNEMOSYS_ENV")
    if not os.getenv("DATABASE_URL"):
        missing_variables.append("DATABASE_URL")
    return missing_variables


def validate_environment_name(environment_name: str) -> bool:
    """Validate that MNEMOSYS_ENV matches a known environment."""
    try:
        Environment(environment_name)
    except ValueError:
        return False
    return True


def validate_alembic_command_available() -> bool:
    """Return True when the alembic command is available on PATH."""
    return shutil.which("alembic") is not None


def format_database_url(database_url: str) -> str:
    """Return a redacted database URL string."""
    try:
        return make_url(database_url).render_as_string(hide_password=True)
    except Exception:
        return "<unparseable database url>"


def log_environment_context(settings: Settings) -> None:
    """Log migration runner environment context."""
    environment_name = os.getenv("MNEMOSYS_ENV", "<missing>")

    LOGGER.info("Migration runner starting.")
    LOGGER.info("Environment: %s", environment_name)
    LOGGER.info("Database URL: %s", format_database_url(settings.database_url))
    LOGGER.info("Database schema: %s", settings.database_schema)


def build_alembic_command(
    command_arguments: Sequence[str],
    alembic_configuration_path: str | None,
) -> list[str]:
    """Build the Alembic CLI command with optional configuration path."""
    command: list[str] = ["alembic"]
    if alembic_configuration_path:
        command.extend(["--config", alembic_configuration_path])
    command.extend(command_arguments)
    return command


def run_alembic_command(
    command_arguments: Sequence[str],
    alembic_configuration_path: str | None,
) -> AlembicCommandResult:
    """Run an Alembic command and capture output."""
    command = build_alembic_command(command_arguments, alembic_configuration_path)
    start_time = time.monotonic()
    completed = subprocess.run(command, capture_output=True, text=True, check=False)
    duration_seconds = time.monotonic() - start_time
    return AlembicCommandResult(
        command=command,
        return_code=completed.returncode,
        standard_output=completed.stdout,
        standard_error=completed.stderr,
        duration_seconds=duration_seconds,
    )


def log_command_result(result: AlembicCommandResult) -> None:
    """Log command execution result."""
    LOGGER.info(
        "Command finished with code %s in %.2fs: %s",
        result.return_code,
        result.duration_seconds,
        " ".join(result.command),
    )
    if result.standard_output.strip():
        LOGGER.info("stdout: %s", result.standard_output.strip())
    if result.standard_error.strip():
        LOGGER.warning("stderr: %s", result.standard_error.strip())


def run_upgrade(alembic_configuration_path: str | None) -> int:
    """Run the automated Alembic upgrade sequence."""
    check_result = run_alembic_command(["check"], alembic_configuration_path)
    log_command_result(check_result)
    if check_result.return_code == 0:
        LOGGER.info("Alembic check succeeded. No upgrade required.")
        return 0

    LOGGER.info("Alembic check failed. Attempting upgrade.")
    upgrade_result = run_alembic_command(["upgrade", "heads"], alembic_configuration_path)
    log_command_result(upgrade_result)
    if upgrade_result.return_code == 0:
        LOGGER.info("Alembic upgrade completed successfully.")
        return 0

    LOGGER.warning("Alembic upgrade failed. Re-checking schema state.")
    recheck_result = run_alembic_command(["check"], alembic_configuration_path)
    log_command_result(recheck_result)
    if recheck_result.return_code == 0:
        LOGGER.warning("Schema is now at head after failed upgrade; assuming concurrency.")
        return 0

    LOGGER.error("Schema remains out of sync after failed upgrade.")
    return 1


def should_verify_downgrade_target(target_revision: str) -> bool:
    """Return True when the downgrade target should be verified."""
    if target_revision == "base":
        return False
    return len(target_revision) >= 8


def run_downgrade(alembic_configuration_path: str | None, target_revision: str) -> int:
    """Run the automated Alembic downgrade sequence."""
    LOGGER.info("Downgrading to revision: %s", target_revision)
    downgrade_result = run_alembic_command(
        ["downgrade", target_revision],
        alembic_configuration_path,
    )
    log_command_result(downgrade_result)
    if downgrade_result.return_code != 0:
        LOGGER.error("Alembic downgrade failed.")
        return 1

    if not should_verify_downgrade_target(target_revision):
        LOGGER.info("Skipping downgrade verification for target: %s", target_revision)
        return 0

    LOGGER.info("Verifying downgrade target via alembic current.")
    current_result = run_alembic_command(["current"], alembic_configuration_path)
    log_command_result(current_result)
    if current_result.return_code != 0:
        LOGGER.error("Unable to verify current revision after downgrade.")
        return 1

    current_output = f"{current_result.standard_output}\n{current_result.standard_error}"
    if target_revision in current_output:
        LOGGER.info("Downgrade verification succeeded.")
        return 0

    LOGGER.error("Downgrade verification failed. Target revision not found.")
    return 1


def main(argument_list: Sequence[str] | None = None) -> int:
    """Entry point for the migration runner CLI."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(levelname)-5.5s [%(name)s] %(message)s",
    )
    arguments = parse_arguments(argument_list)

    missing_variables = validate_required_environment()
    if missing_variables:
        LOGGER.error("Missing required environment variables: %s", ", ".join(missing_variables))
        return 2

    environment_name = os.environ["MNEMOSYS_ENV"]
    if not validate_environment_name(environment_name):
        LOGGER.error("Invalid MNEMOSYS_ENV value: %s", environment_name)
        return 2

    if not validate_alembic_command_available():
        LOGGER.error("Alembic command not found on PATH.")
        return 2

    settings = load_admin_settings_from_env()
    log_environment_context(settings)

    alembic_configuration_path = resolve_alembic_configuration_path(arguments)
    if arguments.action == "upgrade":
        return run_upgrade(alembic_configuration_path)

    downgrade_target = arguments.downgrade_target or os.getenv("MNEMOSYS_DOWNGRADE_TARGET")
    if not downgrade_target:
        LOGGER.error("MNEMOSYS_DOWNGRADE_TARGET is required for downgrade.")
        return 2

    return run_downgrade(alembic_configuration_path, downgrade_target)


if __name__ == "__main__":
    sys.exit(main())
