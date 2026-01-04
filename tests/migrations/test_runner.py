"""
Tests for Alembic migration runner.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import pytest

from mnemosys_core.migrations import runner


@dataclass
class CommandSequence:
    """Callable sequence of Alembic command results."""

    results: list[runner.AlembicCommandResult]

    def __call__(self, command_arguments: list[str], alembic_configuration_path: str | None) -> runner.AlembicCommandResult:
        if not self.results:
            raise AssertionError("No more command results available.")
        return self.results.pop(0)


def make_result(return_code: int, standard_output: str = "", standard_error: str = "") -> runner.AlembicCommandResult:
    """Create a synthetic AlembicCommandResult."""
    return runner.AlembicCommandResult(
        command=["alembic"],
        return_code=return_code,
        standard_output=standard_output,
        standard_error=standard_error,
        duration_seconds=0.01,
    )


def test_run_upgrade_check_success(monkeypatch: pytest.MonkeyPatch) -> None:
    """Upgrade succeeds when alembic check passes."""
    command_sequence = CommandSequence([make_result(0)])
    monkeypatch.setattr(runner, "run_alembic_command", command_sequence)

    assert runner.run_upgrade(None) == 0


def test_run_upgrade_upgrade_success(monkeypatch: pytest.MonkeyPatch) -> None:
    """Upgrade succeeds after applying alembic upgrade."""
    command_sequence = CommandSequence([make_result(1), make_result(0)])
    monkeypatch.setattr(runner, "run_alembic_command", command_sequence)

    assert runner.run_upgrade(None) == 0


def test_run_upgrade_concurrent_success(monkeypatch: pytest.MonkeyPatch) -> None:
    """Upgrade tolerates concurrent migrations when recheck succeeds."""
    command_sequence = CommandSequence([make_result(1), make_result(1), make_result(0)])
    monkeypatch.setattr(runner, "run_alembic_command", command_sequence)

    assert runner.run_upgrade(None) == 0


def test_run_upgrade_failure(monkeypatch: pytest.MonkeyPatch) -> None:
    """Upgrade fails when alembic remains out of sync."""
    command_sequence = CommandSequence([make_result(1), make_result(1), make_result(1)])
    monkeypatch.setattr(runner, "run_alembic_command", command_sequence)

    assert runner.run_upgrade(None) == 1


def test_run_downgrade_verification_success(monkeypatch: pytest.MonkeyPatch) -> None:
    """Downgrade succeeds when current revision matches target."""
    command_sequence = CommandSequence(
        [
            make_result(0),
            make_result(0, standard_output="Rev: abcdef12"),
        ]
    )
    monkeypatch.setattr(runner, "run_alembic_command", command_sequence)

    assert runner.run_downgrade(None, "abcdef12") == 0


def test_run_downgrade_verification_failure(monkeypatch: pytest.MonkeyPatch) -> None:
    """Downgrade fails when current revision does not match target."""
    command_sequence = CommandSequence(
        [
            make_result(0),
            make_result(0, standard_output="Rev: deadbeef"),
        ]
    )
    monkeypatch.setattr(runner, "run_alembic_command", command_sequence)

    assert runner.run_downgrade(None, "abcdef12") == 1


def test_run_downgrade_base_skips_verification(monkeypatch: pytest.MonkeyPatch) -> None:
    """Downgrade to base skips verification."""
    command_sequence = CommandSequence([make_result(0)])
    monkeypatch.setattr(runner, "run_alembic_command", command_sequence)

    assert runner.run_downgrade(None, "base") == 0


def test_main_missing_required_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    """Main returns config error when env vars are missing."""
    monkeypatch.delenv("MNEMOSYS_ENV", raising=False)

    assert runner.main(["upgrade"]) == 2


def test_main_invalid_environment_value(monkeypatch: pytest.MonkeyPatch) -> None:
    """Main returns config error for invalid MNEMOSYS_ENV values."""
    monkeypatch.setenv("MNEMOSYS_ENV", "invalid")

    assert runner.main(["upgrade"]) == 2


def test_main_upgrade_path(monkeypatch: pytest.MonkeyPatch) -> None:
    """Main dispatches to upgrade when action is upgrade."""
    monkeypatch.setenv("MNEMOSYS_ENV", "development")
    monkeypatch.setenv("MNEMOSYS_DB_SCHEMA", "mnemosys")
    monkeypatch.setattr(runner, "validate_alembic_command_available", lambda: True)
    monkeypatch.setattr(runner, "run_upgrade", lambda _: 0)

    assert runner.main(["upgrade"]) == 0


def test_main_downgrade_requires_target(monkeypatch: pytest.MonkeyPatch) -> None:
    """Main requires MNEMOSYS_DOWNGRADE_TARGET for downgrade."""
    monkeypatch.setenv("MNEMOSYS_ENV", "development")
    monkeypatch.setenv("MNEMOSYS_DB_SCHEMA", "mnemosys")
    monkeypatch.delenv("MNEMOSYS_DOWNGRADE_TARGET", raising=False)
    monkeypatch.setattr(runner, "validate_alembic_command_available", lambda: True)

    assert runner.main(["downgrade"]) == 2


def test_main_downgrade_path(monkeypatch: pytest.MonkeyPatch) -> None:
    """Main dispatches to downgrade when action is downgrade."""
    monkeypatch.setenv("MNEMOSYS_ENV", "development")
    monkeypatch.setenv("MNEMOSYS_DB_SCHEMA", "mnemosys")
    monkeypatch.setenv("MNEMOSYS_DOWNGRADE_TARGET", "abcdef12")
    monkeypatch.setattr(runner, "validate_alembic_command_available", lambda: True)
    monkeypatch.setattr(runner, "run_downgrade", lambda _configuration_path, _target: 0)

    assert runner.main(["downgrade"]) == 0
