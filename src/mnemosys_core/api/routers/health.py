"""
Health check endpoints.
"""

from typing import Any

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from ..dependencies import get_db

router = APIRouter()


@router.get("/")
def health_check() -> dict[str, str]:
    """Basic health check."""
    return {"status": "ok"}


@router.get("/db")
def database_health(db: Session = Depends(get_db)) -> dict[str, Any]:
    """Database connectivity check."""
    try:
        db.execute(text("SELECT 1"))
        return {"status": "ok", "database": "connected"}
    except Exception as e:
        return {"status": "error", "database": str(e)}
