"""
Code compliance tests.

These tests enforce code quality standards by running linting and type checking
tools as part of the test suite. This ensures that non-compliant code cannot
pass CI/CD or be accidentally pushed.
"""

import re
import subprocess
from pathlib import Path


def test_ruff_compliance() -> None:
    """
    Test that codebase passes ruff linting.

    Ruff enforces PEP 8 style guide and additional code quality rules.
    Configuration is in pyproject.toml [tool.ruff] section.
    """
    result = subprocess.run(
        ["ruff", "check", "src/", "tests/"],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, (
        f"Ruff linting failed. Run 'ruff check src/ tests/' to see errors.\n"
        f"Output:\n{result.stdout}\n{result.stderr}"
    )


def test_mypy_compliance() -> None:
    """
    Test that codebase passes mypy type checking.

    Mypy enforces strict type checking with complete type annotations.
    Configuration is in pyproject.toml [tool.mypy] section.
    """
    result = subprocess.run(
        ["mypy", "src/", "tests/"],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, (
        f"Mypy type checking failed. Run 'mypy src/ tests/' to see errors.\n"
        f"Output:\n{result.stdout}\n{result.stderr}"
    )


def test_venv_sync() -> None:
    """
    Test that virtual environment is in sync with poetry.lock.

    This ensures tests are running with correct dependencies and no stale
    packages are present. Developers should run 'poetry sync'
    to update their environment.
    """
    # Verify we're running from project root
    pyproject_path = Path("pyproject.toml")
    assert pyproject_path.exists(), "Must run tests from project root directory"

    result = subprocess.run(
        ["poetry", "sync", "--dry-run"],
        capture_output=True,
        text=True,
    )

    # poetry sync --dry-run returns 0 if no changes needed
    assert result.returncode == 0, (
        f"Virtual environment is out of sync with poetry.lock.\n"
        f"Run 'poetry sync' to update your environment.\n"
        f"Output:\n{result.stdout}\n{result.stderr}"
    )

    # Parse "Package operations: X installs, Y updates, Z removals, N skipped"
    # If X, Y, Z are all 0, then venv is in sync
    for line in result.stdout.splitlines():
        if "Package operations:" in line:
            # Extract numbers before "installs", "updates", and "removals"
            match = re.search(r"(\d+) installs?, (\d+) updates?, (\d+) removals?", line)
            if match:
                installs, updates, removals = map(int, match.groups())
                assert installs == 0 and updates == 0 and removals == 0, (
                    f"Virtual environment is out of sync with poetry.lock:\n"
                    f"  - {installs} package(s) to install\n"
                    f"  - {updates} package(s) to update\n"
                    f"  - {removals} package(s) to remove\n"
                    f"Run 'poetry sync' to synchronize your environment.\n"
                    f"\nFull output:\n{result.stdout}"
                )
            break
