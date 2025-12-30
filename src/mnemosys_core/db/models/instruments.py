"""
Instrument profile models.
"""

from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import Float, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..base import Base
from ..types import JSONEncodedList

if TYPE_CHECKING:
    from .sessions import Session


class Instrument(Base):
    """
    Instrument profile defining user's physical instrument capabilities.

    Attributes:
        id: Primary key
        name: Instrument identifier (e.g., "Strat 6-string")
        string_count: Number of strings
        tuning: Array of string pitches (e.g., ["E2", "A2", "D3", "G3", "B3", "E4"])
        technique_capabilities: Supported techniques (e.g., ["bending", "tapping"])
        scale_length: Scale length in inches (e.g., 25.5)
    """

    __tablename__ = "instruments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    string_count: Mapped[int] = mapped_column(Integer, nullable=False)
    tuning: Mapped[List[str]] = mapped_column(JSONEncodedList, nullable=False)
    technique_capabilities: Mapped[List[str]] = mapped_column(JSONEncodedList, nullable=False)
    scale_length: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    # Relationships
    sessions: Mapped[List["Session"]] = relationship(
        "Session", back_populates="instrument", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Instrument(id={self.id}, name='{self.name}', strings={self.string_count})>"
