"""
Dependency injection configuration for FastAPI.
"""

from collections.abc import Generator

from fastapi import FastAPI
from sqlalchemy import Engine
from sqlalchemy.orm import Session as DBSession
from sqlalchemy.orm import sessionmaker

from ..db.session import create_session_factory, get_session_dependency

# Global storage for session factory (set by create_app)
_session_factory: sessionmaker[DBSession] | None = None


def configure_dependencies(app: FastAPI, engine: Engine) -> None:
    """
    Configure application dependencies.

    Args:
        app: FastAPI application
        engine: SQLAlchemy engine
    """
    global _session_factory
    _session_factory = create_session_factory(engine)


def get_db() -> Generator[DBSession]:
    """
    FastAPI dependency for database sessions.

    Yields:
        Database session

    Example:
        @router.get("/instruments")
        def list_instruments(db_session: DBSession = Depends(get_db)):
            return db_session.query(Instrument).all()
    """
    if _session_factory is None:
        raise RuntimeError("Dependencies not configured. Call configure_dependencies first.")

    get_session = get_session_dependency(_session_factory)
    yield from get_session()
