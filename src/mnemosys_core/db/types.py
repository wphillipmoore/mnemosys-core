"""
Custom column types for cross-database compatibility.

These types enable PostgreSQL features while maintaining SQLite compatibility
for testing.
"""

import enum
import json
from typing import Any

from sqlalchemy import Enum as SQLEnum
from sqlalchemy import String, TypeDecorator
from sqlalchemy.dialects import postgresql


class JSONEncodedList(TypeDecorator):
    """
    Array type that stores as PostgreSQL ARRAY in production
    and JSON string in SQLite for testing.
    """

    impl = String
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == "postgresql":
            return dialect.type_descriptor(postgresql.ARRAY(String))
        else:
            return dialect.type_descriptor(String)

    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        if dialect.name == "postgresql":
            return value
        else:
            return json.dumps(value)

    def process_result_value(self, value, dialect):
        if value is None:
            return None
        if dialect.name == "postgresql":
            return value
        else:
            return json.loads(value)


class DatabaseEnum(TypeDecorator):
    """
    Enum type that uses native PostgreSQL ENUM in production
    and VARCHAR in SQLite for testing.
    """

    impl = String
    cache_ok = True

    def __init__(self, enum_class: type[enum.Enum], **kwargs):
        self.enum_class = enum_class
        super().__init__(**kwargs)

    def load_dialect_impl(self, dialect):
        if dialect.name == "postgresql":
            return dialect.type_descriptor(SQLEnum(self.enum_class, name=self.enum_class.__name__))
        else:
            return dialect.type_descriptor(String(50))

    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        if isinstance(value, self.enum_class):
            return value.value
        return value

    def process_result_value(self, value, dialect):
        if value is None:
            return None
        return self.enum_class(value)
