"""
Custom database type tests.
"""

from unittest.mock import MagicMock

from mnemosys_core.db.models import FatigueProfile
from mnemosys_core.db.types import DatabaseEnum, JSONEncodedList


class TestJSONEncodedList:
    """Test JSONEncodedList type converter."""

    def test_load_dialect_impl_postgresql(self) -> None:
        """Test that PostgreSQL uses native ARRAY type."""
        converter = JSONEncodedList()
        mock_dialect = MagicMock()
        mock_dialect.name = "postgresql"

        # Should return PostgreSQL ARRAY
        converter.load_dialect_impl(mock_dialect)
        # Just verify it calls type_descriptor
        mock_dialect.type_descriptor.assert_called_once()

    def test_load_dialect_impl_sqlite(self) -> None:
        """Test that SQLite uses String type."""
        converter = JSONEncodedList()
        mock_dialect = MagicMock()
        mock_dialect.name = "sqlite"

        # Should return String
        converter.load_dialect_impl(mock_dialect)
        mock_dialect.type_descriptor.assert_called_once()

    def test_process_bind_param_postgresql(self) -> None:
        """Test binding list values for PostgreSQL."""
        converter = JSONEncodedList()
        mock_dialect = MagicMock()
        mock_dialect.name = "postgresql"

        value = ["item1", "item2", "item3"]
        result = converter.process_bind_param(value, mock_dialect)

        # PostgreSQL gets the raw list
        assert result == ["item1", "item2", "item3"]

    def test_process_bind_param_sqlite(self) -> None:
        """Test binding list values for SQLite."""
        converter = JSONEncodedList()
        mock_dialect = MagicMock()
        mock_dialect.name = "sqlite"

        value = ["item1", "item2", "item3"]
        result = converter.process_bind_param(value, mock_dialect)

        # SQLite gets JSON string
        assert result == '["item1", "item2", "item3"]'
        assert isinstance(result, str)

    def test_process_bind_param_none(self) -> None:
        """Test binding None value."""
        converter = JSONEncodedList()
        mock_dialect = MagicMock()
        mock_dialect.name = "postgresql"

        result = converter.process_bind_param(None, mock_dialect)
        assert result is None

    def test_process_result_value_postgresql(self) -> None:
        """Test reading list values from PostgreSQL."""
        converter = JSONEncodedList()
        mock_dialect = MagicMock()
        mock_dialect.name = "postgresql"

        value = ["item1", "item2"]
        result = converter.process_result_value(value, mock_dialect)

        # PostgreSQL returns raw list
        assert result == ["item1", "item2"]

    def test_process_result_value_sqlite(self) -> None:
        """Test reading list values from SQLite."""
        converter = JSONEncodedList()
        mock_dialect = MagicMock()
        mock_dialect.name = "sqlite"

        value = '["item1", "item2"]'
        result = converter.process_result_value(value, mock_dialect)

        # SQLite parses JSON string
        assert result == ["item1", "item2"]

    def test_process_result_value_none(self) -> None:
        """Test reading None value."""
        converter = JSONEncodedList()
        mock_dialect = MagicMock()
        mock_dialect.name = "postgresql"

        result = converter.process_result_value(None, mock_dialect)
        assert result is None


class TestDatabaseEnum:
    """Test DatabaseEnum type converter."""

    def test_load_dialect_impl_postgresql(self) -> None:
        """Test that PostgreSQL uses native ENUM type."""
        converter = DatabaseEnum(FatigueProfile)
        mock_dialect = MagicMock()
        mock_dialect.name = "postgresql"

        # Should return PostgreSQL ENUM
        converter.load_dialect_impl(mock_dialect)
        mock_dialect.type_descriptor.assert_called_once()

    def test_load_dialect_impl_sqlite(self) -> None:
        """Test that SQLite uses String type."""
        converter = DatabaseEnum(FatigueProfile)
        mock_dialect = MagicMock()
        mock_dialect.name = "sqlite"

        # Should return String
        converter.load_dialect_impl(mock_dialect)
        mock_dialect.type_descriptor.assert_called_once()

    def test_process_bind_param_with_enum(self) -> None:
        """Test binding enum values."""
        converter = DatabaseEnum(FatigueProfile)
        mock_dialect = MagicMock()
        mock_dialect.name = "postgresql"

        result = converter.process_bind_param(FatigueProfile.F1, mock_dialect)
        assert result == "F1"

    def test_process_bind_param_with_string(self) -> None:
        """Test binding string values (for compatibility)."""
        converter = DatabaseEnum(FatigueProfile)
        mock_dialect = MagicMock()
        mock_dialect.name = "postgresql"

        result = converter.process_bind_param("F2", mock_dialect)
        assert result == "F2"

    def test_process_bind_param_none(self) -> None:
        """Test binding None value."""
        converter = DatabaseEnum(FatigueProfile)
        mock_dialect = MagicMock()
        mock_dialect.name = "postgresql"

        result = converter.process_bind_param(None, mock_dialect)
        assert result is None

    def test_process_result_value_with_string(self) -> None:
        """Test reading enum values from database."""
        converter = DatabaseEnum(FatigueProfile)
        mock_dialect = MagicMock()
        mock_dialect.name = "postgresql"

        result = converter.process_result_value("F0", mock_dialect)
        assert result == FatigueProfile.F0
        assert isinstance(result, FatigueProfile)

    def test_process_result_value_none(self) -> None:
        """Test reading None value."""
        converter = DatabaseEnum(FatigueProfile)
        mock_dialect = MagicMock()
        mock_dialect.name = "postgresql"

        result = converter.process_result_value(None, mock_dialect)
        assert result is None

    def test_enum_class_stored(self) -> None:
        """Test that enum class is stored correctly."""
        converter = DatabaseEnum(FatigueProfile)
        assert converter.enum_class == FatigueProfile
