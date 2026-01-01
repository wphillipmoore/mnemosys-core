"""
Custom column types for cross-database compatibility.

These types enable PostgreSQL features while maintaining SQLite compatibility
for testing.
"""

import enum
from typing import Any, cast

from sqlalchemy import JSON, String, TypeDecorator
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.dialects import postgresql
from sqlalchemy.engine import Dialect


class JSONEncodedList(TypeDecorator[list[str]]):
    """
    Array type that stores as PostgreSQL ARRAY in production
    and JSON in SQLite for testing.
    """

    impl = JSON
    cache_ok = True

    def load_dialect_impl(self, dialect: Dialect) -> Any:
        if dialect.name == "postgresql":
            return dialect.type_descriptor(postgresql.ARRAY(String))
        return dialect.type_descriptor(JSON())

    def process_bind_param(self, value: list[str] | None, dialect: Dialect) -> list[str] | None:
        return value

    def process_result_value(self, value: Any, dialect: Dialect) -> list[str] | None:
        if value is None:
            return None
        return cast("list[str]", value)


class JSONEncodedDict(TypeDecorator[dict[str, Any]]):
    """
    Dictionary type that stores as PostgreSQL JSONB in production
    and JSON in SQLite for testing.
    """

    impl = JSON
    cache_ok = True

    def load_dialect_impl(self, dialect: Dialect) -> Any:
        if dialect.name == "postgresql":
            return dialect.type_descriptor(postgresql.JSONB())
        return dialect.type_descriptor(JSON())

    def process_bind_param(self, value: dict[str, Any] | None, dialect: Dialect) -> dict[str, Any] | None:
        return value

    def process_result_value(self, value: Any, dialect: Dialect) -> dict[str, Any] | None:
        if value is None:
            return None
        return cast("dict[str, Any]", value)


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


class DatabaseEnumList(TypeDecorator[list[enum.Enum]]):
    """
    Enum list type that uses native PostgreSQL ENUM arrays in production
    and JSON in SQLite for testing.
    """

    impl = JSON
    cache_ok = True

    def __init__(self, enum_class: type[enum.Enum], **kwargs: Any) -> None:
        self.enum_class = enum_class
        super().__init__(**kwargs)

    def load_dialect_impl(self, dialect: Dialect) -> Any:
        if dialect.name == "postgresql":
            return dialect.type_descriptor(
                postgresql.ARRAY(SQLEnum(self.enum_class, name=self.enum_class.__name__))
            )
        return dialect.type_descriptor(JSON())

    def process_bind_param(
        self, value: list[enum.Enum] | list[str] | None, dialect: Dialect
    ) -> list[str] | None:
        if value is None:
            return None
        enum_values = [self._coerce_enum(item).value for item in value]
        return enum_values

    def process_result_value(self, value: Any, dialect: Dialect) -> list[enum.Enum] | None:
        if value is None:
            return None
        return [self._coerce_enum(item) for item in value]

    def _coerce_enum(self, value: enum.Enum | str) -> enum.Enum:
        if isinstance(value, self.enum_class):
            return value
        return self.enum_class(value)
