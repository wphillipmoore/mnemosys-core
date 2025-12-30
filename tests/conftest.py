"""
Shared test fixtures.
"""

from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import Engine
from sqlalchemy.orm import Session, sessionmaker

from mnemosys_core.api.app import create_app
from mnemosys_core.db.base import Base
from mnemosys_core.db.engine import create_db_engine


@pytest.fixture(scope="function")
def engine() -> Generator[Engine]:
    """Create in-memory SQLite engine for tests."""
    engine = create_db_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(engine)
    yield engine
    engine.dispose()


@pytest.fixture(scope="function")
def session_factory(engine: Engine) -> sessionmaker[Session]:
    """Create session factory."""
    return sessionmaker(bind=engine)


@pytest.fixture(scope="function")
def db_session(session_factory: sessionmaker[Session]) -> Generator[Session]:
    """Create database session for tests."""
    session = session_factory()
    yield session
    session.rollback()
    session.close()


@pytest.fixture(scope="function")
def client(engine: Engine) -> TestClient:
    """Create FastAPI test client."""
    app = create_app(engine)
    return TestClient(app)
