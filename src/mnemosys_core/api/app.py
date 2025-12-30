"""
FastAPI application factory.
"""

from fastapi import FastAPI
from sqlalchemy import Engine

from .dependencies import configure_dependencies


def create_app(engine: Engine) -> FastAPI:
    """
    Create and configure FastAPI application.

    Args:
        engine: SQLAlchemy engine for database operations

    Returns:
        Configured FastAPI application

    Example:
        >>> from mnemosys_core.db.engine import create_db_engine
        >>> engine = create_db_engine("sqlite:///:memory:")
        >>> app = create_app(engine)
    """
    app = FastAPI(
        title="Mnemosys Core API",
        description="MNEMOSYS practice tracking API",
        version="0.1.0",
    )

    # Configure dependency injection
    configure_dependencies(app, engine)

    # Register routers
    from .routers import exercises, health, instruments, sessions

    app.include_router(health.router, prefix="/health", tags=["health"])
    app.include_router(instruments.router, prefix="/api/v1/instruments", tags=["instruments"])
    app.include_router(exercises.router, prefix="/api/v1/exercises", tags=["exercises"])
    app.include_router(sessions.router, prefix="/api/v1/sessions", tags=["sessions"])

    return app
