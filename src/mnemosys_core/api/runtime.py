"""
Runtime entrypoints for REST API deployment.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from mnemosys_core.config.settings import load_settings_from_env
from mnemosys_core.db.engine import create_db_engine

from .app import create_app

if TYPE_CHECKING:
    from fastapi import FastAPI


def create_application() -> FastAPI:
    """
    Create a FastAPI application using environment settings.

    Returns:
        Configured FastAPI application
    """
    settings = load_settings_from_env()
    engine = create_db_engine(
        settings.database_url,
        echo=settings.log_sql,
        database_schema=settings.database_schema,
    )
    return create_app(engine)
