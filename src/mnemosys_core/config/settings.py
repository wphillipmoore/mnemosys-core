"""
Configuration settings loader (no side effects at import).
"""

import os
from dataclasses import dataclass

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


def load_settings_from_env() -> Settings:
    """
    Load settings from environment variables.

    Environment Variables:
        MNEMOSYS_ENV: Environment name (development/test/production)
        DATABASE_URL: Database connection string
        MNEMOSYS_DB_SCHEMA: Database schema name
        DEBUG: Enable debug mode (true/false)
        LOG_SQL: Log SQL statements (true/false)

    Returns:
        Configured Settings object

    Example:
        >>> os.environ["MNEMOSYS_ENV"] = "test"
        >>> os.environ["DATABASE_URL"] = "sqlite:///:memory:"
        >>> settings = load_settings_from_env()
        >>> settings.environment
        <Environment.TEST: 'test'>
    """
    env_name = os.getenv("MNEMOSYS_ENV", "development")
    environment = Environment(env_name)

    # Default database URLs by environment
    default_db_urls = {
        Environment.DEVELOPMENT: "postgresql://localhost/mnemosys_dev",
        Environment.TEST: "sqlite:///:memory:",
        Environment.PRODUCTION: "postgresql://localhost/mnemosys_prod",
    }

    default_database_schemas = {
        Environment.DEVELOPMENT: "mnemosys",
        Environment.TEST: "mnemosys",
        Environment.PRODUCTION: "mnemosys",
    }

    database_url = os.getenv("DATABASE_URL", default_db_urls[environment])
    database_schema = os.getenv("MNEMOSYS_DB_SCHEMA", default_database_schemas[environment])
    debug = os.getenv("DEBUG", "false").lower() == "true"
    log_sql = os.getenv("LOG_SQL", "false").lower() == "true"

    return Settings(
        environment=environment,
        database_url=database_url,
        database_schema=database_schema,
        debug=debug,
        log_sql=log_sql,
    )
