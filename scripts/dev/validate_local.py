#!/usr/bin/env python3
"""
Local validation helper mirroring CI hard gates.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

COMMANDS: tuple[tuple[str, ...], ...] = (
    ("poetry", "sync", "--dry-run"),
    ("poetry", "run", "ruff", "check"),
    ("poetry", "run", "mypy", "src/"),
    (
        "poetry",
        "run",
        "pytest",
        "--cov=mnemosys_core",
        "--cov-report=term-missing",
        "--cov-branch",
    ),
)


def ensure_project_root() -> None:
    """Fail fast if invoked outside the repository root."""
    if not Path("pyproject.toml").is_file():
        raise SystemExit("Run from the repository root (pyproject.toml missing).")


def run_command(command: tuple[str, ...]) -> int:
    """Run a command and return its exit code."""
    return subprocess.run(command).returncode


def main() -> int:
    ensure_project_root()

    for command in COMMANDS:
        print(f"Running: {' '.join(command)}")
        exit_code = run_command(command)
        if exit_code != 0:
            return exit_code

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
