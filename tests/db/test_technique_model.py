"""Tests for Technique entity."""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from mnemosys_core.db.base import Base
from mnemosys_core.db.models.techniques import Technique


def test_technique_creation() -> None:
    """Technique should be creatable with name and description."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    technique = Technique(
        name="string skipping",
        description="Skipping over one or more strings during picking",
    )
    session.add(technique)
    session.commit()

    retrieved = session.query(Technique).filter_by(name="string skipping").first()
    assert retrieved is not None
    assert retrieved.name == "string skipping"
    assert "Skipping over" in retrieved.description
    session.close()


def test_technique_unique_name() -> None:
    """Technique names should be unique."""
    from sqlalchemy.exc import IntegrityError

    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    technique1 = Technique(name="alternate picking")
    session.add(technique1)
    session.commit()

    technique2 = Technique(name="alternate picking")
    session.add(technique2)

    try:
        session.commit()
        raise AssertionError("Should have raised IntegrityError")
    except IntegrityError:
        session.rollback()
    finally:
        session.close()


def test_technique_repr() -> None:
    """Technique __repr__ should be informative."""
    technique = Technique(name="palm muting")
    assert "palm muting" in repr(technique)
