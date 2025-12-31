"""Tests for Instrument-Technique many-to-many relationship."""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from mnemosys_core.db.base import Base
from mnemosys_core.db.models.instrument import StringedInstrument
from mnemosys_core.db.models.technique import Technique


def test_instrument_can_support_multiple_techniques() -> None:
    """An instrument can support multiple techniques."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    guitar = StringedInstrument(
        name="Strat", string_count=6, scale_length=25.5
    )

    bending = Technique(name="string bending")
    tapping = Technique(name="tapping")
    alternate = Technique(name="alternate picking")

    guitar.techniques.extend([bending, tapping, alternate])

    session.add(guitar)
    session.commit()

    retrieved = session.query(StringedInstrument).filter_by(name="Strat").first()
    assert retrieved is not None
    assert len(retrieved.techniques) == 3
    assert any(t.name == "string bending" for t in retrieved.techniques)
    session.close()


def test_technique_can_be_supported_by_multiple_instruments() -> None:
    """A technique can be supported by multiple instruments."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    alternate = Technique(name="alternate picking")

    guitar = StringedInstrument(name="Guitar", string_count=6, scale_length=25.5)
    bass = StringedInstrument(name="Bass", string_count=4, scale_length=34.0)

    guitar.techniques.append(alternate)
    bass.techniques.append(alternate)

    session.add_all([guitar, bass])
    session.commit()

    retrieved_technique = (
        session.query(Technique).filter_by(name="alternate picking").first()
    )
    assert retrieved_technique is not None
    assert len(retrieved_technique.instruments) == 2
    session.close()
