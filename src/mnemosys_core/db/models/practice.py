"""
Practice session model.
"""

from datetime import date
from typing import TYPE_CHECKING

from sqlalchemy import Date, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..base import Base
from ..types import DatabaseEnum
from . import SessionType

if TYPE_CHECKING:
    from .exercise_instance import ExerciseInstance
    from .instrument import Instrument
    from .practice_block import PracticeBlock


class Practice(Base):
    """
    Practice session record.

    Attributes:
        id: Primary key
        instrument_id: Foreign key to instruments
        session_date: Date of session
        session_type: Intensity level
        total_minutes: Total session duration
    """

    __tablename__ = "practice"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    instrument_id: Mapped[int] = mapped_column(Integer, ForeignKey("instrument.id"), nullable=False)
    session_date: Mapped[date] = mapped_column(Date, nullable=False)
    session_type: Mapped[SessionType] = mapped_column(DatabaseEnum(SessionType), nullable=False)
    total_minutes: Mapped[int] = mapped_column(Integer, nullable=False)

    # Relationships
    instrument: Mapped["Instrument"] = relationship("Instrument", back_populates="practices")
    exercise_instances: Mapped[list["ExerciseInstance"]] = relationship(
        "ExerciseInstance", back_populates="practice", cascade="all, delete-orphan", order_by="ExerciseInstance.sequence_order"
    )
    blocks: Mapped[list["PracticeBlock"]] = relationship(
        "PracticeBlock", back_populates="practice", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Practice(id={self.id}, date={self.session_date}, " f"type={self.session_type.value})>"
