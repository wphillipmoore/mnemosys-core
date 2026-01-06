"""
Dependency injection configuration for FastAPI.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from fastapi import Request  # noqa: TC002

from ..db.session import create_session_factory, get_session_dependency

if TYPE_CHECKING:
    from collections.abc import Generator

    from fastapi import FastAPI
    from sqlalchemy import Engine
    from sqlalchemy.orm import Session as DBSession


def configure_dependencies(app: FastAPI, engine: Engine) -> None:
    """
    Configure application dependencies.

    Args:
        app: FastAPI application
        engine: SQLAlchemy engine
    """
    app.state.session_factory = create_session_factory(engine)


def get_db(request: Request) -> Generator[DBSession]:
    """
    FastAPI dependency for database sessions.

    Yields:
        Database session

    Example:
        @router.get("/instruments")
        def list_instruments(db_session: DBSession = Depends(get_db)):
            return db_session.query(Instrument).all()
    """
    session_factory = getattr(request.app.state, "session_factory", None)
    if session_factory is None:
        raise RuntimeError("Dependencies not configured. Call configure_dependencies first.")

    get_session = get_session_dependency(session_factory)
    yield from get_session()
