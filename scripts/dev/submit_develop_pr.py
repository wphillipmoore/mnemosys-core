#!/usr/bin/env python3
"""
Prepare a pull request with pre-submission checks.
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Sequence

DOCUMENTATION_ONLY_FILENAMES = {"README.md", "CHANGELOG.md"}
FORBIDDEN_BRANCHES = {"develop", "main", "release"}


def parse_arguments(argument_list: Sequence[str] | None = None) -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Prepare a pull request by validating, pushing, and creating the PR."
    )
    parser.add_argument(
        "--base",
        default="develop",
        help="Target base branch for the pull request.",
    )
    parser.add_argument(
        "--remote",
        default="origin",
        help="Git remote used for fetch and push.",
    )
    parser.add_argument(
        "--title",
        default=None,
        help="Optional pull request title. Defaults to commit history or branch name.",
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
        "--force-validation",
        action="store_true",
        help="Run validation even when changes are docs-only.",
    )
    parser.add_argument(
        "--no-fetch",
        action="store_true",
        help="Skip fetching the base branch from the remote.",
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
        raise SystemExit("Working tree must be clean before preparing a pull request.")


def get_current_branch() -> str:
    """Return the current git branch name."""
    return read_command_output(("git", "rev-parse", "--abbrev-ref", "HEAD"))


def ensure_branch_allowed(current_branch: str, base_branch: str) -> None:
    """Prevent preparing pull requests from forbidden branches."""
    forbidden = FORBIDDEN_BRANCHES | {base_branch}
    if current_branch in forbidden:
        raise SystemExit(f"Refuse to run on branch '{current_branch}'.")


def ensure_base_branch_supported(base_branch: str) -> None:
    """Ensure the tool is only used for develop-bound pull requests."""
    if base_branch != "develop":
        raise SystemExit("submit_develop_pr supports only develop-bound pull requests.")


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


def git_reference_exists(reference: str) -> bool:
    """Return True if the git reference exists."""
    result = subprocess.run(("git", "rev-parse", "--verify", "--quiet", reference))
    return result.returncode == 0


def fetch_base_branch(remote_name: str, base_branch: str) -> None:
    """Fetch the base branch from the remote."""
    run_command(("git", "fetch", remote_name, base_branch))


def resolve_base_reference(remote_name: str, base_branch: str) -> str:
    """Resolve the base reference preferring the remote tracking branch."""
    remote_reference = f"{remote_name}/{base_branch}"
    if git_reference_exists(remote_reference):
        return remote_reference
    if git_reference_exists(base_branch):
        return base_branch
    raise SystemExit(f"Unable to resolve base branch reference for '{base_branch}'.")


def ensure_branch_divergence(base_reference: str) -> None:
    """Ensure the feature branch is ahead of and not behind the base."""
    behind_count = int(read_command_output(("git", "rev-list", "--count", f"HEAD..{base_reference}")))
    if behind_count > 0:
        raise SystemExit("Branch is behind base; rebase before preparing a pull request.")

    ahead_count = int(read_command_output(("git", "rev-list", "--count", f"{base_reference}..HEAD")))
    if ahead_count == 0:
        raise SystemExit("No commits found relative to base; nothing to submit.")


def collect_changed_files(base_reference: str) -> list[str]:
    """Collect changed files relative to the base reference."""
    output = read_command_output(("git", "diff", "--name-only", f"{base_reference}...HEAD"))
    return [line for line in output.splitlines() if line]


def is_documentation_path(file_path: str) -> bool:
    """Return True if the file path counts as documentation."""
    if file_path in DOCUMENTATION_ONLY_FILENAMES:
        return True
    return Path(file_path).parts[:1] == ("docs",)


def determine_documentation_only(changed_files: list[str]) -> bool:
    """Return True if changes are documentation-only."""
    return bool(changed_files) and all(is_documentation_path(path) for path in changed_files)


def build_default_title(base_reference: str, current_branch: str) -> str:
    """Derive a default pull request title."""
    commit_messages = read_command_output(("git", "log", "--format=%s", f"{base_reference}..HEAD"))
    for message in commit_messages.splitlines():
        return message
    return current_branch.replace("-", " ")


def build_documentation_only_body(changed_files: list[str], existing_body: str | None) -> str:
    """Build a documentation-only pull request body with required annotations."""
    lines: list[str] = []
    if existing_body:
        lines.append(existing_body.strip())
        lines.append("")
    lines.append("Docs-only: tests skipped")
    lines.append("")
    lines.append("Files changed:")
    for file_path in sorted(changed_files):
        lines.append(f"- {file_path}")
    return "\n".join(lines).strip() + "\n"


def run_validation(base_ref: str) -> None:
    """Run the canonical local validation."""
    result = run_command(
        (sys.executable, "scripts/dev/validate_local.py", "--base-ref", base_ref),
        check=False,
    )
    if result.returncode != 0:
        raise SystemExit(result.returncode)


def create_pull_request(
    arguments: argparse.Namespace,
    base_reference: str,
    changed_files: list[str],
    current_branch: str,
    documentation_only: bool,
) -> None:
    """Push the branch and create the pull request."""
    run_command(("git", "push", "--set-upstream", arguments.remote, "HEAD"))

    command = ["gh", "pr", "create", "--base", arguments.base, "--head", current_branch]
    if arguments.draft:
        command.append("--draft")

    temporary_body_path = None
    if documentation_only:
        title = arguments.title or build_default_title(base_reference, current_branch)
        command.extend(["--title", title])
        existing_body = None
        if arguments.body_file:
            existing_body = Path(arguments.body_file).read_text()
        elif arguments.body:
            existing_body = arguments.body
        body_text = build_documentation_only_body(changed_files, existing_body)
        with tempfile.NamedTemporaryFile("w", delete=False) as temporary_body:
            temporary_body.write(body_text)
            temporary_body_path = temporary_body.name
        command.extend(["--body-file", temporary_body_path])
    else:
        if arguments.title:
            command.extend(["--title", arguments.title])
        if arguments.body_file:
            command.extend(["--body-file", arguments.body_file])
        elif arguments.body is not None:
            command.extend(["--body", arguments.body])
        elif not arguments.title:
            command.append("--fill")
        elif arguments.body is None and arguments.body_file is None:
            command.extend(["--body", ""])

    try:
        run_command(tuple(command))
    finally:
        if documentation_only and temporary_body_path is not None:
            Path(temporary_body_path).unlink(missing_ok=True)


def main(argument_list: Sequence[str] | None = None) -> int:
    """Entry point for preparing a pull request."""
    arguments = parse_arguments(argument_list)

    ensure_project_root()
    ensure_executable_available("git")
    ensure_executable_available("gh")
    ensure_clean_worktree()
    ensure_base_branch_supported(arguments.base)
    ensure_no_open_pull_requests(arguments.base)

    if not arguments.no_fetch:
        fetch_base_branch(arguments.remote, arguments.base)

    base_reference = resolve_base_reference(arguments.remote, arguments.base)
    current_branch = get_current_branch()
    ensure_branch_allowed(current_branch, arguments.base)
    ensure_branch_divergence(base_reference)

    changed_files = collect_changed_files(base_reference)
    documentation_only = determine_documentation_only(changed_files)
    if not documentation_only or arguments.force_validation:
        run_validation(arguments.base)

    create_pull_request(arguments, base_reference, changed_files, current_branch, documentation_only)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
