#!/usr/bin/env python3
"""
Validate version string rules for CI.
"""

from __future__ import annotations

import argparse
import os
import re
import subprocess
import tomllib
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Sequence

VERSION_PATTERN = re.compile(
    r"^(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)$"
)


@dataclass(frozen=True)
class Version:
    """Semantic version with build component."""

    major: int
    minor: int
    patch: int
    build: int

    def as_string(self) -> str:
        """Return the version formatted as MAJOR.MINOR.PATCH.BUILD."""
        return f"{self.major}.{self.minor}.{self.patch}.{self.build}"

    def as_tuple(self) -> tuple[int, int, int, int]:
        """Return the version as a comparison tuple."""
        return (self.major, self.minor, self.patch, self.build)


def parse_arguments(argument_list: Sequence[str] | None = None) -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Validate MNEMOSYS version string rules in CI.",
    )
    parser.add_argument(
        "--base-ref",
        default=None,
        help="Base branch reference for comparison (defaults to GITHUB_BASE_REF).",
    )
    parser.add_argument(
        "--event-name",
        default=None,
        help="Event name override (defaults to GITHUB_EVENT_NAME).",
    )
    return parser.parse_args(list(argument_list) if argument_list is not None else None)


def ensure_project_root() -> None:
    """Fail fast if invoked outside the repository root."""
    if not Path("pyproject.toml").is_file():
        raise SystemExit("Run from the repository root (pyproject.toml missing).")


def read_command_output(command: Sequence[str]) -> str:
    """Run a command and return its stripped standard output."""
    result = subprocess.run(command, check=True, text=True, capture_output=True)
    return result.stdout.strip()


def git_reference_exists(reference: str) -> bool:
    """Return True if the git reference exists."""
    result = subprocess.run(("git", "rev-parse", "--verify", "--quiet", reference))
    return result.returncode == 0


def resolve_base_reference(base_reference: str) -> str:
    """Resolve a base reference to an existing git ref."""
    if git_reference_exists(base_reference):
        return base_reference
    remote_reference = f"origin/{base_reference}"
    if git_reference_exists(remote_reference):
        return remote_reference
    raise SystemExit(
        "Base reference not found. Fetch the base branch before running version checks."
    )


def parse_version(version_value: str) -> Version:
    """Parse and validate a version string."""
    match = VERSION_PATTERN.match(version_value)
    if not match:
        raise SystemExit(f"Invalid version format: {version_value}")
    major, minor, patch, build = (int(match.group(index)) for index in range(1, 5))
    return Version(major=major, minor=minor, patch=patch, build=build)


def load_version_from_toml_text(toml_text: str) -> Version:
    """Load the version from a pyproject.toml text block."""
    data = tomllib.loads(toml_text)
    version_value = None
    project_section = data.get("project")
    if isinstance(project_section, dict):
        version_value = project_section.get("version")
    if version_value is None:
        tool_section = data.get("tool")
        poetry_section = tool_section.get("poetry") if isinstance(tool_section, dict) else None
        if isinstance(poetry_section, dict):
            version_value = poetry_section.get("version")
    if version_value is None:
        raise SystemExit(
            "Missing version in pyproject.toml (expected project.version or tool.poetry.version)."
        )
    if not isinstance(version_value, str):
        raise SystemExit("Version value in pyproject.toml must be a string.")
    return parse_version(version_value)


def load_version_from_worktree() -> Version:
    """Load the version from the working tree."""
    pyproject_text = Path("pyproject.toml").read_text(encoding="utf-8")
    return load_version_from_toml_text(pyproject_text)


def load_version_from_git(reference: str) -> Version:
    """Load the version from a git reference."""
    pyproject_text = read_command_output(("git", "show", f"{reference}:pyproject.toml"))
    return load_version_from_toml_text(pyproject_text)


def ensure_version_is_greater(base_version: Version, head_version: Version, base_reference: str) -> None:
    """Ensure the head version is greater than the base."""
    if head_version.as_tuple() <= base_version.as_tuple():
        raise SystemExit(
            "Version must advance relative to the base branch. "
            f"Base ({base_reference}) is {base_version.as_string()}, "
            f"head is {head_version.as_string()}."
        )


def validate_develop_rules(base_version: Version, head_version: Version) -> None:
    """Validate develop-bound version rules."""
    if (head_version.major, head_version.minor, head_version.patch) == (
        base_version.major,
        base_version.minor,
        base_version.patch,
    ):
        expected_build = base_version.build + 1
        if head_version.build != expected_build:
            raise SystemExit(
                "BUILD must increment by exactly 1 for develop PRs. "
                f"Expected {expected_build}, got {head_version.build}."
            )
        return

    if (head_version.major, head_version.minor) == (base_version.major, base_version.minor):
        expected_patch = base_version.patch + 1
        if head_version.patch != expected_patch:
            raise SystemExit(
                "PATCH must increment by exactly 1 when MAJOR/MINOR are unchanged. "
                f"Expected {expected_patch}, got {head_version.patch}."
            )
        if head_version.build != 0:
            raise SystemExit("BUILD must reset to 0 when PATCH increments.")
        return

    if head_version.patch != 0 or head_version.build != 0:
        raise SystemExit("PATCH and BUILD must reset to 0 when MAJOR or MINOR changes.")


def main() -> int:
    arguments = parse_arguments()
    ensure_project_root()

    head_version = load_version_from_worktree()

    base_reference = arguments.base_ref or os.environ.get("GITHUB_BASE_REF")
    event_name = arguments.event_name or os.environ.get("GITHUB_EVENT_NAME", "")
    if base_reference and (event_name == "pull_request" or arguments.base_ref is not None):
        resolved_base = resolve_base_reference(base_reference)
        base_version = load_version_from_git(resolved_base)
        ensure_version_is_greater(base_version, head_version, resolved_base)

        base_branch = resolved_base.split("/")[-1]
        if base_branch == "develop":
            validate_develop_rules(base_version, head_version)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
