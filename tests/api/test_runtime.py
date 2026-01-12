from __future__ import annotations

from typing import TYPE_CHECKING

from fastapi import FastAPI

from mnemosys_core.api.runtime import create_application

if TYPE_CHECKING:
    import pytest


def test_create_application_configures_dependencies(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("MNEMOSYS_ENV", "test")
    app = create_application()

    assert isinstance(app, FastAPI)
    assert getattr(app.state, "session_factory", None) is not None
