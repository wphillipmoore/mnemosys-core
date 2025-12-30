"""Tests for Exercise-OverloadDimension many-to-many relationship."""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from mnemosys_core.db.base import Base
from mnemosys_core.db.models.exercises import Exercise
from mnemosys_core.db.models.overload_dimensions import OverloadDimension


def test_exercise_can_support_multiple_overload_dimensions() -> None:
    """An exercise can support multiple overload dimensions."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    exercise = Exercise(name="Chromatic Scale", domains=[], technique_tags=[])

    tempo = OverloadDimension(name="tempo", description="Speed in BPM")
    duration = OverloadDimension(name="duration", description="Length in minutes")
    complexity = OverloadDimension(name="complexity", description="Pattern difficulty")

    exercise.overload_dimensions.extend([tempo, duration, complexity])

    session.add(exercise)
    session.commit()

    retrieved = session.query(Exercise).filter_by(name="Chromatic Scale").first()
    assert retrieved is not None
    assert len(retrieved.overload_dimensions) == 3
    assert any(od.name == "tempo" for od in retrieved.overload_dimensions)
    session.close()


def test_overload_dimension_can_be_used_by_multiple_exercises() -> None:
    """An overload dimension can be used by multiple exercises."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    tempo = OverloadDimension(name="tempo", description="Speed in BPM")

    exercise1 = Exercise(name="Chromatic Scale", domains=[], technique_tags=[])
    exercise2 = Exercise(name="Alternate Picking", domains=[], technique_tags=[])

    exercise1.overload_dimensions.append(tempo)
    exercise2.overload_dimensions.append(tempo)

    session.add_all([exercise1, exercise2])
    session.commit()

    retrieved_dimension = (
        session.query(OverloadDimension).filter_by(name="tempo").first()
    )
    assert retrieved_dimension is not None
    assert len(retrieved_dimension.exercises) == 2
    session.close()
