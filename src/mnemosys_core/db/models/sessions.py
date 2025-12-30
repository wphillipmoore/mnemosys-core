"""
Session, block, and logging models.
"""

from datetime import date
from typing import TYPE_CHECKING

from sqlalchemy import Date, ForeignKey, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..base import Base
from ..types import DatabaseEnum
from . import BlockType, CompletionStatus, QualityRating, SessionType

if TYPE_CHECKING:
    from .exercises import Exercise
    from .instruments import Instrument


class Session(Base):
    """
    Practice session record.

    Attributes:
        id: Primary key
        instrument_id: Foreign key to instruments
        session_date: Date of session
        session_type: Intensity level
        total_minutes: Total session duration
    """

    __tablename__ = "session"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    instrument_id: Mapped[int] = mapped_column(Integer, ForeignKey("instrument.id"), nullable=False)
    session_date: Mapped[date] = mapped_column(Date, nullable=False)
    session_type: Mapped[SessionType] = mapped_column(DatabaseEnum(SessionType), nullable=False)
    total_minutes: Mapped[int] = mapped_column(Integer, nullable=False)

    # Relationships
    instrument: Mapped["Instrument"] = relationship("Instrument", back_populates="sessions")
    blocks: Mapped[list["SessionBlock"]] = relationship(
        "SessionBlock", back_populates="session", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Session(id={self.id}, date={self.session_date}, " f"type={self.session_type.value})>"


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
