#!/usr/bin/env python3
"""
Create release promotion and patch-bump pull requests from develop.
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
import tomllib
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Sequence

VERSION_PATTERN = re.compile(r"^(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)$")


@dataclass(frozen=True)
class Version:
    """Semantic version without a build component."""

    major: int
    minor: int
    patch: int

    def as_string(self) -> str:
        """Return the version formatted as MAJOR.MINOR.PATCH."""
        return f"{self.major}.{self.minor}.{self.patch}"

    def as_branch_label(self) -> str:
        """Return the version formatted for use in branch names."""
        return self.as_string().replace(".", "-")


def parse_arguments(argument_list: Sequence[str] | None = None) -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description=(
            "Create a develop->release PR via a promotion branch and a patch-bump PR to develop. "
            "The patch bump increments PATCH."
        )
    )
    parser.add_argument(
        "--remote",
        default="origin",
        help="Git remote used for fetch and push.",
    )
    parser.add_argument(
        "--develop-branch",
        default="develop",
        help="Branch used as the source for releases.",
    )
    parser.add_argument(
        "--release-branch",
        default="release",
        help="Branch used for release promotion.",
    )
    parser.add_argument(
        "--patch-branch-name",
        default=None,
        help="Explicit branch name for the patch bump PR.",
    )
    parser.add_argument(
        "--promotion-branch-name",
        default=None,
        help="Explicit branch name for the release promotion PR.",
    )
    parser.add_argument(
        "--release-title",
        default=None,
        help="Optional title for the release pull request.",
    )
    parser.add_argument(
        "--release-body",
        default=None,
        help="Optional body for the release pull request.",
    )
    parser.add_argument(
        "--release-body-file",
        dest="release_body_file",
        default=None,
        help="Optional body file for the release pull request.",
    )
    parser.add_argument(
        "--patch-title",
        default=None,
        help="Optional title for the patch bump pull request.",
    )
    parser.add_argument(
        "--patch-body",
        default=None,
        help="Optional body for the patch bump pull request.",
    )
    parser.add_argument(
        "--patch-body-file",
        dest="patch_body_file",
        default=None,
        help="Optional body file for the patch bump pull request.",
    )
    parser.add_argument(
        "--draft",
        action="store_true",
        help="Create both pull requests as drafts.",
    )
    parser.add_argument(
        "--no-target-merge",
        action="store_true",
        help="Skip merging the release branch into the promotion branch.",
    )
    parser.add_argument(
        "--no-fetch",
        action="store_true",
        help="Skip fetching the develop and release branches from the remote.",
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


def ensure_on_develop(current_branch: str, develop_branch: str) -> None:
    """Ensure the current branch is the develop branch."""
    if current_branch != develop_branch:
        raise SystemExit(f"Switch to '{develop_branch}' before running this script.")


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


def fetch_branches(remote_name: str, develop_branch: str, release_branch: str) -> None:
    """Fetch the develop and release branches from the remote."""
    run_command(("git", "fetch", remote_name, develop_branch))
    run_command(("git", "fetch", remote_name, release_branch))


def ensure_branch_matches_remote(remote_name: str, branch_name: str) -> None:
    """Ensure the local branch matches the remote tracking branch."""
    remote_reference = f"{remote_name}/{branch_name}"
    local_commit = read_command_output(("git", "rev-parse", branch_name))
    remote_commit = read_command_output(("git", "rev-parse", remote_reference))
    if local_commit != remote_commit:
        raise SystemExit(f"{branch_name} must match {remote_reference} before releasing.")


def parse_version(version_value: str) -> Version:
    """Parse and validate a version string."""
    match = VERSION_PATTERN.match(version_value)
    if not match:
        raise SystemExit(f"Invalid version format: {version_value}")
    major, minor, patch = (int(part) for part in match.groups())
    return Version(major=major, minor=minor, patch=patch)


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


def load_develop_version(develop_branch: str) -> Version:
    """Load the version from the develop branch."""
    pyproject_text = read_command_output(("git", "show", f"{develop_branch}:pyproject.toml"))
    return load_version_from_toml_text(pyproject_text)


def bump_patch_version(version: Version) -> Version:
    """Return the next patch version."""
    return Version(
        major=version.major,
        minor=version.minor,
        patch=version.patch + 1,
    )


def update_pyproject_version(current_version: Version, new_version: Version) -> None:
    """Update the version string in pyproject.toml."""
    pyproject_path = Path("pyproject.toml")
    content = pyproject_path.read_text()
    version_pattern = re.compile(r'^(version\s*=\s*")([^"]+)(")\s*$', re.MULTILINE)
    matches = list(version_pattern.finditer(content))
    if len(matches) != 1:
        raise SystemExit("Expected a single version entry in pyproject.toml.")

    match = matches[0]
    existing_version = match.group(2)
    if existing_version != current_version.as_string():
        raise SystemExit("pyproject.toml version does not match expected value.")

    updated = content[: match.start(2)] + new_version.as_string() + content[match.end(2) :]
    pyproject_path.write_text(updated)


def commit_patch_bump(new_version: Version) -> None:
    """Commit the patch bump."""
    run_command(("git", "add", "pyproject.toml"))
    commit_message = f"chore: bump patch version to {new_version.as_string()}"
    run_command(("git", "commit", "-m", commit_message))


def create_patch_branch_name(version: Version) -> str:
    """Generate a unique patch branch name."""
    timestamp = datetime.now(UTC).strftime("%Y%m%d%H%M%S")
    return f"feature/patch-bump-{version.as_branch_label()}-{timestamp}"


def create_promotion_branch_name(version: Version) -> str:
    """Generate a unique release promotion branch name."""
    timestamp = datetime.now(UTC).strftime("%Y%m%d%H%M%S")
    return f"promotion/release-{version.as_branch_label()}-{timestamp}"


def ensure_branch_available(branch_name: str) -> None:
    """Ensure the branch name is not already in use."""
    result = subprocess.run(("git", "show-ref", "--verify", "--quiet", f"refs/heads/{branch_name}"))
    if result.returncode == 0:
        raise SystemExit(f"Branch already exists: {branch_name}")


def merge_target_branch(branch_name: str, target_reference: str) -> None:
    """Merge the target branch into the promotion branch."""
    result = run_command(("git", "merge", target_reference), check=False)
    if result.returncode == 0:
        return
    raise SystemExit(
        "Merge conflict while preparing the promotion branch. "
        f"Resolve conflicts on '{branch_name}', commit the merge, and retry PR creation."
    )


def run_validation(base_ref: str) -> None:
    """Run the canonical local validation."""
    result = run_command(
        (sys.executable, "scripts/dev/validate_local.py", "--base-ref", base_ref),
        check=False,
    )
    if result.returncode != 0:
        raise SystemExit(result.returncode)


def create_release_pull_request(
    promotion_branch: str,
    release_branch: str,
    release_version: Version,
    arguments: argparse.Namespace,
) -> None:
    """Create the promotion->release pull request."""
    command = [
        "gh",
        "pr",
        "create",
        "--base",
        release_branch,
        "--head",
        promotion_branch,
    ]
    if arguments.draft:
        command.append("--draft")
    title = arguments.release_title or f"Release {release_version.as_string()}"
    command.extend(["--title", title])
    if arguments.release_body_file:
        command.extend(["--body-file", arguments.release_body_file])
    elif arguments.release_body is not None:
        command.extend(["--body", arguments.release_body])
    else:
        command.extend(["--body", ""])
    run_command(tuple(command))


def create_patch_pull_request(
    patch_branch_name: str,
    develop_branch: str,
    patch_version: Version,
    arguments: argparse.Namespace,
) -> None:
    """Create the patch bump pull request."""
    command = [
        "gh",
        "pr",
        "create",
        "--base",
        develop_branch,
        "--head",
        patch_branch_name,
    ]
    if arguments.draft:
        command.append("--draft")
    title = arguments.patch_title or f"chore: bump patch version to {patch_version.as_string()}"
    command.extend(["--title", title])
    if arguments.patch_body_file:
        command.extend(["--body-file", arguments.patch_body_file])
    elif arguments.patch_body is not None:
        command.extend(["--body", arguments.patch_body])
    else:
        command.extend(["--body", ""])
    run_command(tuple(command))


def main(argument_list: Sequence[str] | None = None) -> int:
    """Entry point for creating release pull requests."""
    arguments = parse_arguments(argument_list)

    ensure_project_root()
    ensure_executable_available("git")
    ensure_executable_available("gh")
    ensure_clean_worktree()

    if not arguments.no_fetch:
        fetch_branches(arguments.remote, arguments.develop_branch, arguments.release_branch)

    current_branch = get_current_branch()
    ensure_on_develop(current_branch, arguments.develop_branch)
    ensure_branch_matches_remote(arguments.remote, arguments.develop_branch)
    ensure_no_open_pull_requests(arguments.release_branch)
    ensure_no_open_pull_requests(arguments.develop_branch)

    develop_version = load_develop_version(arguments.develop_branch)
    patch_version = bump_patch_version(develop_version)

    patch_branch_name = arguments.patch_branch_name or create_patch_branch_name(patch_version)
    promotion_branch_name = arguments.promotion_branch_name or create_promotion_branch_name(develop_version)
    ensure_branch_available(patch_branch_name)
    ensure_branch_available(promotion_branch_name)

    run_command(("git", "checkout", "-b", promotion_branch_name))
    if not arguments.no_target_merge:
        merge_target_branch(promotion_branch_name, f"{arguments.remote}/{arguments.release_branch}")
    run_validation(arguments.release_branch)
    run_command(("git", "push", "--set-upstream", arguments.remote, promotion_branch_name))
    create_release_pull_request(
        promotion_branch_name,
        arguments.release_branch,
        develop_version,
        arguments,
    )

    run_command(("git", "checkout", arguments.develop_branch))
    run_command(("git", "checkout", "-b", patch_branch_name))
    update_pyproject_version(develop_version, patch_version)
    commit_patch_bump(patch_version)
    run_validation(arguments.develop_branch)
    run_command(("git", "push", "--set-upstream", arguments.remote, patch_branch_name))
    create_patch_pull_request(
        patch_branch_name,
        arguments.develop_branch,
        patch_version,
        arguments,
    )

    run_command(("git", "checkout", arguments.develop_branch))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
