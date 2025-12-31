"""Tests for polymorphic Instrument hierarchy."""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from mnemosys_core.db.base import Base
from mnemosys_core.db.models.instrument import (
    Instrument,
    KeyboardInstrument,
    PercussionInstrument,
    StringedInstrument,
    WindInstrument,
)


def test_base_instrument_has_discriminator() -> None:
    """Base Instrument should have instrument_type discriminator."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    # Cannot instantiate abstract base directly - must use subclass
    instrument = StringedInstrument(
        name="Test Guitar", string_count=6, scale_length=25.5
    )
    session.add(instrument)
    session.commit()

    # Verify discriminator is set
    assert instrument.instrument_type == "stringed"
    session.close()


def test_stringed_instrument_creation() -> None:
    """StringedInstrument should be creatable with specific attributes."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    instrument = StringedInstrument(
        name="Fender Jazz Bass", string_count=4, scale_length=34.0
    )
    session.add(instrument)
    session.commit()

    retrieved = session.query(StringedInstrument).first()
    assert retrieved is not None
    assert retrieved.name == "Fender Jazz Bass"
    assert retrieved.string_count == 4
    assert retrieved.scale_length == 34.0
    assert retrieved.instrument_type == "stringed"
    session.close()


def test_placeholder_instruments_exist() -> None:
    """Placeholder instrument classes should exist."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    keyboard = KeyboardInstrument(name="Yamaha P-125")
    wind = WindInstrument(name="Yamaha YAS-280")
    percussion = PercussionInstrument(name="Pearl Export")

    session.add_all([keyboard, wind, percussion])
    session.commit()

    assert session.query(KeyboardInstrument).count() == 1
    assert session.query(WindInstrument).count() == 1
    assert session.query(PercussionInstrument).count() == 1
    session.close()


def test_polymorphic_query_returns_correct_types() -> None:
    """Querying base Instrument should return specific subclass instances."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    stringed = StringedInstrument(
        name="Guitar", string_count=6, scale_length=25.5
    )
    keyboard = KeyboardInstrument(name="Piano")

    session.add_all([stringed, keyboard])
    session.commit()

    # Query base class returns subclass instances
    instruments = session.query(Instrument).all()
    assert len(instruments) == 2
    assert isinstance(instruments[0], StringedInstrument)
    assert isinstance(instruments[1], KeyboardInstrument)
    session.close()
