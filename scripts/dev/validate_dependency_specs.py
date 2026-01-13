#!/usr/bin/env python3
"""
Validate dependency specification rules for pyproject.toml.
"""

from __future__ import annotations

import re
from pathlib import Path

import tomllib


ANCHOR_PREFIX = "# Anchor:"
DEPENDENCY_RECORDS_DIR = Path("docs/dependencies")
PYPROJECT_PATH = Path("pyproject.toml")


class DependencySpecError(Exception):
    """Raised when dependency specification validation fails."""


def ensure_project_root() -> None:
    """Fail fast if invoked outside the repository root."""
    if not PYPROJECT_PATH.is_file():
        raise SystemExit("Run from the repository root (pyproject.toml missing).")


def load_pyproject() -> dict[str, object]:
    with PYPROJECT_PATH.open("rb") as handle:
        return tomllib.load(handle)


def parse_version(version_text: str) -> tuple[int, int | None, int | None] | None:
    if not re.fullmatch(r"\d+(?:\.\d+){0,2}", version_text):
        return None
    parts = [int(part) for part in version_text.split(".")]
    major = parts[0]
    minor = parts[1] if len(parts) > 1 else None
    patch = parts[2] if len(parts) > 2 else None
    return major, minor, patch


def parse_range_spec(spec_text: str) -> tuple[tuple[int, int | None, int | None], tuple[int, int | None, int | None]] | None:
    parts = [part.strip() for part in spec_text.split(",") if part.strip()]
    if len(parts) != 2:
        return None

    lower_part = next((part for part in parts if part.startswith(">=")), None)
    upper_part = next((part for part in parts if part.startswith("<")), None)
    if lower_part is None or upper_part is None:
        return None

    if lower_part.startswith(">") and not lower_part.startswith(">="):
        return None
    if upper_part.startswith("<="):
        return None

    lower_version = parse_version(lower_part[2:].strip())
    upper_version = parse_version(upper_part[1:].strip())
    if lower_version is None or upper_version is None:
        return None

    return lower_version, upper_version


def is_standard_range(spec_text: str) -> bool:
    parsed = parse_range_spec(spec_text)
    if parsed is None:
        return False
    lower_version, upper_version = parsed
    lower_major, lower_minor, lower_patch = lower_version
    upper_major, upper_minor, upper_patch = upper_version

    if lower_major == 0:
        if upper_major != 0 or lower_minor is None or upper_minor is None:
            return False
        if upper_minor != lower_minor + 1:
            return False
        if lower_patch not in (None, 0) or upper_patch not in (None, 0):
            return False
        return True

    if upper_major != lower_major + 1:
        return False
    if lower_minor not in (None, 0) or lower_patch not in (None, 0):
        return False
    if upper_minor not in (None, 0) or upper_patch not in (None, 0):
        return False
    return True


def collect_dependency_lines(lines: list[str]) -> dict[tuple[str, str], int]:
    current_section: str | None = None
    dependency_lines: dict[tuple[str, str], int] = {}

    section_pattern = re.compile(r"^\[(.+)]\s*$")
    dependency_pattern = re.compile(r"^([A-Za-z0-9_.-]+)\s*=")

    for index, line in enumerate(lines):
        section_match = section_pattern.match(line.strip())
        if section_match:
            current_section = section_match.group(1)
            continue

        if current_section is None:
            continue

        if current_section == "tool.poetry.dependencies":
            dependency_match = dependency_pattern.match(line)
            if dependency_match:
                dependency_lines[(current_section, dependency_match.group(1))] = index
            continue

        if current_section.startswith("tool.poetry.group.") and current_section.endswith(".dependencies"):
            dependency_match = dependency_pattern.match(line)
            if dependency_match:
                dependency_lines[(current_section, dependency_match.group(1))] = index
            continue

    return dependency_lines


def anchor_comment_for(lines: list[str], line_index: int) -> str | None:
    if line_index == 0:
        return None
    comment_line = lines[line_index - 1].strip()
    if not comment_line.startswith(ANCHOR_PREFIX):
        return None
    return comment_line


def dependency_record_path(dependency_name: str) -> Path:
    return DEPENDENCY_RECORDS_DIR / f"{dependency_name}.md"


def validate_dependency_specs() -> None:
    pyproject = load_pyproject()
    tool_section = pyproject.get("tool")
    if not isinstance(tool_section, dict):
        raise DependencySpecError("Missing [tool] section in pyproject.toml.")

    poetry_section = tool_section.get("poetry")
    if not isinstance(poetry_section, dict):
        raise DependencySpecError("Missing [tool.poetry] section in pyproject.toml.")

    dependencies_section = poetry_section.get("dependencies")
    if not isinstance(dependencies_section, dict):
        raise DependencySpecError("Missing [tool.poetry.dependencies] section in pyproject.toml.")

    group_section = poetry_section.get("group", {})
    if not isinstance(group_section, dict):
        raise DependencySpecError("Invalid [tool.poetry.group] section in pyproject.toml.")

    lines = PYPROJECT_PATH.read_text().splitlines()
    dependency_lines = collect_dependency_lines(lines)
    errors: list[str] = []

    def validate_section(section_name: str, dependencies: dict[str, object]) -> None:
        for dependency_name, dependency_spec in sorted(dependencies.items()):
            if dependency_name == "python":
                continue

            spec_text: str | None = None
            if isinstance(dependency_spec, str):
                spec_text = dependency_spec.strip()
            elif isinstance(dependency_spec, dict):
                version_value = dependency_spec.get("version")
                if isinstance(version_value, str):
                    spec_text = version_value.strip()
            else:
                errors.append(f"{section_name}:{dependency_name} has unsupported spec format.")
                continue

            if not spec_text:
                errors.append(f"{section_name}:{dependency_name} has no version specifier.")
                continue

            if "*" in spec_text:
                errors.append(f"{section_name}:{dependency_name} uses '*' which is forbidden.")
                continue

            if is_standard_range(spec_text):
                continue

            line_index = dependency_lines.get((section_name, dependency_name))
            if line_index is None:
                errors.append(f"{section_name}:{dependency_name} missing in pyproject.toml lines.")
                continue

            anchor_comment = anchor_comment_for(lines, line_index)
            record_path = dependency_record_path(dependency_name)

            if anchor_comment is None:
                errors.append(
                    f"{section_name}:{dependency_name} requires anchor comment '{ANCHOR_PREFIX}' with record reference."
                )
            elif f"docs/dependencies/{dependency_name}.md" not in anchor_comment:
                errors.append(
                    f"{section_name}:{dependency_name} anchor comment must reference docs/dependencies/{dependency_name}.md."
                )

            if not record_path.is_file():
                errors.append(
                    f"{section_name}:{dependency_name} missing dependency record at {record_path}."
                )

    validate_section("tool.poetry.dependencies", dependencies_section)

    for group_name, group_value in group_section.items():
        if not isinstance(group_value, dict):
            errors.append(f"tool.poetry.group.{group_name} must be a table.")
            continue
        group_dependencies = group_value.get("dependencies")
        if not isinstance(group_dependencies, dict):
            continue
        section_name = f"tool.poetry.group.{group_name}.dependencies"
        validate_section(section_name, group_dependencies)

    if errors:
        message = "Dependency specification validation failed:\n" + "\n".join(f"- {error}" for error in errors)
        raise DependencySpecError(message)


def main() -> int:
    ensure_project_root()
    try:
        validate_dependency_specs()
    except DependencySpecError as error:
        raise SystemExit(str(error)) from error
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
