"""
Configuration settings loader (no side effects at import).
"""

import os
from dataclasses import dataclass

from sqlalchemy.engine import URL

from .environments import Environment


@dataclass(frozen=True)
class Settings:
    """
    Application configuration.

    Attributes:
        environment: Current environment
        database_url: Database connection string
        database_schema: Database schema name
        debug: Enable debug mode
        log_sql: Log SQL statements
    """

    environment: Environment
    database_url: str
    database_schema: str
    debug: bool = False
    log_sql: bool = False


@dataclass(frozen=True)
class DatabaseComponents:
    """Structured database URL components."""

    drivername: str
    username: str | None
    password: str | None
    host: str | None
    port: int | None
    database: str


def _default_db_components() -> dict[Environment, DatabaseComponents]:
    """Return default database URL components for each environment."""
    return {
        Environment.SANDBOX: DatabaseComponents(
            drivername="postgresql",
            username=None,
            password=None,
            host="localhost",
            port=None,
            database="mnemosys_sandbox",
        ),
        Environment.DEVELOPMENT: DatabaseComponents(
            drivername="postgresql",
            username=None,
            password=None,
            host="localhost",
            port=None,
            database="mnemosys_dev",
        ),
        Environment.TEST: DatabaseComponents(
            drivername="sqlite",
            username=None,
            password=None,
            host=None,
            port=None,
            database=":memory:",
        ),
        Environment.PRODUCTION: DatabaseComponents(
            drivername="postgresql",
            username=None,
            password=None,
            host="localhost",
            port=None,
            database="mnemosys_prod",
        ),
    }


def _default_database_schemas() -> dict[Environment, str]:
    """Return default schema names per environment."""
    return {
        Environment.SANDBOX: "mnemosys",
        Environment.DEVELOPMENT: "mnemosys",
        Environment.TEST: "mnemosys",
        Environment.PRODUCTION: "mnemosys",
    }


def _get_env_value(prefix: str, name: str, fallback_prefix: str | None) -> str | None:
    """Return a value from the primary prefix, falling back when needed."""
    value = os.getenv(f"{prefix}{name}")
    if value is None and fallback_prefix is not None:
        value = os.getenv(f"{fallback_prefix}{name}")
    return value


def _parse_port(port_value: str | None, default: int | None, port_name: str) -> int | None:
    """Parse a port value from the environment."""
    if port_value is None:
        return default
    try:
        return int(port_value)
    except ValueError as exc:
        raise ValueError(f"{port_name} must be an integer.") from exc


def _build_database_url(
    environment: Environment,
    prefix: str,
    fallback_prefix: str | None = None,
    url_override_env_var: str | None = None,
) -> str:
    """Build a database URL from environment variables."""
    if url_override_env_var is not None:
        override_value = os.getenv(url_override_env_var)
        if override_value is not None:
            return override_value

    defaults = _default_db_components()[environment]
    port_value = _get_env_value(prefix, "PORT", fallback_prefix)
    port = _parse_port(port_value, defaults.port, f"{prefix}PORT")

    return str(
        URL.create(
            drivername=_get_env_value(prefix, "DRIVERNAME", fallback_prefix) or defaults.drivername,
            username=_get_env_value(prefix, "USERNAME", fallback_prefix) or defaults.username,
            password=_get_env_value(prefix, "PASSWORD", fallback_prefix) or defaults.password,
            host=_get_env_value(prefix, "HOST", fallback_prefix) or defaults.host,
            port=port,
            database=_get_env_value(prefix, "DATABASE", fallback_prefix) or defaults.database,
        )
    )


def _load_settings_from_env(prefix: str, fallback_prefix: str | None, url_override_env_var: str | None) -> Settings:
    """Load settings using the specified environment variable prefix."""
    env_name = os.getenv("MNEMOSYS_ENV", "development")
    environment = Environment(env_name)

    database_url = _build_database_url(environment, prefix, fallback_prefix, url_override_env_var)
    database_schema = os.getenv("MNEMOSYS_DB_SCHEMA", _default_database_schemas()[environment])
    debug = os.getenv("DEBUG", "false").lower() == "true"
    log_sql = os.getenv("LOG_SQL", "false").lower() == "true"

    return Settings(
        environment=environment,
        database_url=database_url,
        database_schema=database_schema,
        debug=debug,
        log_sql=log_sql,
    )


def load_settings_from_env() -> Settings:
    """
    Load application settings from environment variables.

    Environment Variables:
        MNEMOSYS_ENV: Environment name (sandbox/development/test/production)
        DATABASE_URL: Database connection string (override)
        MNEMOSYS_DB_DRIVERNAME: SQLAlchemy driver name (e.g., postgresql, sqlite)
        MNEMOSYS_DB_USERNAME: Database username
        MNEMOSYS_DB_PASSWORD: Database password
        MNEMOSYS_DB_HOST: Database host
        MNEMOSYS_DB_PORT: Database port
        MNEMOSYS_DB_DATABASE: Database name
        MNEMOSYS_DB_SCHEMA: Database schema name
        DEBUG: Enable debug mode (true/false)
        LOG_SQL: Log SQL statements (true/false)

    Returns:
        Configured Settings object
    """
    return _load_settings_from_env("MNEMOSYS_DB_", None, "DATABASE_URL")


def load_admin_settings_from_env() -> Settings:
    """
    Load admin settings for migrations from environment variables.

    Environment Variables:
        MNEMOSYS_ENV: Environment name (sandbox/development/test/production)
        MNEMOSYS_DB_ADMIN_DRIVERNAME: SQLAlchemy driver name (e.g., postgresql, sqlite)
        MNEMOSYS_DB_ADMIN_USERNAME: Database admin username
        MNEMOSYS_DB_ADMIN_PASSWORD: Database admin password
        MNEMOSYS_DB_ADMIN_HOST: Database host
        MNEMOSYS_DB_ADMIN_PORT: Database port
        MNEMOSYS_DB_ADMIN_DATABASE: Database name
        MNEMOSYS_DB_SCHEMA: Database schema name
        DEBUG: Enable debug mode (true/false)
        LOG_SQL: Log SQL statements (true/false)

    Notes:
        Falls back to MNEMOSYS_DB_* when admin variables are not set.
    """
    return _load_settings_from_env("MNEMOSYS_DB_ADMIN_", "MNEMOSYS_DB_", None)
