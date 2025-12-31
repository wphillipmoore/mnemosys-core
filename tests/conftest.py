"""
Shared test fixtures.
"""

import gc
from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import Engine
from sqlalchemy.orm import Session as DBSession
from sqlalchemy.orm import close_all_sessions, sessionmaker

from mnemosys_core.api.app import create_app

# Import all models to register them with Base.metadata before create_all()
from mnemosys_core.db import models  # noqa: F401
from mnemosys_core.db.base import Base
from mnemosys_core.db.engine import create_db_engine


@pytest.fixture(scope="function")
def engine() -> Generator[Engine]:
    """
    Create in-memory SQLite engine for tests.

    Uses StaticPool to ensure all operations share the same in-memory database.
    Explicit cleanup prevents most connection warnings.
    """
    engine = create_db_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(engine)
    yield engine
    # Ensure all sessions are closed before disposal
    close_all_sessions()
    gc.collect()
    # Clean up
    Base.metadata.drop_all(engine)
    engine.dispose()
    gc.collect()


@pytest.fixture(scope="function")
def session_factory(engine: Engine) -> sessionmaker[DBSession]:
    """Create session factory."""
    return sessionmaker(bind=engine)


@pytest.fixture(scope="function")
def db_session(session_factory: sessionmaker[DBSession]) -> Generator[DBSession]:
    """Create database session for tests."""
    session = session_factory()
    yield session
    session.rollback()
    session.close()


@pytest.fixture(scope="function")
def client(engine: Engine) -> Generator[TestClient]:
    """Create FastAPI test client."""
    app = create_app(engine)
    with TestClient(app) as test_client:
        yield test_client
