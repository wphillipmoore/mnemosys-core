"""
Database engine and connection factory.

Provides explicit engine creation with no side effects at import time.
"""

from sqlalchemy import Engine, create_engine
from sqlalchemy.pool import StaticPool


def create_db_engine(
    database_url: str,
    echo: bool = False,
    pool_pre_ping: bool = True,
    poolclass: type | None = None,
) -> Engine:
    """
    Create a SQLAlchemy engine.

    Args:
        database_url: Database connection string
        echo: Whether to log SQL statements
        pool_pre_ping: Check connection health before use
        poolclass: Optional pool class override (e.g., NullPool for tests)

    Returns:
        Configured SQLAlchemy engine

    Example:
        >>> engine = create_db_engine("postgresql://user:pass@localhost/db")
        >>> engine = create_db_engine("sqlite:///:memory:")
    """
    # SQLite-specific configuration
    if database_url.startswith("sqlite"):
        # Use provided poolclass or default to StaticPool for in-memory databases
        pool = poolclass if poolclass is not None else StaticPool
        return create_engine(
            database_url,
            echo=echo,
            connect_args={"check_same_thread": False},
            poolclass=pool,
        )

    # PostgreSQL production configuration
    return create_engine(
        database_url,
        echo=echo,
        pool_pre_ping=pool_pre_ping,
        pool_size=5,
        max_overflow=10,
    )
