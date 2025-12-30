"""
Database session management for dependency injection.

Provides session factory and FastAPI dependency functions.
"""

from typing import Generator

from sqlalchemy import Engine
from sqlalchemy.orm import Session, sessionmaker


def create_session_factory(engine: Engine) -> sessionmaker:
    """
    Create a session factory bound to an engine.

    Args:
        engine: SQLAlchemy engine

    Returns:
        Configured sessionmaker

    Example:
        >>> engine = create_db_engine("sqlite:///:memory:")
        >>> SessionFactory = create_session_factory(engine)
        >>> with SessionFactory() as session:
        ...     session.query(Exercise).all()
    """
    return sessionmaker(
        bind=engine,
        autocommit=False,
        autoflush=False,
        expire_on_commit=False,
    )


def get_session_dependency(session_factory: sessionmaker):
    """
    Create a FastAPI dependency that yields database sessions.

    Args:
        session_factory: Configured sessionmaker

    Returns:
        Dependency function for FastAPI

    Example:
        >>> app = create_app(engine)
        >>> # FastAPI will call this for each request
    """

    def get_session() -> Generator[Session, None, None]:
        session = session_factory()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    return get_session
