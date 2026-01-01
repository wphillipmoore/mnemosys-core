"""Tests for ExerciseInstance entity (replaces SessionBlock)."""

from datetime import date

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from mnemosys_core.db.base import Base
from mnemosys_core.db.models import DomainType, SessionType
from mnemosys_core.db.models.exercise import Exercise
from mnemosys_core.db.models.exercise_instance import ExerciseInstance
from mnemosys_core.db.models.instrument import StringedInstrument
from mnemosys_core.db.models.practice import Practice


def test_exercise_instance_creation() -> None:
    """ExerciseInstance should be creatable with session, exercise, and order."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session_maker = sessionmaker(bind=engine)
    session_db = Session_maker()

    # Create dependencies
    instrument = StringedInstrument(
        name="Test Guitar", string_count=6, scale_length=25.5
    )
    exercise = Exercise(name="Chromatic Scale", domains=[DomainType.TECHNIQUE])
    practice_session = Practice(
        instrument=instrument,
        session_date=date(2025, 12, 30),
        session_type=SessionType.NORMAL,
        total_minutes=60,
    )

    # Create exercise instance
    instance = ExerciseInstance(
        practice=practice_session,
        exercise=exercise,
        sequence_order=1,
        parameters={"tempo": 120, "key": "C", "pattern": "alternate-picking"},
    )

    session_db.add(instance)
    session_db.commit()

    # Verify
    retrieved = session_db.query(ExerciseInstance).first()
    assert retrieved is not None
    assert retrieved.sequence_order == 1
    assert retrieved.parameters["tempo"] == 120
    assert retrieved.parameters["key"] == "C"
    assert retrieved.exercise.name == "Chromatic Scale"
    assert retrieved.practice.total_minutes == 60
    session_db.close()
    engine.dispose()


def test_exercise_instance_parameters_optional() -> None:
    """ExerciseInstance parameters should be optional (can be empty dict)."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session_maker = sessionmaker(bind=engine)
    session_db = Session_maker()

    instrument = StringedInstrument(
        name="Test Guitar", string_count=6, scale_length=25.5
    )
    exercise = Exercise(name="Warmup", domains=[DomainType.TECHNIQUE])
    practice_session = Practice(
        instrument=instrument,
        session_date=date(2025, 12, 30),
        session_type=SessionType.LIGHT,
        total_minutes=30,
    )

    instance = ExerciseInstance(
        practice=practice_session, exercise=exercise, sequence_order=1, parameters={}
    )

    session_db.add(instance)
    session_db.commit()

    retrieved = session_db.query(ExerciseInstance).first()
    assert retrieved is not None
    assert retrieved.parameters == {}
    session_db.close()
    engine.dispose()


def test_session_has_multiple_exercise_instances() -> None:
    """A session can have multiple exercise instances in sequence."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session_maker = sessionmaker(bind=engine)
    session_db = Session_maker()

    instrument = StringedInstrument(
        name="Test Guitar", string_count=6, scale_length=25.5
    )
    exercise1 = Exercise(name="Warmup", domains=[DomainType.TECHNIQUE])
    exercise2 = Exercise(name="Scales", domains=[DomainType.TECHNIQUE])
    exercise3 = Exercise(name="Arpeggios", domains=[DomainType.TECHNIQUE])

    practice_session = Practice(
        instrument=instrument,
        session_date=date(2025, 12, 30),
        session_type=SessionType.NORMAL,
        total_minutes=60,
    )

    instance1 = ExerciseInstance(
        practice=practice_session, exercise=exercise1, sequence_order=1, parameters={}
    )
    instance2 = ExerciseInstance(
        practice=practice_session,
        exercise=exercise2,
        sequence_order=2,
        parameters={"tempo": 100},
    )
    instance3 = ExerciseInstance(
        practice=practice_session,
        exercise=exercise3,
        sequence_order=3,
        parameters={"tempo": 80},
    )

    session_db.add_all([instance1, instance2, instance3])
    session_db.commit()

    # Verify through session relationship
    retrieved_session = session_db.query(Practice).first()
    assert retrieved_session is not None
    assert len(retrieved_session.exercise_instances) == 3
    assert retrieved_session.exercise_instances[0].sequence_order == 1
    assert retrieved_session.exercise_instances[1].sequence_order == 2
    assert retrieved_session.exercise_instances[2].sequence_order == 3
    session_db.close()
    engine.dispose()


def test_exercise_instance_repr() -> None:
    """ExerciseInstance __repr__ should be informative."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session_maker = sessionmaker(bind=engine)
    session_db = Session_maker()

    instrument = StringedInstrument(
        name="Test Guitar", string_count=6, scale_length=25.5
    )
    exercise = Exercise(name="Test Exercise", domains=[DomainType.TECHNIQUE])
    practice_session = Practice(
        instrument=instrument,
        session_date=date(2025, 12, 30),
        session_type=SessionType.NORMAL,
        total_minutes=60,
    )

    instance = ExerciseInstance(
        practice=practice_session, exercise=exercise, sequence_order=5, parameters={}
    )
    session_db.add(instance)
    session_db.commit()

    assert "ExerciseInstance" in repr(instance)
    assert "5" in repr(instance)
    session_db.close()
    engine.dispose()
