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
from sqlalchemy.engine import Dialect


class JSONEncodedList(TypeDecorator[list[str]]):
    """
    Array type that stores as PostgreSQL ARRAY in production
    and JSON string in SQLite for testing.
    """

    impl = String
    cache_ok = True

    def load_dialect_impl(self, dialect: Dialect) -> Any:
        if dialect.name == "postgresql":
            return dialect.type_descriptor(postgresql.ARRAY(String))
        else:
            return dialect.type_descriptor(String())

    def process_bind_param(self, value: list[str] | None, dialect: Dialect) -> list[str] | str | None:
        if value is None:
            return None
        if dialect.name == "postgresql":
            return value
        else:
            return json.dumps(value)

    def process_result_value(self, value: Any, dialect: Dialect) -> list[str] | None:
        if value is None:
            return None
        if dialect.name == "postgresql":
            return value  # type: ignore[no-any-return]
        else:
            return json.loads(value)  # type: ignore[no-any-return]


class DatabaseEnum(TypeDecorator[enum.Enum]):
    """
    Enum type that uses native PostgreSQL ENUM in production
    and VARCHAR in SQLite for testing.
    """

    impl = String
    cache_ok = True

    def __init__(self, enum_class: type[enum.Enum], **kwargs: Any) -> None:
        self.enum_class = enum_class
        super().__init__(**kwargs)

    def load_dialect_impl(self, dialect: Dialect) -> Any:
        if dialect.name == "postgresql":
            return dialect.type_descriptor(SQLEnum(self.enum_class, name=self.enum_class.__name__))
        else:
            return dialect.type_descriptor(String(50))

    def process_bind_param(self, value: enum.Enum | str | None, dialect: Dialect) -> str | None:
        if value is None:
            return None
        if isinstance(value, self.enum_class):
            return value.value  # type: ignore[no-any-return]
        return value  # type: ignore[return-value]

    def process_result_value(self, value: Any, dialect: Dialect) -> enum.Enum | None:
        if value is None:
            return None
        return self.enum_class(value)
