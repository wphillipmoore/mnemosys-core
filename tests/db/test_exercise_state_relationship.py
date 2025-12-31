"""Tests for Exercise-ExerciseState one-to-one relationship."""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session as DBSession

from mnemosys_core.db.base import Base
from mnemosys_core.db.models.exercise import Exercise, ExerciseState


def test_exercise_has_one_exercise_state() -> None:
    """An Exercise has at most one ExerciseState (one-to-one relationship)."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    exercise = Exercise(name="Chromatic Scale", domains=[])
    ExerciseState(exercise=exercise)  # Creates and links state

    session.add(exercise)
    session.commit()

    # Verify one-to-one relationship
    retrieved_exercise = session.query(Exercise).filter_by(name="Chromatic Scale").first()
    assert retrieved_exercise is not None
    assert retrieved_exercise.exercise_state is not None  # Should be singular, not plural
    assert retrieved_exercise.exercise_state.exercise_id == exercise.id
    session.close()


def test_exercise_state_unique_per_exercise() -> None:
    """Each Exercise can have only one ExerciseState (unique constraint)."""
    from sqlalchemy.exc import IntegrityError

    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    exercise = Exercise(name="Chromatic Scale", domains=[])
    session.add(exercise)
    session.commit()

    state1 = ExerciseState(exercise_id=exercise.id)
    session.add(state1)
    session.commit()

    # Try to add second state for same exercise
    state2 = ExerciseState(exercise_id=exercise.id)
    session.add(state2)

    try:
        session.commit()
        raise AssertionError("Should have raised IntegrityError")
    except IntegrityError:
        session.rollback()
    finally:
        session.close()


def test_exercise_without_state() -> None:
    """An Exercise can exist without an ExerciseState."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    exercise = Exercise(name="Chromatic Scale", domains=[])
    session.add(exercise)
    session.commit()

    retrieved = session.query(Exercise).filter_by(name="Chromatic Scale").first()
    assert retrieved is not None
    assert retrieved.exercise_state is None  # No state yet
    session.close()
