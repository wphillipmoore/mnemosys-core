#!/usr/bin/env python3
"""
Validate that the local virtual environment is usable after moves or rebuilds.
"""

from __future__ import annotations

from pathlib import Path

REQUIRED_TOOLS: tuple[str, ...] = ("pip-audit", "ruff", "mypy", "pytest")


def ensure_project_root() -> None:
    """Fail fast if invoked outside the repository root."""
    if not Path("pyproject.toml").is_file():
        raise SystemExit("Run from the repository root (pyproject.toml missing).")


def read_shebang(script_path: Path) -> str | None:
    """Return the shebang line without '#!' or None if absent."""
    with script_path.open("rb") as handle:
        first_line = handle.readline().decode("utf-8", errors="replace").strip()
    if first_line.startswith("#!"):
        return first_line[2:].strip()
    return None


def is_binary(script_path: Path) -> bool:
    """Detect binary entrypoints by scanning for null bytes."""
    sample = script_path.read_bytes()[:1024]
    return b"\x00" in sample


def validate_shebang(script_path: Path, expected_python: Path) -> None:
    """Ensure entrypoint uses the current venv interpreter."""
    shebang = read_shebang(script_path)
    if shebang is None:
        if is_binary(script_path):
            return
        raise SystemExit(f"Missing shebang in {script_path}. Rebuild the venv.")

    interpreter = shebang.split()[0]
    if interpreter == "/usr/bin/env":
        return

    interpreter_path = Path(interpreter)
    if not interpreter_path.is_absolute():
        raise SystemExit(
            f"Unexpected shebang in {script_path}: {shebang}. Rebuild the venv."
        )

    if not interpreter_path.exists():
        raise SystemExit(
            f"Broken shebang in {script_path}: {interpreter_path} not found. Rebuild the venv."
        )

    if interpreter_path.resolve() != expected_python.resolve():
        raise SystemExit(
            "Venv entrypoint mismatch detected.\n"
            f"Expected: {expected_python}\n"
            f"Found:    {interpreter_path}\n"
            "Rebuild the venv."
        )


def validate_venv() -> None:
    venv_path = Path(".venv").resolve()
    if not venv_path.is_dir():
        raise SystemExit("Missing .venv. Rebuild with: python3 -m venv .venv")

    python_path = venv_path / "bin" / "python"
    if not python_path.exists():
        raise SystemExit(f"Missing venv interpreter: {python_path}")

    bin_dir = venv_path / "bin"
    for tool in REQUIRED_TOOLS:
        tool_path = bin_dir / tool
        if not tool_path.exists():
            raise SystemExit(
                f"Missing venv tool: {tool_path}. Run: poetry sync --with dev"
            )
        validate_shebang(tool_path, python_path)


def main() -> int:
    ensure_project_root()
    validate_venv()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
