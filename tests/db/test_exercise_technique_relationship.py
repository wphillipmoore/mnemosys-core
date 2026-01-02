"""Tests for Exercise-Technique many-to-many relationship."""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from mnemosys_core.db.base import Base
from mnemosys_core.db.models.exercise import Exercise
from mnemosys_core.db.models.technique import Technique


def test_exercise_can_use_multiple_techniques() -> None:
    """An exercise can use multiple techniques."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    exercise = Exercise(name="Chromatic Scale", domains=[])

    alternate = Technique(name="alternate picking")
    legato = Technique(name="legato")
    string_skipping = Technique(name="string skipping")

    exercise.techniques.extend([alternate, legato, string_skipping])

    session.add(exercise)
    session.commit()

    retrieved = session.query(Exercise).filter_by(name="Chromatic Scale").first()
    assert retrieved is not None
    assert len(retrieved.techniques) == 3
    assert any(technique.name == "alternate picking" for technique in retrieved.techniques)
    session.close()
    engine.dispose()


def test_technique_can_be_used_by_multiple_exercises() -> None:
    """A technique can be used by multiple exercises."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    alternate = Technique(name="alternate picking")

    exercise1 = Exercise(name="Chromatic Scale", domains=[])
    exercise2 = Exercise(name="String Skipping", domains=[])

    exercise1.techniques.append(alternate)
    exercise2.techniques.append(alternate)

    session.add_all([exercise1, exercise2])
    session.commit()

    retrieved_technique = (
        session.query(Technique).filter_by(name="alternate picking").first()
    )
    assert retrieved_technique is not None
    assert len(retrieved_technique.exercises) == 2
    session.close()
    engine.dispose()
