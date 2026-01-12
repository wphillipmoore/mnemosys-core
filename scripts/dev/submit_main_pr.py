#!/usr/bin/env python3
"""
Create a release->main pull request with validation and guardrails.
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path
from typing import TYPE_CHECKING

import tomllib

if TYPE_CHECKING:
    from collections.abc import Sequence


def parse_arguments(argument_list: Sequence[str] | None = None) -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Create a release->main pull request.")
    parser.add_argument(
        "--remote",
        default="origin",
        help="Git remote used for fetch.",
    )
    parser.add_argument(
        "--release-branch",
        default="release",
        help="Branch used for release promotion.",
    )
    parser.add_argument(
        "--main-branch",
        default="main",
        help="Branch used for production promotion.",
    )
    parser.add_argument(
        "--title",
        default=None,
        help="Optional pull request title.",
    )
    parser.add_argument(
        "--body",
        default=None,
        help="Optional pull request body. Use for single-line bodies.",
    )
    parser.add_argument(
        "--body-file",
        dest="body_file",
        default=None,
        help="Optional path to a pull request body file.",
    )
    parser.add_argument(
        "--draft",
        action="store_true",
        help="Create the pull request as a draft.",
    )
    parser.add_argument(
        "--no-fetch",
        action="store_true",
        help="Skip fetching the release and main branches from the remote.",
    )
    return parser.parse_args(list(argument_list) if argument_list is not None else None)


def ensure_project_root() -> None:
    """Fail fast if invoked outside the repository root."""
    if not Path("pyproject.toml").is_file():
        raise SystemExit("Run from the repository root (pyproject.toml missing).")


def ensure_executable_available(executable: str) -> None:
    """Ensure a required executable is available."""
    if shutil.which(executable) is None:
        raise SystemExit(f"Required executable not found on PATH: {executable}")


def run_command(command: Sequence[str], check: bool = True) -> subprocess.CompletedProcess[str]:
    """Run a command and return the completed process."""
    return subprocess.run(command, check=check)


def read_command_output(command: Sequence[str]) -> str:
    """Run a command and return its stripped standard output."""
    result = subprocess.run(command, check=True, text=True, capture_output=True)
    return result.stdout.strip()


def ensure_clean_worktree() -> None:
    """Ensure there are no uncommitted changes."""
    status_output = read_command_output(("git", "status", "--porcelain"))
    if status_output:
        raise SystemExit("Working tree must be clean before preparing releases.")


def get_current_branch() -> str:
    """Return the current git branch name."""
    return read_command_output(("git", "rev-parse", "--abbrev-ref", "HEAD"))


def ensure_on_branch(current_branch: str, expected_branch: str) -> None:
    """Ensure the current branch matches expectations."""
    if current_branch != expected_branch:
        raise SystemExit(f"Switch to '{expected_branch}' before running this script.")


def fetch_branches(remote_name: str, release_branch: str, main_branch: str) -> None:
    """Fetch the release and main branches from the remote."""
    run_command(("git", "fetch", remote_name, release_branch))
    run_command(("git", "fetch", remote_name, main_branch))


def ensure_branch_matches_remote(remote_name: str, branch_name: str) -> None:
    """Ensure the local branch matches the remote tracking branch."""
    remote_reference = f"{remote_name}/{branch_name}"
    local_commit = read_command_output(("git", "rev-parse", branch_name))
    remote_commit = read_command_output(("git", "rev-parse", remote_reference))
    if local_commit != remote_commit:
        raise SystemExit(f"{branch_name} must match {remote_reference} before promoting.")


def list_open_pull_requests(base_branch: str) -> list[dict[str, object]]:
    """Return open pull requests that target the base branch."""
    output = read_command_output(
        (
            "gh",
            "pr",
            "list",
            "--state",
            "open",
            "--base",
            base_branch,
            "--json",
            "number,title,headRefName",
        )
    )
    try:
        data = json.loads(output)
    except json.JSONDecodeError as exc:
        raise SystemExit("Unable to parse gh pr list output.") from exc
    if not isinstance(data, list):
        raise SystemExit("Unexpected gh pr list output format.")
    return data


def ensure_no_open_pull_requests(base_branch: str) -> None:
    """Fail if open pull requests already target the base branch."""
    pull_requests = list_open_pull_requests(base_branch)
    if not pull_requests:
        return
    details = []
    for pull_request in pull_requests:
        number = pull_request.get("number")
        title = pull_request.get("title")
        head_reference_name = pull_request.get("headRefName")
        details.append(f"#{number} {head_reference_name}: {title}")
    details_text = "\n".join(details)
    raise SystemExit(f"Open pull requests already target {base_branch}:\n{details_text}")


def load_version_label() -> str:
    """Load the version string for display."""
    data = tomllib.loads(Path("pyproject.toml").read_text())
    try:
        version_value = data["tool"]["poetry"]["version"]
    except KeyError as exc:
        raise SystemExit("Missing tool.poetry.version in pyproject.toml.") from exc
    if not isinstance(version_value, str):
        raise SystemExit("tool.poetry.version must be a string.")
    return version_value


def run_validation() -> None:
    """Run the canonical local validation."""
    result = run_command((sys.executable, "scripts/dev/validate_local.py"), check=False)
    if result.returncode != 0:
        raise SystemExit(result.returncode)


def create_pull_request(arguments: argparse.Namespace, release_branch: str, main_branch: str) -> None:
    """Create the release->main pull request."""
    command = ["gh", "pr", "create", "--base", main_branch, "--head", release_branch]
    if arguments.draft:
        command.append("--draft")

    if arguments.title:
        command.extend(["--title", arguments.title])
    else:
        version_label = load_version_label()
        command.extend(["--title", f"Promote release {version_label}"])

    if arguments.body_file:
        command.extend(["--body-file", arguments.body_file])
    elif arguments.body is not None:
        command.extend(["--body", arguments.body])
    else:
        command.extend(["--body", ""])

    run_command(tuple(command))


def main(argument_list: Sequence[str] | None = None) -> int:
    """Entry point for creating a release->main pull request."""
    arguments = parse_arguments(argument_list)

    ensure_project_root()
    ensure_executable_available("git")
    ensure_executable_available("gh")
    ensure_clean_worktree()

    if not arguments.no_fetch:
        fetch_branches(arguments.remote, arguments.release_branch, arguments.main_branch)

    current_branch = get_current_branch()
    ensure_on_branch(current_branch, arguments.release_branch)
    ensure_branch_matches_remote(arguments.remote, arguments.release_branch)
    ensure_no_open_pull_requests(arguments.main_branch)

    run_validation()
    create_pull_request(arguments, arguments.release_branch, arguments.main_branch)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
