"""
Alembic migration environment.
"""

from logging.config import fileConfig

from alembic import context
from sqlalchemy import pool

# Import metadata and models
from mnemosys_core.config.settings import load_admin_settings_from_env
from mnemosys_core.db import models  # noqa: F401
from mnemosys_core.db.base import Base
from mnemosys_core.db.engine import create_db_engine

# Alembic Config object
config = context.config

# Interpret the config file for Python logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Metadata for autogenerate
target_metadata = Base.metadata


def get_url():
    """Get database URL from settings."""
    settings = load_admin_settings_from_env()
    return settings.database_url


def get_schema_name():
    """Get database schema name from settings."""
    settings = load_admin_settings_from_env()
    if settings.database_url.startswith("sqlite"):
        return None
    return settings.database_schema


def run_migrations_offline():
    """Run migrations in 'offline' mode."""
    url = get_url()
    schema_name = get_schema_name()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        version_table_schema=schema_name,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    """Run migrations in 'online' mode."""
    database_url = get_url()
    schema_name = get_schema_name()
    connectable = create_db_engine(
        database_url,
        poolclass=pool.NullPool,
        database_schema=schema_name,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            version_table_schema=schema_name,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
