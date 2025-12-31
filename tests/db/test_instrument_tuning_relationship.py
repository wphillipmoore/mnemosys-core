"""Tests for Instrument-Tuning many-to-many relationships."""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from mnemosys_core.db.base import Base
from mnemosys_core.db.models.instrument import StringedInstrument
from mnemosys_core.db.models.tuning import StringedInstrumentTuning


def test_stringed_instrument_can_have_multiple_tunings() -> None:
    """A StringedInstrument can be associated with multiple tunings."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    # Create instrument
    guitar = StringedInstrument(
        name="Strat", string_count=6, scale_length=25.5
    )

    # Create tunings
    standard = StringedInstrumentTuning(
        name="Standard", pitch_sequence=["E2", "A2", "D3", "G3", "B3", "E4"]
    )
    drop_d = StringedInstrumentTuning(
        name="Drop D", pitch_sequence=["D2", "A2", "D3", "G3", "B3", "E4"]
    )

    # Associate tunings with instrument
    guitar.tunings.extend([standard, drop_d])

    session.add(guitar)
    session.commit()

    # Verify relationships
    retrieved = session.query(StringedInstrument).filter_by(name="Strat").first()
    assert retrieved is not None
    assert len(retrieved.tunings) == 2
    assert retrieved.tunings[0].name == "Standard"
    assert retrieved.tunings[1].name == "Drop D"
    session.close()


def test_tuning_can_be_used_by_multiple_instruments() -> None:
    """A tuning can be associated with multiple instruments."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    # Create tuning
    standard = StringedInstrumentTuning(
        name="Standard", pitch_sequence=["E2", "A2", "D3", "G3", "B3", "E4"]
    )

    # Create instruments
    guitar1 = StringedInstrument(
        name="Strat", string_count=6, scale_length=25.5
    )
    guitar2 = StringedInstrument(
        name="Les Paul", string_count=6, scale_length=24.75
    )

    # Associate same tuning with both instruments
    guitar1.tunings.append(standard)
    guitar2.tunings.append(standard)

    session.add_all([guitar1, guitar2])
    session.commit()

    # Verify bidirectional relationship
    retrieved_tuning = (
        session.query(StringedInstrumentTuning).filter_by(name="Standard").first()
    )
    assert retrieved_tuning is not None
    assert len(retrieved_tuning.instruments) == 2
    session.close()
