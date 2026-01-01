"""
Model smoke tests.
"""

from sqlalchemy.orm import Session

from mnemosys_core.db.models import (
    BlockType,
    CompletionStatus,
    DomainType,
    Exercise,
    ExerciseState,
    FatigueProfile,
    Instrument,
    Practice,
    PracticeBlock,
    PracticeBlockLog,
    QualityRating,
    SessionType,
)


def test_can_import_all_models() -> None:
    """Test that all models can be imported."""
    assert Instrument is not None
    assert Exercise is not None
    assert ExerciseState is not None
    assert Practice is not None
    assert PracticeBlock is not None
    assert PracticeBlockLog is not None


def test_can_import_all_enums() -> None:
    """Test that all enums can be imported."""
    assert FatigueProfile is not None
    assert SessionType is not None
    assert BlockType is not None
    assert CompletionStatus is not None
    assert QualityRating is not None


def test_instrument_instantiation(db_session: Session) -> None:
    """Test that StringedInstrument can be instantiated and saved."""
    from mnemosys_core.db.models.instrument import StringedInstrument

    instrument = StringedInstrument(
        name="Test Guitar",
        string_count=6,
        scale_length=25.5,
    )
    db_session.add(instrument)
    db_session.flush()

    assert instrument.id is not None
    assert instrument.name == "Test Guitar"


def test_exercise_instantiation(db_session: Session) -> None:
    """Test that Exercise can be instantiated and saved."""
    exercise = Exercise(
        name="Chromatic Scale",
        domains=[DomainType.TECHNIQUE],
    )
    db_session.add(exercise)
    db_session.flush()

    assert exercise.id is not None
    assert exercise.name == "Chromatic Scale"


def test_session_instantiation(db_session: Session) -> None:
    """Test that Session can be instantiated and saved."""
    from datetime import date

    from mnemosys_core.db.models.instrument import StringedInstrument

    # Create instrument first
    instrument = StringedInstrument(name="Test Bass", string_count=4, scale_length=34.0)
    db_session.add(instrument)
    db_session.flush()

    # Create session
    session = Practice(
        instrument_id=instrument.id, session_date=date.today(), session_type=SessionType.NORMAL, total_minutes=30
    )
    db_session.add(session)
    db_session.flush()

    assert session.id is not None
    assert session.session_type == SessionType.NORMAL


def test_instrument_repr(db_session: Session) -> None:
    """Test StringedInstrument __repr__ method."""
    from mnemosys_core.db.models.instrument import StringedInstrument

    instrument = StringedInstrument(
        name="Test Guitar",
        string_count=6,
        scale_length=25.5,
    )
    db_session.add(instrument)
    db_session.flush()

    repr_str = repr(instrument)
    assert "StringedInstrument" in repr_str
    assert "Test Guitar" in repr_str
    assert str(instrument.id) in repr_str


def test_exercise_repr(db_session: Session) -> None:
    """Test Exercise __repr__ method."""
    exercise = Exercise(
        name="Chromatic Scale",
        domains=[DomainType.TECHNIQUE],
    )
    db_session.add(exercise)
    db_session.flush()

    repr_str = repr(exercise)
    assert "Exercise" in repr_str
    assert "Chromatic Scale" in repr_str
    assert str(exercise.id) in repr_str


def test_exercise_state_repr(db_session: Session) -> None:
    """Test ExerciseState __repr__ method."""
    exercise = Exercise(
        name="Test Exercise",
        domains=[DomainType.TECHNIQUE],
    )
    db_session.add(exercise)
    db_session.flush()

    state = ExerciseState(
        exercise_id=exercise.id,
        rolling_minutes_7d=100,
        rolling_minutes_28d=400,
        mastery_estimate=0.75,
    )
    db_session.add(state)
    db_session.flush()

    repr_str = repr(state)
    assert "ExerciseState" in repr_str
    assert str(state.exercise_id) in repr_str
    assert "0.75" in repr_str


def test_session_repr(db_session: Session) -> None:
    """Test Session __repr__ method."""
    from datetime import date

    from mnemosys_core.db.models.instrument import StringedInstrument

    instrument = StringedInstrument(name="Test Guitar", string_count=6, scale_length=25.5)
    db_session.add(instrument)
    db_session.flush()

    session = Practice(
        instrument_id=instrument.id,
        session_date=date(2025, 1, 15),
        session_type=SessionType.NORMAL,
        total_minutes=60,
    )
    db_session.add(session)
    db_session.flush()

    repr_str = repr(session)
    assert "Practice" in repr_str
    assert "2025-01-15" in repr_str
    assert "normal" in repr_str


def test_session_block_repr(db_session: Session) -> None:
    """Test PracticeBlock __repr__ method."""
    from datetime import date

    from mnemosys_core.db.models.instrument import StringedInstrument

    instrument = StringedInstrument(name="Test Guitar", string_count=6, scale_length=25.5)
    db_session.add(instrument)
    db_session.flush()

    exercise = Exercise(
        name="Test Exercise",
        domains=[DomainType.TECHNIQUE],
    )
    db_session.add(exercise)
    db_session.flush()

    session = Practice(
        instrument_id=instrument.id,
        session_date=date.today(),
        session_type=SessionType.NORMAL,
        total_minutes=60,
    )
    db_session.add(session)
    db_session.flush()

    block = PracticeBlock(
        practice_id=session.id,
        exercise_id=exercise.id,
        block_order=1,
        block_type=BlockType.WARMUP,
        duration_minutes=15,
    )
    db_session.add(block)
    db_session.flush()

    repr_str = repr(block)
    assert "PracticeBlock" in repr_str
    assert "order=1" in repr_str
    assert "Warmup" in repr_str


def test_block_log_repr(db_session: Session) -> None:
    """Test PracticeBlockLog __repr__ method."""
    from datetime import date

    from mnemosys_core.db.models.instrument import StringedInstrument

    instrument = StringedInstrument(name="Test Guitar", string_count=6, scale_length=25.5)
    db_session.add(instrument)
    db_session.flush()

    exercise = Exercise(
        name="Test Exercise",
        domains=[DomainType.TECHNIQUE],
    )
    db_session.add(exercise)
    db_session.flush()

    session = Practice(
        instrument_id=instrument.id,
        session_date=date.today(),
        session_type=SessionType.NORMAL,
        total_minutes=60,
    )
    db_session.add(session)
    db_session.flush()

    block = PracticeBlock(
        practice_id=session.id,
        exercise_id=exercise.id,
        block_order=1,
        block_type=BlockType.WARMUP,
        duration_minutes=15,
    )
    db_session.add(block)
    db_session.flush()

    log = PracticeBlockLog(
        practice_block_id=block.id,
        completed=CompletionStatus.YES,
        quality=QualityRating.CLEAN,
        notes="Test notes",
    )
    db_session.add(log)
    db_session.flush()

    repr_str = repr(log)
    assert "PracticeBlockLog" in repr_str
    assert "yes" in repr_str
    assert "clean" in repr_str
