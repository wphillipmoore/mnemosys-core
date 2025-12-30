"""
Exercise and exercise state models.
"""

from datetime import date
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import Date, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..base import Base
from ..types import DatabaseEnum, JSONEncodedList
from . import FatigueProfile

if TYPE_CHECKING:
    from .sessions import SessionBlock


class Exercise(Base):
    """
    Canonical exercise definition (~35 exercises, static reference).

    Attributes:
        id: Primary key
        name: Exercise name (e.g., "Chromatic Scale")
        domains: List of applicable domains
        technique_tags: Technique categories (e.g., ["alternate-picking"])
        supported_overload_dimensions: Overload methods (e.g., ["tempo", "duration"])
        instrument_compatibility: Required instrument features
    """

    __tablename__ = "exercise"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False, unique=True)
    domains: Mapped[List[str]] = mapped_column(JSONEncodedList, nullable=False)
    technique_tags: Mapped[List[str]] = mapped_column(JSONEncodedList, nullable=False)
    supported_overload_dimensions: Mapped[List[str]] = mapped_column(JSONEncodedList, nullable=False)
    instrument_compatibility: Mapped[Optional[List[str]]] = mapped_column(JSONEncodedList, nullable=True)

    # Relationships
    exercise_states: Mapped[List["ExerciseState"]] = relationship(
        "ExerciseState", back_populates="exercise", cascade="all, delete-orphan"
    )
    session_blocks: Mapped[List["SessionBlock"]] = relationship("SessionBlock", back_populates="exercise")

    def __repr__(self) -> str:
        return f"<Exercise(id={self.id}, name='{self.name}')>"


class ExerciseState(Base):
    """
    Per-exercise tracking state (one row per exercise being tracked).

    Attributes:
        id: Primary key
        exercise_id: Foreign key to exercises
        last_practiced_date: Most recent practice date
        rolling_minutes_7d: Total minutes in last 7 days
        rolling_minutes_28d: Total minutes in last 28 days
        mastery_estimate: Skill level (0.0 = novice, 1.0 = mastery)
        last_fatigue_profile: Most recent fatigue state
    """

    __tablename__ = "exercise_state"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    exercise_id: Mapped[int] = mapped_column(Integer, ForeignKey("exercise.id"), nullable=False, unique=True)
    last_practiced_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    rolling_minutes_7d: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    rolling_minutes_28d: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    mastery_estimate: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    last_fatigue_profile: Mapped[Optional[FatigueProfile]] = mapped_column(DatabaseEnum(FatigueProfile), nullable=True)

    # Relationships
    exercise: Mapped["Exercise"] = relationship("Exercise", back_populates="exercise_states")

    def __repr__(self) -> str:
        return (
            f"<ExerciseState(id={self.id}, exercise_id={self.exercise_id}, " f"mastery={self.mastery_estimate:.2f})>"
        )
