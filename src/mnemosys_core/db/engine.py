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
) -> Engine:
    """
    Create a SQLAlchemy engine.

    Args:
        database_url: Database connection string
        echo: Whether to log SQL statements
        pool_pre_ping: Check connection health before use

    Returns:
        Configured SQLAlchemy engine

    Example:
        >>> engine = create_db_engine("postgresql://user:pass@localhost/db")
        >>> engine = create_db_engine("sqlite:///:memory:")
    """
    # SQLite-specific configuration for testing
    if database_url.startswith("sqlite"):
        return create_engine(
            database_url,
            echo=echo,
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,  # Required for in-memory SQLite
        )

    # PostgreSQL production configuration
    return create_engine(
        database_url,
        echo=echo,
        pool_pre_ping=pool_pre_ping,
        pool_size=5,
        max_overflow=10,
    )
