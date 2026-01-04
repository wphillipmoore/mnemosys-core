"""
Alembic migration environment.
"""

from logging.config import fileConfig

from alembic import context
from alembic.autogenerate import rewriter
from alembic.operations import ops
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


def should_include_object(object_, name, type_, reflected, compare_to):
    """Exclude Alembic's version table from autogenerate comparisons."""
    return not (type_ == "table" and name == "alembic_version")


def should_include_name(name, type_, parent_names):
    """Limit autogenerate to the configured schema when present."""
    schema_name = get_schema_name()
    if not schema_name:
        return True
    if type_ == "schema":
        return name in (None, schema_name)
    return not (parent_names and parent_names.get("schema_name") not in (None, schema_name))


def build_schema_rewriter(schema_name: str) -> rewriter.Rewriter:
    """Build a rewriter that strips a fixed schema from generated operations."""
    schema_rewriter = rewriter.Rewriter()
    schema_attributes = ("schema", "table_schema", "source_schema", "referent_schema")

    @schema_rewriter.rewrites(ops.MigrateOperation)
    def strip_schema(context, revision, op):
        for attribute_name in schema_attributes:
            if getattr(op, attribute_name, None) == schema_name:
                setattr(op, attribute_name, None)
        return op

    return schema_rewriter


def process_revision_directives(context, revision, directives):
    """Rewrite autogenerate directives to avoid hard-coded schemas."""
    if not directives:
        return

    schema_name = get_schema_name()
    if not schema_name:
        return
    schema_rewriter = build_schema_rewriter(schema_name)
    schema_rewriter(context, revision, directives)


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
        include_schemas=bool(schema_name),
        include_name=should_include_name,
        include_object=should_include_object,
        process_revision_directives=process_revision_directives,
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
            include_schemas=bool(schema_name),
            include_name=should_include_name,
            include_object=should_include_object,
            process_revision_directives=process_revision_directives,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
