"""
Settings loading tests.
"""

import pytest
from sqlalchemy.engine import URL

from mnemosys_core.config.environments import Environment
from mnemosys_core.config.settings import Settings, load_admin_settings_from_env, load_settings_from_env

DB_COMPONENT_ENV_VARS = (
    "MNEMOSYS_DB_DRIVERNAME",
    "MNEMOSYS_DB_USERNAME",
    "MNEMOSYS_DB_PASSWORD",
    "MNEMOSYS_DB_HOST",
    "MNEMOSYS_DB_PORT",
    "MNEMOSYS_DB_DATABASE",
)

DB_ADMIN_COMPONENT_ENV_VARS = (
    "MNEMOSYS_DB_ADMIN_DRIVERNAME",
    "MNEMOSYS_DB_ADMIN_USERNAME",
    "MNEMOSYS_DB_ADMIN_PASSWORD",
    "MNEMOSYS_DB_ADMIN_HOST",
    "MNEMOSYS_DB_ADMIN_PORT",
    "MNEMOSYS_DB_ADMIN_DATABASE",
)


@pytest.fixture(autouse=True)
def clear_db_component_env(monkeypatch: pytest.MonkeyPatch) -> None:
    """Clear component-based database environment variables for each test."""
    for variable_name in DB_COMPONENT_ENV_VARS:
        monkeypatch.delenv(variable_name, raising=False)
    for variable_name in DB_ADMIN_COMPONENT_ENV_VARS:
        monkeypatch.delenv(variable_name, raising=False)


def test_settings_dataclass_creation() -> None:
    """Test creating Settings directly."""
    settings = Settings(
        environment=Environment.TEST,
        database_url="sqlite:///:memory:",
        database_schema="mnemosys_test",
        debug=True,
        log_sql=True,
    )

    assert settings.environment == Environment.TEST
    assert settings.database_url == "sqlite:///:memory:"
    assert settings.database_schema == "mnemosys_test"
    assert settings.debug is True
    assert settings.log_sql is True


def test_settings_dataclass_defaults() -> None:
    """Test Settings default values."""
    settings = Settings(
        environment=Environment.DEVELOPMENT,
        database_url="postgresql://localhost/test",
        database_schema="mnemosys",
    )

    assert settings.debug is False
    assert settings.log_sql is False


