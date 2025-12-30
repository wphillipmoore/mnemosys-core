"""
Environment enum tests.
"""

from mnemosys_core.config.environments import Environment


def test_environment_enum_values() -> None:
    """Test that all environment values are accessible."""
    assert Environment.DEVELOPMENT.value == "development"
    assert Environment.TEST.value == "test"
    assert Environment.PRODUCTION.value == "production"


def test_environment_enum_from_string() -> None:
    """Test creating Environment from string values."""
    assert Environment("development") == Environment.DEVELOPMENT
    assert Environment("test") == Environment.TEST
    assert Environment("production") == Environment.PRODUCTION


def test_environment_enum_members() -> None:
    """Test that all expected members exist."""
    members = list(Environment)
    assert len(members) == 3
    assert Environment.DEVELOPMENT in members
    assert Environment.TEST in members
    assert Environment.PRODUCTION in members
