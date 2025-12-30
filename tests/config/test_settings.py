"""
Settings loading tests.
"""

import pytest

from mnemosys_core.config.environments import Environment
from mnemosys_core.config.settings import Settings, load_settings_from_env


def test_settings_dataclass_creation() -> None:
    """Test creating Settings directly."""
    settings = Settings(
        environment=Environment.TEST,
        database_url="sqlite:///:memory:",
        debug=True,
        log_sql=True,
    )

    assert settings.environment == Environment.TEST
    assert settings.database_url == "sqlite:///:memory:"
    assert settings.debug is True
    assert settings.log_sql is True


def test_settings_dataclass_defaults() -> None:
    """Test Settings default values."""
    settings = Settings(environment=Environment.DEVELOPMENT, database_url="postgresql://localhost/test")

    assert settings.debug is False
    assert settings.log_sql is False


def test_load_settings_from_env_development(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test loading development settings from environment."""
    monkeypatch.setenv("MNEMOSYS_ENV", "development")
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.delenv("DEBUG", raising=False)
    monkeypatch.delenv("LOG_SQL", raising=False)

    settings = load_settings_from_env()

    assert settings.environment == Environment.DEVELOPMENT
    assert settings.database_url == "postgresql://localhost/mnemosys_dev"
    assert settings.debug is False
    assert settings.log_sql is False


def test_load_settings_from_env_test(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test loading test settings from environment."""
    monkeypatch.setenv("MNEMOSYS_ENV", "test")
    monkeypatch.delenv("DATABASE_URL", raising=False)

    settings = load_settings_from_env()

    assert settings.environment == Environment.TEST
    assert settings.database_url == "sqlite:///:memory:"


def test_load_settings_from_env_production(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test loading production settings from environment."""
    monkeypatch.setenv("MNEMOSYS_ENV", "production")
    monkeypatch.delenv("DATABASE_URL", raising=False)

    settings = load_settings_from_env()

    assert settings.environment == Environment.PRODUCTION
    assert settings.database_url == "postgresql://localhost/mnemosys_prod"


def test_load_settings_from_env_custom_database_url(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test custom DATABASE_URL override."""
    monkeypatch.setenv("MNEMOSYS_ENV", "development")
    monkeypatch.setenv("DATABASE_URL", "postgresql://custom:5432/customdb")

    settings = load_settings_from_env()

    assert settings.database_url == "postgresql://custom:5432/customdb"


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

    settings = load_settings_from_env()

    assert settings.environment == Environment.DEVELOPMENT
    assert settings.database_url == "postgresql://localhost/mnemosys_dev"


def test_load_settings_from_env_all_custom(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test all settings customized via environment."""
    monkeypatch.setenv("MNEMOSYS_ENV", "test")
    monkeypatch.setenv("DATABASE_URL", "sqlite:///test.db")
    monkeypatch.setenv("DEBUG", "true")
    monkeypatch.setenv("LOG_SQL", "true")

    settings = load_settings_from_env()

    assert settings.environment == Environment.TEST
    assert settings.database_url == "sqlite:///test.db"
    assert settings.debug is True
    assert settings.log_sql is True
