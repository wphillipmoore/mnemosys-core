"""
Practice block and logging models.

PracticeBlock represents an individual exercise block within a practice session.
PracticeBlockLog records completion and quality for a practice block (1:many relationship).

These models are being phased out in favor of ExerciseInstance/ExerciseLog,
but remain for backward compatibility.
"""

from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..base import Base
from ..types import DatabaseEnum
from . import BlockType, CompletionStatus, QualityRating

if TYPE_CHECKING:
    from .exercise import Exercise
    from .practice import Practice


class PracticeBlock(Base):
    """
    Individual exercise block within a practice session.

    Attributes:
        id: Primary key
        practice_id: Foreign key to practices
        exercise_id: Foreign key to exercises
        block_order: Sequence within practice session
        block_type: Category of work
        duration_minutes: Block duration
    """

    __tablename__ = "practice_block"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    practice_id: Mapped[int] = mapped_column(Integer, ForeignKey("practice.id"), nullable=False)
    exercise_id: Mapped[int] = mapped_column(Integer, ForeignKey("exercise.id"), nullable=False)
    block_order: Mapped[int] = mapped_column(Integer, nullable=False)
    block_type: Mapped[BlockType] = mapped_column(DatabaseEnum(BlockType), nullable=False)
    duration_minutes: Mapped[int] = mapped_column(Integer, nullable=False)

    # Relationships
    practice: Mapped["Practice"] = relationship("Practice", back_populates="blocks")
    exercise: Mapped["Exercise"] = relationship("Exercise", back_populates="practice_blocks")
    logs: Mapped[list["PracticeBlockLog"]] = relationship("PracticeBlockLog", back_populates="practice_block", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<PracticeBlock(id={self.id}, order={self.block_order}, " f"type={self.block_type.value})>"


class PracticeBlockLog(Base):
    """
    Daily logging per block (completion, quality, notes).

    Attributes:
        id: Primary key
        practice_block_id: Foreign key to practice_blocks
        completed: Completion status
        quality: Quality assessment
        notes: Optional free text
    """

    __tablename__ = "practice_block_log"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    practice_block_id: Mapped[int] = mapped_column(Integer, ForeignKey("practice_block.id"), nullable=False)
    completed: Mapped[CompletionStatus] = mapped_column(DatabaseEnum(CompletionStatus), nullable=False)
    quality: Mapped[QualityRating] = mapped_column(DatabaseEnum(QualityRating), nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Relationships
    practice_block: Mapped["PracticeBlock"] = relationship("PracticeBlock", back_populates="logs")

    def __repr__(self) -> str:
        return f"<PracticeBlockLog(id={self.id}, completed={self.completed.value}, " f"quality={self.quality.value})>"
