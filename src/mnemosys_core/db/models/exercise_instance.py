"""
Exercise instance and logging models.

ExerciseInstance represents a parameterized exercise for a specific practice session.
ExerciseLog records the performance outcome for an exercise instance (1:1 relationship).
"""

from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..base import Base
from ..types import DatabaseEnum, JSONEncodedDict
from . import CompletionStatus, QualityRating

if TYPE_CHECKING:
    from .exercise import Exercise
    from .practice import Practice


class ExerciseInstance(Base):
    """
    Parameterized exercise for a specific practice session.

    Replaces SessionBlock with cleaner semantics and parameterization support.

    Attributes:
        id: Primary key
        practice_id: Foreign key to practices
        exercise_id: Foreign key to exercises
        sequence_order: Position within practice session (1-indexed)
        parameters: Exercise parameters (tempo, key, pattern, duration, etc.)
    """

    __tablename__ = "exercise_instance"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    practice_id: Mapped[int] = mapped_column(Integer, ForeignKey("practice.id"), nullable=False)
    exercise_id: Mapped[int] = mapped_column(Integer, ForeignKey("exercise.id"), nullable=False)
    sequence_order: Mapped[int] = mapped_column(Integer, nullable=False)
    parameters: Mapped[dict[str, str | int | float]] = mapped_column(JSONEncodedDict, nullable=False, default=dict)

    # Relationships
    practice: Mapped["Practice"] = relationship("Practice", back_populates="exercise_instances")
    exercise: Mapped["Exercise"] = relationship("Exercise", back_populates="exercise_instances")
    log: Mapped["ExerciseLog | None"] = relationship(
        "ExerciseLog", back_populates="exercise_instance", cascade="all, delete-orphan", uselist=False
    )

    def __repr__(self) -> str:
        return f"<ExerciseInstance(id={self.id}, sequence={self.sequence_order})>"


class ExerciseLog(Base):
    """
    Performance record for an exercise instance (1:1 relationship).

    Replaces BlockLog with cleaner semantics tied to ExerciseInstance.

    Attributes:
        id: Primary key
        exercise_instance_id: Foreign key to exercise_instance (unique - one log per instance)
        completion_status: Whether exercise was completed (yes/partial/no)
        quality_rating: Subjective quality assessment (clean/acceptable/sloppy)
        notes: Optional free text notes
    """

    __tablename__ = "exercise_log"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    exercise_instance_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("exercise_instance.id"), nullable=False, unique=True
    )
    completion_status: Mapped[CompletionStatus] = mapped_column(DatabaseEnum(CompletionStatus), nullable=False)
    quality_rating: Mapped[QualityRating] = mapped_column(DatabaseEnum(QualityRating), nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Relationships
    exercise_instance: Mapped["ExerciseInstance"] = relationship("ExerciseInstance", back_populates="log")

    def __repr__(self) -> str:
        return (
            f"<ExerciseLog(id={self.id}, status={self.completion_status.value}, "
            f"quality={self.quality_rating.value})>"
        )
