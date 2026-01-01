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
    engine.dispose()


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
    engine.dispose()


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
    engine.dispose()


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
    engine.dispose()


def test_base_tuning_repr() -> None:
    """Base Tuning __repr__ should include id, name, and type."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    tuning = StringedInstrumentTuning(
        name="Standard", pitch_sequence=["E2", "A2", "D3", "G3"]
    )
    session.add(tuning)
    session.commit()

    # Explicitly call base class __repr__ to test it
    repr_str = Tuning.__repr__(tuning)
    assert "Tuning" in repr_str
    assert "Standard" in repr_str
    assert str(tuning.id) in repr_str
    assert "stringed" in repr_str
    session.close()
    engine.dispose()


def test_stringed_instrument_tuning_repr() -> None:
    """StringedInstrumentTuning __repr__ should include id and name."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    tuning = StringedInstrumentTuning(
        name="Drop D", pitch_sequence=["D2", "A2", "D3", "G3", "B3", "E4"]
    )
    session.add(tuning)
    session.commit()

    repr_str = repr(tuning)
    assert "StringedInstrumentTuning" in repr_str
    assert "Drop D" in repr_str
    assert str(tuning.id) in repr_str
    session.close()
    engine.dispose()


def test_keyboard_instrument_tuning_repr() -> None:
    """KeyboardInstrumentTuning __repr__ should include id and name."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    tuning = KeyboardInstrumentTuning(name="A440")
    session.add(tuning)
    session.commit()

    repr_str = repr(tuning)
    assert "KeyboardInstrumentTuning" in repr_str
    assert "A440" in repr_str
    assert str(tuning.id) in repr_str
    session.close()
    engine.dispose()


def test_wind_instrument_tuning_repr() -> None:
    """WindInstrumentTuning __repr__ should include id and name."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    tuning = WindInstrumentTuning(name="A442")
    session.add(tuning)
    session.commit()

    repr_str = repr(tuning)
    assert "WindInstrumentTuning" in repr_str
    assert "A442" in repr_str
    assert str(tuning.id) in repr_str
    session.close()
    engine.dispose()


def test_percussion_instrument_tuning_repr() -> None:
    """PercussionInstrumentTuning __repr__ should include id and name."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    tuning = PercussionInstrumentTuning(name="Standard")
    session.add(tuning)
    session.commit()

    repr_str = repr(tuning)
    assert "PercussionInstrumentTuning" in repr_str
    assert "Standard" in repr_str
    assert str(tuning.id) in repr_str
    session.close()
    engine.dispose()