def test_load_settings_from_env_development(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test loading development settings from environment."""
    monkeypatch.setenv("MNEMOSYS_ENV", "development")
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.delenv("MNEMOSYS_DB_SCHEMA", raising=False)
    monkeypatch.delenv("DEBUG", raising=False)
    monkeypatch.delenv("LOG_SQL", raising=False)

    settings = load_settings_from_env()

    assert settings.environment == Environment.DEVELOPMENT
    assert settings.database_url == "postgresql://localhost/mnemosys_dev"
    assert settings.database_schema == "mnemosys"
    assert settings.debug is False
    assert settings.log_sql is False


def test_load_settings_from_env_sandbox(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test loading sandbox settings from environment."""
    monkeypatch.setenv("MNEMOSYS_ENV", "sandbox")
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.delenv("MNEMOSYS_DB_SCHEMA", raising=False)

    settings = load_settings_from_env()

    assert settings.environment == Environment.SANDBOX
    assert settings.database_url == "postgresql://localhost/mnemosys_sandbox"
    assert settings.database_schema == "mnemosys"


def test_load_settings_from_env_test(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test loading test settings from environment."""
    monkeypatch.setenv("MNEMOSYS_ENV", "test")
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.delenv("MNEMOSYS_DB_SCHEMA", raising=False)

    settings = load_settings_from_env()

    assert settings.environment == Environment.TEST
    assert settings.database_url == "sqlite:///:memory:"
    assert settings.database_schema == "mnemosys"


def test_load_settings_from_env_production(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test loading production settings from environment."""
    monkeypatch.setenv("MNEMOSYS_ENV", "production")
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.delenv("MNEMOSYS_DB_SCHEMA", raising=False)

    settings = load_settings_from_env()

    assert settings.environment == Environment.PRODUCTION
    assert settings.database_url == "postgresql://localhost/mnemosys_prod"
    assert settings.database_schema == "mnemosys"


def test_load_settings_from_env_custom_database_url(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test custom DATABASE_URL override."""
    monkeypatch.setenv("MNEMOSYS_ENV", "development")
    monkeypatch.setenv("DATABASE_URL", "postgresql://custom:5432/customdb")
    monkeypatch.setenv("MNEMOSYS_DB_HOST", "ignored.example.com")
    monkeypatch.delenv("MNEMOSYS_DB_SCHEMA", raising=False)

    settings = load_settings_from_env()

    assert settings.database_url == "postgresql://custom:5432/customdb"
    assert settings.database_schema == "mnemosys"


def test_load_settings_from_env_debug_true(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test DEBUG=true environment variable."""
    monkeypatch.setenv("MNEMOSYS_ENV", "development")
    monkeypatch.setenv("DEBUG", "true")

    settings = load_settings_from_env()

    assert settings.debug is True


def test_load_settings_from_env_debug_false(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test DEBUG=false environment variable."""
    monkeypatch.setenv("MNEMOSYS_ENV", "development")
    monkeypatch.setenv("DEBUG", "false")

    settings = load_settings_from_env()

    assert settings.debug is False


def test_load_settings_from_env_log_sql_true(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test LOG_SQL=true environment variable."""
    monkeypatch.setenv("MNEMOSYS_ENV", "development")
    monkeypatch.setenv("LOG_SQL", "true")

    settings = load_settings_from_env()

    assert settings.log_sql is True


def test_load_settings_from_env_default_no_env_var(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test default environment when MNEMOSYS_ENV is not set."""
    monkeypatch.delenv("MNEMOSYS_ENV", raising=False)
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.delenv("MNEMOSYS_DB_SCHEMA", raising=False)

    settings = load_settings_from_env()

    assert settings.environment == Environment.DEVELOPMENT
    assert settings.database_url == "postgresql://localhost/mnemosys_dev"
    assert settings.database_schema == "mnemosys"


def test_load_settings_from_env_all_custom(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test all settings customized via environment."""
    monkeypatch.setenv("MNEMOSYS_ENV", "test")
    monkeypatch.setenv("DATABASE_URL", "sqlite:///test.db")
    monkeypatch.setenv("MNEMOSYS_DB_SCHEMA", "mnemosys_custom")
    monkeypatch.setenv("DEBUG", "true")
    monkeypatch.setenv("LOG_SQL", "true")

    settings = load_settings_from_env()

    assert settings.environment == Environment.TEST
    assert settings.database_url == "sqlite:///test.db"
    assert settings.database_schema == "mnemosys_custom"
    assert settings.debug is True
    assert settings.log_sql is True


def test_load_settings_from_env_custom_schema(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test custom MNEMOSYS_DB_SCHEMA override."""
    monkeypatch.setenv("MNEMOSYS_ENV", "development")
    monkeypatch.setenv("MNEMOSYS_DB_SCHEMA", "mnemosys_dev_feature")

    settings = load_settings_from_env()

    assert settings.database_schema == "mnemosys_dev_feature"


def test_load_settings_from_env_db_components(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test building database URL from MNEMOSYS_DB_* components."""
    monkeypatch.setenv("MNEMOSYS_ENV", "development")
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.setenv("MNEMOSYS_DB_DRIVERNAME", "postgresql")
    monkeypatch.setenv("MNEMOSYS_DB_USERNAME", "mnemosys_user")
    monkeypatch.setenv("MNEMOSYS_DB_PASSWORD", "secret")
    monkeypatch.setenv("MNEMOSYS_DB_HOST", "db.local")
    monkeypatch.setenv("MNEMOSYS_DB_PORT", "5433")
    monkeypatch.setenv("MNEMOSYS_DB_DATABASE", "mnemosys_dev")

    settings = load_settings_from_env()

    expected_url = str(
        URL.create(
            drivername="postgresql",
            username="mnemosys_user",
            password="secret",
            host="db.local",
            port=5433,
            database="mnemosys_dev",
        )
    )
    assert settings.database_url == expected_url


def test_load_settings_from_env_invalid_port(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test invalid MNEMOSYS_DB_PORT raises a ValueError."""
    monkeypatch.setenv("MNEMOSYS_ENV", "development")
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.setenv("MNEMOSYS_DB_PORT", "not-a-number")

    with pytest.raises(ValueError, match="MNEMOSYS_DB_PORT must be an integer"):
        load_settings_from_env()


def test_load_admin_settings_from_env_db_components(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test building admin database URL from MNEMOSYS_DB_ADMIN_* components."""
    monkeypatch.setenv("MNEMOSYS_ENV", "development")
    monkeypatch.setenv("MNEMOSYS_DB_ADMIN_DRIVERNAME", "postgresql")
    monkeypatch.setenv("MNEMOSYS_DB_ADMIN_USERNAME", "mnemosys_admin")
    monkeypatch.setenv("MNEMOSYS_DB_ADMIN_PASSWORD", "secret")
    monkeypatch.setenv("MNEMOSYS_DB_ADMIN_HOST", "db.local")
    monkeypatch.setenv("MNEMOSYS_DB_ADMIN_PORT", "5433")
    monkeypatch.setenv("MNEMOSYS_DB_ADMIN_DATABASE", "mnemosys_sandbox")

    settings = load_admin_settings_from_env()

    expected_url = str(
        URL.create(
            drivername="postgresql",
            username="mnemosys_admin",
            password="secret",
            host="db.local",
            port=5433,
            database="mnemosys_sandbox",
        )
    )
    assert settings.database_url == expected_url


def test_load_admin_settings_from_env_fallback(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test admin settings fall back to MNEMOSYS_DB_* values."""
    monkeypatch.setenv("MNEMOSYS_ENV", "development")
    monkeypatch.setenv("MNEMOSYS_DB_DRIVERNAME", "postgresql")
    monkeypatch.setenv("MNEMOSYS_DB_USERNAME", "mnemosys_user")
    monkeypatch.setenv("MNEMOSYS_DB_PASSWORD", "secret")
    monkeypatch.setenv("MNEMOSYS_DB_HOST", "db.local")
    monkeypatch.setenv("MNEMOSYS_DB_PORT", "5433")
    monkeypatch.setenv("MNEMOSYS_DB_DATABASE", "mnemosys_sandbox")

    settings = load_admin_settings_from_env()

    expected_url = str(
        URL.create(
            drivername="postgresql",
            username="mnemosys_user",
            password="secret",
            host="db.local",
            port=5433,
            database="mnemosys_sandbox",
        )
    )
    assert settings.database_url == expected_url
