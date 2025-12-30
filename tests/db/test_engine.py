"""
Database engine tests.
"""

from sqlalchemy import Engine

from mnemosys_core.db.engine import create_db_engine


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
    engine = create_db_engine("postgresql://localhost/testdb", echo=False, pool_pre_ping=True)

    assert engine is not None
    assert isinstance(engine, Engine)
    assert str(engine.url).startswith("postgresql")


def test_create_db_engine_postgresql_settings() -> None:
    """Test PostgreSQL engine has correct pool settings."""
    engine = create_db_engine("postgresql://localhost/testdb", echo=False)

    # Verify pool settings are applied
    assert engine.pool is not None
    assert engine.echo is False
