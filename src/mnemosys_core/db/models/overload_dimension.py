"""
OverloadDimension entity - dimensions for progressive overload.
"""

from typing import TYPE_CHECKING

from sqlalchemy import Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..base import Base

if TYPE_CHECKING:
    from .exercise import Exercise


class OverloadDimension(Base):
    """
    Dimension for progressive overload (tempo, duration, complexity, etc.).

    OverloadDimensions are connector entities linking exercises to progression axes.
    They define the ways exercises can be made progressively harder.

    Attributes:
        id: Primary key
        name: Dimension identifier (e.g., "tempo", "duration", "complexity")
        description: Optional explanatory text
    """

    __tablename__ = "overload_dimension"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Relationships
    exercises: Mapped[list["Exercise"]] = relationship(
        "Exercise",
        secondary="exercise_overload_dimension_association",
        back_populates="overload_dimensions",
    )

    def __repr__(self) -> str:
        return f"<OverloadDimension(id={self.id}, name='{self.name}')>"
