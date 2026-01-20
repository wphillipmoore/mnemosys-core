#!/usr/bin/env python3
"""
Docs-only validation helper.
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
from pathlib import Path


def parse_arguments() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Run docs-only validation.")
    parser.add_argument(
        "--paths",
        nargs="*",
        default=None,
        help="Optional list of markdown files to validate.",
    )
    return parser.parse_args()


def ensure_project_root() -> None:
    """Fail fast if invoked outside the repository root."""
    if not Path("pyproject.toml").is_file():
        raise SystemExit("Run from the repository root (pyproject.toml missing).")


def gather_default_paths() -> list[str]:
    """Collect default markdown files for docs-only validation."""
    candidates: list[Path] = []
    docs_root = Path("docs")
    if docs_root.exists():
        candidates.extend(docs_root.rglob("*.md"))

    for filename in ("README.md", "CHANGELOG.md"):
        path = Path(filename)
        if path.is_file():
            candidates.append(path)

    unique_paths = sorted(set(candidates))
    return [str(path) for path in unique_paths]


def run_markdownlint(paths: list[str]) -> int:
    """Run markdownlint if available."""
    markdownlint = shutil.which("markdownlint")
    if not markdownlint:
        raise SystemExit(
            "markdownlint is required for docs-only validation. "
            "Install markdownlint and retry."
        )

    if not paths:
        print("No markdown files found to validate.")
        return 0

    command = (markdownlint, *paths)
    print(f"Running: {' '.join(command)}")
    return subprocess.run(command).returncode


def main() -> int:
    arguments = parse_arguments()
    ensure_project_root()

    paths = arguments.paths or gather_default_paths()
    return run_markdownlint(paths)


if __name__ == "__main__":
    raise SystemExit(main())
