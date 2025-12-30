"""
Declarative base and metadata for SQLAlchemy models.

This module provides the base class for all ORM models and the metadata
object for schema introspection. No side effects occur at import time.
"""

from sqlalchemy import MetaData
from sqlalchemy.orm import DeclarativeBase

# Convention for constraint naming (PostgreSQL compatibility)
convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}

metadata = MetaData(naming_convention=convention)


class Base(DeclarativeBase):
    """Base class for all ORM models."""

    metadata = metadata
