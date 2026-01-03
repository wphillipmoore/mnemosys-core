"""
Alembic revision wrapper enforcing message conventions.
"""

from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
from collections.abc import Sequence

MAX_MESSAGE_LENGTH = 60
MESSAGE_PATTERN = re.compile(r"^[a-z0-9]+(?:_[a-z0-9]+)*$")


def parse_arguments(argument_list: Sequence[str] | None = None) -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Create Alembic revisions with enforced naming.")
    parser.add_argument(
        "message",
        help="Short snake_case message describing the change.",
    )
    parser.add_argument(
        "--config",
        dest="alembic_configuration_path",
        default=None,
        help="Optional path to alembic.ini.",
    )
    parser.add_argument(
        "--no-autogenerate",
        dest="autogenerate",
        action="store_false",
        help="Disable Alembic autogenerate.",
    )
    parser.set_defaults(autogenerate=True)
    return parser.parse_args(list(argument_list) if argument_list is not None else None)


def validate_message(message: str) -> list[str]:
    """Return a list of validation errors for the message."""
    errors: list[str] = []
    if not MESSAGE_PATTERN.match(message):
        errors.append("Message must be snake_case with lowercase letters, digits, and underscores only.")
    if len(message) > MAX_MESSAGE_LENGTH:
        errors.append(f"Message must be {MAX_MESSAGE_LENGTH} characters or fewer.")
    return errors


def validate_alembic_available() -> bool:
    """Return True if alembic is on PATH."""
    return shutil.which("alembic") is not None


def build_command(arguments: argparse.Namespace) -> list[str]:
    """Build the Alembic revision command."""
    command: list[str] = ["alembic"]
    if arguments.alembic_configuration_path:
        command.extend(["--config", arguments.alembic_configuration_path])
    command.extend(["revision", "-m", arguments.message])
    if arguments.autogenerate:
        command.append("--autogenerate")
    return command


def main(argument_list: Sequence[str] | None = None) -> int:
    """Entry point for the Alembic revision wrapper."""
    arguments = parse_arguments(argument_list)

    if not validate_alembic_available():
        print("ERROR: alembic command not found on PATH.", file=sys.stderr)
        return 2

    errors = validate_message(arguments.message)
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 2

    command = build_command(arguments)
    result = subprocess.run(command, check=False)
    return result.returncode


if __name__ == "__main__":
    sys.exit(main())
