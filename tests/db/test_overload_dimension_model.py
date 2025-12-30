"""Tests for OverloadDimension entity."""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from mnemosys_core.db.base import Base
from mnemosys_core.db.models.overload_dimensions import OverloadDimension


def test_overload_dimension_creation() -> None:
    """OverloadDimension should be creatable with name and description."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    dimension = OverloadDimension(
        name="tempo",
        description="Speed in beats per minute (BPM)",
    )
    session.add(dimension)
    session.commit()

    retrieved = session.query(OverloadDimension).filter_by(name="tempo").first()
    assert retrieved is not None
    assert retrieved.name == "tempo"
    assert "beats per minute" in retrieved.description
    session.close()


def test_overload_dimension_unique_name() -> None:
    """OverloadDimension names should be unique."""
    from sqlalchemy.exc import IntegrityError

    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    dimension1 = OverloadDimension(name="duration")
    session.add(dimension1)
    session.commit()

    dimension2 = OverloadDimension(name="duration")
    session.add(dimension2)

    try:
        session.commit()
        raise AssertionError("Should have raised IntegrityError")
    except IntegrityError:
        session.rollback()
    finally:
        session.close()


def test_overload_dimension_repr() -> None:
    """OverloadDimension __repr__ should be informative."""
    dimension = OverloadDimension(name="complexity")
    assert "complexity" in repr(dimension)
