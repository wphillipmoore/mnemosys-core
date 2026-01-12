"""
Health check endpoints.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from fastapi import APIRouter, Depends
from sqlalchemy import text

from ..dependencies import get_db

router = APIRouter()

if TYPE_CHECKING:
    from sqlalchemy.orm import Session as DBSession


@router.get("/")
def health_check() -> dict[str, str]:
    """Basic health check."""
    return {"status": "ok"}


@router.get("/db")
def database_health(db_session: DBSession = Depends(get_db)) -> dict[str, Any]:
    """Database connectivity check."""
    try:
        db_session.execute(text("SELECT 1"))
        return {"status": "ok", "database": "connected"}
    except Exception as exception:
        return {"status": "error", "database": str(exception)}
