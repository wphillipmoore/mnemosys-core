"""Tests for polymorphic Tuning hierarchy."""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from mnemosys_core.db.base import Base
from mnemosys_core.db.models.tuning import (
    KeyboardInstrumentTuning,
    PercussionInstrumentTuning,
    StringedInstrumentTuning,
    Tuning,
    WindInstrumentTuning,
)


def test_base_tuning_has_discriminator() -> None:
    """Base Tuning should have tuning_type discriminator."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    tuning = StringedInstrumentTuning(
        name="Standard", pitch_sequence=["E2", "A2", "D3", "G3", "B3", "E4"]
    )
    session.add(tuning)
    session.commit()

    assert tuning.tuning_type == "stringed"
    session.close()


def test_stringed_instrument_tuning_creation() -> None:
    """StringedInstrumentTuning should store pitch sequences."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    standard = StringedInstrumentTuning(
        name="Standard", pitch_sequence=["E2", "A2", "D3", "G3", "B3", "E4"]
    )
    drop_d = StringedInstrumentTuning(
        name="Drop D", pitch_sequence=["D2", "A2", "D3", "G3", "B3", "E4"]
    )

    session.add_all([standard, drop_d])
    session.commit()

    retrieved = session.query(StringedInstrumentTuning).filter_by(name="Standard").first()
    assert retrieved is not None
    assert retrieved.pitch_sequence == ["E2", "A2", "D3", "G3", "B3", "E4"]
    assert retrieved.tuning_type == "stringed"
    session.close()


def test_placeholder_tunings_exist() -> None:
    """Placeholder tuning classes should exist."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    keyboard = KeyboardInstrumentTuning(name="A440")
    wind = WindInstrumentTuning(name="A440")
    percussion = PercussionInstrumentTuning(name="Standard")

    session.add_all([keyboard, wind, percussion])
    session.commit()

    assert session.query(KeyboardInstrumentTuning).count() == 1
    assert session.query(WindInstrumentTuning).count() == 1
    assert session.query(PercussionInstrumentTuning).count() == 1
    session.close()


def test_polymorphic_tuning_query() -> None:
    """Querying base Tuning should return specific subclass instances."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    stringed = StringedInstrumentTuning(
        name="Standard", pitch_sequence=["E2", "A2", "D3", "G3"]
    )
    keyboard = KeyboardInstrumentTuning(name="A440")

    session.add_all([stringed, keyboard])
    session.commit()

    tunings = session.query(Tuning).all()
    assert len(tunings) == 2
    assert isinstance(tunings[0], StringedInstrumentTuning)
    assert isinstance(tunings[1], KeyboardInstrumentTuning)
    session.close()
