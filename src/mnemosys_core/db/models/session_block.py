"""
Session block and logging models.

SessionBlock represents an individual exercise block within a session.
BlockLog records completion and quality for a session block (1:many relationship).

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
    from .session import Session


class SessionBlock(Base):
    """
    Individual exercise block within a session.

    Attributes:
        id: Primary key
        session_id: Foreign key to sessions
        exercise_id: Foreign key to exercises
        block_order: Sequence within session
        block_type: Category of work
        duration_minutes: Block duration
    """

    __tablename__ = "session_block"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    session_id: Mapped[int] = mapped_column(Integer, ForeignKey("session.id"), nullable=False)
    exercise_id: Mapped[int] = mapped_column(Integer, ForeignKey("exercise.id"), nullable=False)
    block_order: Mapped[int] = mapped_column(Integer, nullable=False)
    block_type: Mapped[BlockType] = mapped_column(DatabaseEnum(BlockType), nullable=False)
    duration_minutes: Mapped[int] = mapped_column(Integer, nullable=False)

    # Relationships
    session: Mapped["Session"] = relationship("Session", back_populates="blocks")
    exercise: Mapped["Exercise"] = relationship("Exercise", back_populates="session_blocks")
    logs: Mapped[list["BlockLog"]] = relationship("BlockLog", back_populates="session_block", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<SessionBlock(id={self.id}, order={self.block_order}, " f"type={self.block_type.value})>"


class BlockLog(Base):
    """
    Daily logging per block (completion, quality, notes).

    Attributes:
        id: Primary key
        session_block_id: Foreign key to session_blocks
        completed: Completion status
        quality: Quality assessment
        notes: Optional free text
    """

    __tablename__ = "block_log"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    session_block_id: Mapped[int] = mapped_column(Integer, ForeignKey("session_block.id"), nullable=False)
    completed: Mapped[CompletionStatus] = mapped_column(DatabaseEnum(CompletionStatus), nullable=False)
    quality: Mapped[QualityRating] = mapped_column(DatabaseEnum(QualityRating), nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Relationships
    session_block: Mapped["SessionBlock"] = relationship("SessionBlock", back_populates="logs")

    def __repr__(self) -> str:
        return f"<BlockLog(id={self.id}, completed={self.completed.value}, " f"quality={self.quality.value})>"
