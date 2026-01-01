"""
Dependency injection tests.
"""

import pytest
from fastapi import FastAPI, Request

from mnemosys_core.api.dependencies import get_db


def test_get_db_without_configuration() -> None:
    """Test that get_db raises error when not configured."""
    app = FastAPI()
    scope = {"type": "http", "app": app, "headers": []}
    request = Request(scope)

    with pytest.raises(RuntimeError, match="Dependencies not configured"):
        generator = get_db(request)
        next(generator)
