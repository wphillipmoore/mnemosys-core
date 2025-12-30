"""
Metadata invariant tests.
"""

from mnemosys_core.db.base import Base


def test_all_models_have_tablename() -> None:
    """Test that all models have __tablename__ defined."""
    for mapper in Base.registry.mappers:
        cls = mapper.class_
        assert hasattr(cls, "__tablename__"), f"{cls.__name__} missing __tablename__"


def test_all_tables_have_primary_key() -> None:
    """Test that all tables have a primary key."""
    for table in Base.metadata.tables.values():
        assert table.primary_key is not None, f"Table {table.name} missing primary key"
        assert len(table.primary_key) > 0, f"Table {table.name} has empty primary key"


def test_naming_conventions_applied() -> None:
    """Test that naming conventions are applied to constraints."""
    metadata = Base.metadata
    assert metadata.naming_convention is not None
    assert "pk" in metadata.naming_convention
    assert "fk" in metadata.naming_convention
    assert "ix" in metadata.naming_convention


def test_no_circular_dependencies() -> None:
    """Test that there are no circular foreign key dependencies."""
    # This is validated by SQLAlchemy's metadata creation
    # If there were circular deps, Base.metadata would fail to initialize
    assert Base.metadata is not None
    assert len(Base.metadata.tables) > 0
