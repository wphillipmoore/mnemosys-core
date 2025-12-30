"""
Dependency injection tests.
"""

import pytest

from mnemosys_core.api.dependencies import get_db


def test_get_db_without_configuration() -> None:
    """Test that get_db raises error when not configured."""
    # Reset the global session factory to None
    import mnemosys_core.api.dependencies as deps

    original_factory = deps._session_factory
    deps._session_factory = None

    try:
        # Attempt to get a database session
        with pytest.raises(RuntimeError, match="Dependencies not configured"):
            generator = get_db()
            next(generator)
    finally:
        # Restore original factory
        deps._session_factory = original_factory
