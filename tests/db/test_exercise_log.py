"""Tests for ExerciseLog entity (replaces BlockLog)."""

from datetime import date

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from mnemosys_core.db.base import Base
from mnemosys_core.db.models import CompletionStatus, QualityRating, SessionType
from mnemosys_core.db.models.exercise import Exercise
from mnemosys_core.db.models.exercise_instance import ExerciseInstance, ExerciseLog
from mnemosys_core.db.models.instrument import StringedInstrument
from mnemosys_core.db.models.practice import Practice


def test_exercise_log_creation() -> None:
    """ExerciseLog should be creatable with completion, quality, and notes."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session_maker = sessionmaker(bind=engine)
    session_db = Session_maker()

    # Create dependencies
    instrument = StringedInstrument(name="Test Guitar", string_count=6, scale_length=25.5)
    exercise = Exercise(name="Chromatic Scale", domains=["technique"])
    practice_session = Practice(
        instrument=instrument,
        session_date=date(2025, 12, 30),
        session_type=SessionType.NORMAL,
        total_minutes=60,
    )
    instance = ExerciseInstance(
        practice=practice_session,
        exercise=exercise,
        sequence_order=1,
        parameters={"tempo": 120},
    )

    # Create exercise log
    log = ExerciseLog(
        exercise_instance=instance,
        completion_status=CompletionStatus.YES,
        quality_rating=QualityRating.CLEAN,
        notes="Great session!",
    )

    session_db.add(log)
    session_db.commit()

    # Verify
    retrieved = session_db.query(ExerciseLog).first()
    assert retrieved is not None
    assert retrieved.completion_status == CompletionStatus.YES
    assert retrieved.quality_rating == QualityRating.CLEAN
    assert retrieved.notes == "Great session!"
    assert retrieved.exercise_instance.sequence_order == 1
    session_db.close()


def test_exercise_log_notes_optional() -> None:
    """ExerciseLog notes should be optional."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session_maker = sessionmaker(bind=engine)
    session_db = Session_maker()

    instrument = StringedInstrument(name="Test Guitar", string_count=6, scale_length=25.5)
    exercise = Exercise(name="Warmup", domains=["warmup"])
    practice_session = Practice(
        instrument=instrument,
        session_date=date(2025, 12, 30),
        session_type=SessionType.LIGHT,
        total_minutes=30,
    )
    instance = ExerciseInstance(
        practice=practice_session,
        exercise=exercise,
        sequence_order=1,
        parameters={},
    )

    log = ExerciseLog(
        exercise_instance=instance,
        completion_status=CompletionStatus.PARTIAL,
        quality_rating=QualityRating.ACCEPTABLE,
    )

    session_db.add(log)
    session_db.commit()

    retrieved = session_db.query(ExerciseLog).first()
    assert retrieved is not None
    assert retrieved.notes is None
    session_db.close()


def test_exercise_instance_has_log() -> None:
    """ExerciseInstance should have relationship to ExerciseLog."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session_maker = sessionmaker(bind=engine)
    session_db = Session_maker()

    instrument = StringedInstrument(name="Test Guitar", string_count=6, scale_length=25.5)
    exercise = Exercise(name="Test Exercise", domains=["test"])
    practice_session = Practice(
        instrument=instrument,
        session_date=date(2025, 12, 30),
        session_type=SessionType.NORMAL,
        total_minutes=60,
    )
    instance = ExerciseInstance(
        practice=practice_session,
        exercise=exercise,
        sequence_order=1,
        parameters={},
    )

    log = ExerciseLog(
        exercise_instance=instance,
        completion_status=CompletionStatus.YES,
        quality_rating=QualityRating.CLEAN,
    )

    session_db.add(log)
    session_db.commit()

    # Verify through instance relationship
    retrieved_instance = session_db.query(ExerciseInstance).first()
    assert retrieved_instance is not None
    assert retrieved_instance.log is not None
    assert retrieved_instance.log.completion_status == CompletionStatus.YES
    session_db.close()


def test_exercise_log_repr() -> None:
    """ExerciseLog __repr__ should be informative."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session_maker = sessionmaker(bind=engine)
    session_db = Session_maker()

    instrument = StringedInstrument(name="Test Guitar", string_count=6, scale_length=25.5)
    exercise = Exercise(name="Test", domains=["test"])
    practice_session = Practice(
        instrument=instrument,
        session_date=date(2025, 12, 30),
        session_type=SessionType.NORMAL,
        total_minutes=60,
    )
    instance = ExerciseInstance(
        practice=practice_session,
        exercise=exercise,
        sequence_order=1,
        parameters={},
    )

    log = ExerciseLog(
        exercise_instance=instance,
        completion_status=CompletionStatus.YES,
        quality_rating=QualityRating.CLEAN,
    )
    session_db.add(log)
    session_db.commit()

    assert "ExerciseLog" in repr(log)
    assert "yes" in repr(log)
    assert "clean" in repr(log)
    session_db.close()
