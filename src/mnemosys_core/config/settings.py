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


def load_settings_from_env() -> Settings:
    """
    Load settings from environment variables.

    Environment Variables:
        MNEMOSYS_ENV: Environment name (development/test/production)
        DATABASE_URL: Database connection string
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

    Example:
        >>> os.environ["MNEMOSYS_ENV"] = "test"
        >>> os.environ["DATABASE_URL"] = "sqlite:///:memory:"
        >>> settings = load_settings_from_env()
        >>> settings.environment
        <Environment.TEST: 'test'>
    """
    env_name = os.getenv("MNEMOSYS_ENV", "development")
    environment = Environment(env_name)

    default_db_components = {
        Environment.DEVELOPMENT: {
            "drivername": "postgresql",
            "username": None,
            "password": None,
            "host": "localhost",
            "port": None,
            "database": "mnemosys_dev",
        },
        Environment.TEST: {
            "drivername": "sqlite",
            "username": None,
            "password": None,
            "host": None,
            "port": None,
            "database": ":memory:",
        },
        Environment.PRODUCTION: {
            "drivername": "postgresql",
            "username": None,
            "password": None,
            "host": "localhost",
            "port": None,
            "database": "mnemosys_prod",
        },
    }

    default_database_schemas = {
        Environment.DEVELOPMENT: "mnemosys",
        Environment.TEST: "mnemosys",
        Environment.PRODUCTION: "mnemosys",
    }

    database_url = os.getenv("DATABASE_URL")
    if database_url is None:
        defaults = default_db_components[environment]
        port_value = os.getenv("MNEMOSYS_DB_PORT")
        port = defaults["port"]
        if port_value is not None:
            try:
                port = int(port_value)
            except ValueError as exc:
                raise ValueError("MNEMOSYS_DB_PORT must be an integer.") from exc

        database_url = str(
            URL.create(
                drivername=os.getenv("MNEMOSYS_DB_DRIVERNAME", defaults["drivername"]),
                username=os.getenv("MNEMOSYS_DB_USERNAME", defaults["username"]),
                password=os.getenv("MNEMOSYS_DB_PASSWORD", defaults["password"]),
                host=os.getenv("MNEMOSYS_DB_HOST", defaults["host"]),
                port=port,
                database=os.getenv("MNEMOSYS_DB_DATABASE", defaults["database"]),
            )
        )
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
