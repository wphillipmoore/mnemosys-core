"""
Model smoke tests.
"""

from sqlalchemy.orm import Session

from mnemosys_core.db.models import (
    BlockLog,
    BlockType,
    CompletionStatus,
    Exercise,
    ExerciseState,
    FatigueProfile,
    Instrument,
    QualityRating,
    Session as PracticeSession,
    SessionBlock,
    SessionType,
)


def test_can_import_all_models():
    """Test that all models can be imported."""
    assert Instrument is not None
    assert Exercise is not None
    assert ExerciseState is not None
    assert PracticeSession is not None
    assert SessionBlock is not None
    assert BlockLog is not None


def test_can_import_all_enums():
    """Test that all enums can be imported."""
    assert FatigueProfile is not None
    assert SessionType is not None
    assert BlockType is not None
    assert CompletionStatus is not None
    assert QualityRating is not None


def test_instrument_instantiation(db_session: Session):
    """Test that Instrument can be instantiated and saved."""
    instrument = Instrument(
        name="Test Guitar",
        string_count=6,
        tuning=["E2", "A2", "D3", "G3", "B3", "E4"],
        technique_capabilities=["bending"],
        scale_length=25.5,
    )
    db_session.add(instrument)
    db_session.flush()

    assert instrument.id is not None
    assert instrument.name == "Test Guitar"


def test_exercise_instantiation(db_session: Session):
    """Test that Exercise can be instantiated and saved."""
    exercise = Exercise(
        name="Chromatic Scale",
        domains=["Technique"],
        technique_tags=["alternate-picking"],
        supported_overload_dimensions=["tempo"],
    )
    db_session.add(exercise)
    db_session.flush()

    assert exercise.id is not None
    assert exercise.name == "Chromatic Scale"


def test_session_instantiation(db_session: Session):
    """Test that Session can be instantiated and saved."""
    from datetime import date

    # Create instrument first
    instrument = Instrument(
        name="Test Bass", string_count=4, tuning=["E1", "A1", "D2", "G2"], technique_capabilities=[]
    )
    db_session.add(instrument)
    db_session.flush()

    # Create session
    session = PracticeSession(
        instrument_id=instrument.id, session_date=date.today(), session_type=SessionType.NORMAL, total_minutes=30
    )
    db_session.add(session)
    db_session.flush()

    assert session.id is not None
    assert session.session_type == SessionType.NORMAL
