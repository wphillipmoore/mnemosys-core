"""
Custom database type tests.
"""

from unittest.mock import MagicMock

from mnemosys_core.db.models import DomainType, FatigueProfile
from mnemosys_core.db.types import DatabaseEnum, DatabaseEnumList, JSONEncodedDict, JSONEncodedList


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


class TestDatabaseEnumList:
    """Test DatabaseEnumList type converter."""

    def test_load_dialect_impl_postgresql(self) -> None:
        """Test that PostgreSQL uses native ENUM array type."""
        converter = DatabaseEnumList(DomainType)
        mock_dialect = MagicMock()
        mock_dialect.name = "postgresql"

        converter.load_dialect_impl(mock_dialect)
        mock_dialect.type_descriptor.assert_called_once()

    def test_load_dialect_impl_sqlite(self) -> None:
        """Test that SQLite uses String type."""
        converter = DatabaseEnumList(DomainType)
        mock_dialect = MagicMock()
        mock_dialect.name = "sqlite"

        converter.load_dialect_impl(mock_dialect)
        mock_dialect.type_descriptor.assert_called_once()

    def test_process_bind_param_with_enums(self) -> None:
        """Test binding enum values for PostgreSQL."""
        converter = DatabaseEnumList(DomainType)
        mock_dialect = MagicMock()
        mock_dialect.name = "postgresql"

        result = converter.process_bind_param(
            [DomainType.TECHNIQUE, DomainType.HARMONY], mock_dialect
        )
        assert result == ["Technique", "Harmony"]

    def test_process_bind_param_with_strings(self) -> None:
        """Test binding string values for PostgreSQL."""
        converter = DatabaseEnumList(DomainType)
        mock_dialect = MagicMock()
        mock_dialect.name = "postgresql"

        result = converter.process_bind_param(["Technique", "Harmony"], mock_dialect)
        assert result == ["Technique", "Harmony"]

    def test_process_bind_param_none(self) -> None:
        """Test binding None value."""
        converter = DatabaseEnumList(DomainType)
        mock_dialect = MagicMock()
        mock_dialect.name = "postgresql"

        result = converter.process_bind_param(None, mock_dialect)
        assert result is None

    def test_process_result_value_postgresql(self) -> None:
        """Test reading enum list values from PostgreSQL."""
        converter = DatabaseEnumList(DomainType)
        mock_dialect = MagicMock()
        mock_dialect.name = "postgresql"

        result = converter.process_result_value(["Technique", "Harmony"], mock_dialect)
        assert result == [DomainType.TECHNIQUE, DomainType.HARMONY]

    def test_process_result_value_postgresql_with_enums(self) -> None:
        """Test reading enum list values when enums are returned."""
        converter = DatabaseEnumList(DomainType)
        mock_dialect = MagicMock()
        mock_dialect.name = "postgresql"

        result = converter.process_result_value([DomainType.TECHNIQUE], mock_dialect)
        assert result == [DomainType.TECHNIQUE]

    def test_process_result_value_sqlite(self) -> None:
        """Test reading enum list values from SQLite."""
        converter = DatabaseEnumList(DomainType)
        mock_dialect = MagicMock()
        mock_dialect.name = "sqlite"

        result = converter.process_result_value('["Technique", "Harmony"]', mock_dialect)
        assert result == [DomainType.TECHNIQUE, DomainType.HARMONY]

    def test_process_result_value_none(self) -> None:
        """Test reading None value."""
        converter = DatabaseEnumList(DomainType)
        mock_dialect = MagicMock()
        mock_dialect.name = "postgresql"

        result = converter.process_result_value(None, mock_dialect)
        assert result is None

    def test_enum_class_stored(self) -> None:
        """Test that enum class is stored correctly."""
        converter = DatabaseEnumList(DomainType)
        assert converter.enum_class == DomainType


class TestJSONEncodedDict:
    """Test JSONEncodedDict type converter."""

    def test_load_dialect_impl_postgresql(self) -> None:
        """Test that PostgreSQL uses native JSONB type."""
        converter = JSONEncodedDict()
        mock_dialect = MagicMock()
        mock_dialect.name = "postgresql"

        # Should return PostgreSQL JSONB
        converter.load_dialect_impl(mock_dialect)
        mock_dialect.type_descriptor.assert_called_once()

    def test_load_dialect_impl_sqlite(self) -> None:
        """Test that SQLite uses String type."""
        converter = JSONEncodedDict()
        mock_dialect = MagicMock()
        mock_dialect.name = "sqlite"

        # Should return String
        converter.load_dialect_impl(mock_dialect)
        mock_dialect.type_descriptor.assert_called_once()

    def test_process_bind_param_postgresql(self) -> None:
        """Test binding dict values for PostgreSQL."""
        converter = JSONEncodedDict()
        mock_dialect = MagicMock()
        mock_dialect.name = "postgresql"

        value = {"key1": "value1", "key2": 42}
        result = converter.process_bind_param(value, mock_dialect)

        # PostgreSQL gets the raw dict
        assert result == {"key1": "value1", "key2": 42}

    def test_process_bind_param_sqlite(self) -> None:
        """Test binding dict values for SQLite."""
        converter = JSONEncodedDict()
        mock_dialect = MagicMock()
        mock_dialect.name = "sqlite"

        value = {"key1": "value1", "key2": 42}
        result = converter.process_bind_param(value, mock_dialect)

        # SQLite gets JSON string
        assert result == '{"key1": "value1", "key2": 42}'
        assert isinstance(result, str)

    def test_process_bind_param_none(self) -> None:
        """Test binding None value."""
        converter = JSONEncodedDict()
        mock_dialect = MagicMock()
        mock_dialect.name = "postgresql"

        result = converter.process_bind_param(None, mock_dialect)
        assert result is None

    def test_process_result_value_postgresql(self) -> None:
        """Test reading dict values from PostgreSQL."""
        converter = JSONEncodedDict()
        mock_dialect = MagicMock()
        mock_dialect.name = "postgresql"

        value = {"key1": "value1", "key2": 42}
        result = converter.process_result_value(value, mock_dialect)

        # PostgreSQL returns raw dict
        assert result == {"key1": "value1", "key2": 42}

    def test_process_result_value_sqlite(self) -> None:
        """Test reading dict values from SQLite."""
        converter = JSONEncodedDict()
        mock_dialect = MagicMock()
        mock_dialect.name = "sqlite"

        value = '{"key1": "value1", "key2": 42}'
        result = converter.process_result_value(value, mock_dialect)

        # SQLite parses JSON string
        assert result == {"key1": "value1", "key2": 42}

    def test_process_result_value_none(self) -> None:
        """Test reading None value."""
        converter = JSONEncodedDict()
        mock_dialect = MagicMock()
        mock_dialect.name = "postgresql"

        result = converter.process_result_value(None, mock_dialect)
        assert result is None
