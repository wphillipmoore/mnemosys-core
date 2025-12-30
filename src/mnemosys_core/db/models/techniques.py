"""
Technique entity - connector for exercises, repertoire, and instruments.
"""

from typing import TYPE_CHECKING

from sqlalchemy import Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..base import Base

if TYPE_CHECKING:
    from .exercises import Exercise
    from .instruments import Instrument


class Technique(Base):
    """
    Technique entity representing a musical technique.

    Techniques are connector entities with no independent state tracking.
    They link exercises, repertoire entries, and instruments through
    many-to-many relationships.

    Technique mastery is inferred from exercise and repertoire performance,
    not tracked directly.

    Attributes:
        id: Primary key
        name: Technique identifier (e.g., "string skipping", "alternate picking")
        description: Optional explanatory text
    """

    __tablename__ = "technique"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Relationships
    instruments: Mapped[list["Instrument"]] = relationship(
        "Instrument",
        secondary="instrument_technique_association",
        back_populates="techniques",
    )
    exercises: Mapped[list["Exercise"]] = relationship(
        "Exercise",
        secondary="exercise_technique_association",
        back_populates="techniques",
    )

    def __repr__(self) -> str:
        return f"<Technique(id={self.id}, name='{self.name}')>"
