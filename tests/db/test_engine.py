"""
Database engine tests.
"""

from importlib.util import find_spec

import pytest
from sqlalchemy import Engine

from mnemosys_core.db.engine import create_db_engine


def is_psycopg2_available() -> bool:
    """Return True when the psycopg2 driver is installed."""
    return find_spec("psycopg2") is not None


def test_create_db_engine_sqlite() -> None:
    """Test creating SQLite engine."""
    engine = create_db_engine("sqlite:///:memory:", echo=False)

    assert engine is not None
    assert isinstance(engine, Engine)
    assert str(engine.url).startswith("sqlite")


def test_create_db_engine_sqlite_with_echo() -> None:
    """Test creating SQLite engine with echo enabled."""
    engine = create_db_engine("sqlite:///:memory:", echo=True)

    assert engine is not None
    assert engine.echo is True


def test_create_db_engine_postgresql() -> None:
    """Test creating PostgreSQL engine configuration."""
    # We can't actually connect to PostgreSQL in tests, but we can verify the engine is created
    if is_psycopg2_available():
        engine = create_db_engine("postgresql://localhost/testdb", echo=False, pool_pre_ping=True)

        assert engine is not None
        assert isinstance(engine, Engine)
        assert str(engine.url).startswith("postgresql")
    else:
        with pytest.raises(ModuleNotFoundError, match="psycopg2"):
            create_db_engine("postgresql://localhost/testdb", echo=False, pool_pre_ping=True)


def test_create_db_engine_postgresql_settings() -> None:
    """Test PostgreSQL engine has correct pool settings."""
    if is_psycopg2_available():
        engine = create_db_engine("postgresql://localhost/testdb", echo=False)

        # Verify pool settings are applied
        assert engine.pool is not None
        assert engine.echo is False
    else:
        with pytest.raises(ModuleNotFoundError, match="psycopg2"):
            create_db_engine("postgresql://localhost/testdb", echo=False)
