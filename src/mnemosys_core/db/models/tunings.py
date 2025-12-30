"""
Tuning models with polymorphic hierarchy parallel to Instrument hierarchy.
"""

from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from ..base import Base
from ..types import JSONEncodedList


class Tuning(Base):
    """
    Base tuning class for polymorphic hierarchy.

    Uses joined table inheritance - each subclass gets its own table
    with a foreign key to the base tuning table.

    Attributes:
        id: Primary key
        name: Tuning identifier (e.g., "Standard", "Drop D", "A440")
        tuning_type: Discriminator for polymorphism
    """

    __tablename__ = "tuning"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    tuning_type: Mapped[str] = mapped_column(String(50), nullable=False)

    # Polymorphic configuration
    __mapper_args__ = {
        "polymorphic_identity": "tuning",
        "polymorphic_on": tuning_type,
    }

    def __repr__(self) -> str:
        return f"<Tuning(id={self.id}, name='{self.name}', type={self.tuning_type})>"


class StringedInstrumentTuning(Tuning):
    """
    Tuning for stringed instruments (guitar, bass, etc.).

    Attributes:
        pitch_sequence: Array of string pitches from lowest to highest
                       (e.g., ["E2", "A2", "D3", "G3", "B3", "E4"] for standard guitar)
    """

    __tablename__ = "stringed_instrument_tuning"

    id: Mapped[int] = mapped_column(Integer, ForeignKey("tuning.id"), primary_key=True)
    pitch_sequence: Mapped[list[str]] = mapped_column(JSONEncodedList, nullable=False)

    # Polymorphic configuration
    __mapper_args__ = {
        "polymorphic_identity": "stringed",
    }

    def __repr__(self) -> str:
        return f"<StringedInstrumentTuning(id={self.id}, name='{self.name}')>"


class KeyboardInstrumentTuning(Tuning):
    """
    Tuning for keyboard instruments - placeholder implementation.

    Future attributes: pitch_reference (e.g., A440, A442), temperament, etc.
    """

    __tablename__ = "keyboard_instrument_tuning"

    id: Mapped[int] = mapped_column(Integer, ForeignKey("tuning.id"), primary_key=True)

    # Polymorphic configuration
    __mapper_args__ = {
        "polymorphic_identity": "keyboard",
    }

    def __repr__(self) -> str:
        return f"<KeyboardInstrumentTuning(id={self.id}, name='{self.name}')>"


class WindInstrumentTuning(Tuning):
    """
    Tuning for wind instruments - placeholder implementation.

    Future attributes: pitch_reference, temperament, transposition, etc.
    """

    __tablename__ = "wind_instrument_tuning"

    id: Mapped[int] = mapped_column(Integer, ForeignKey("tuning.id"), primary_key=True)

    # Polymorphic configuration
    __mapper_args__ = {
        "polymorphic_identity": "wind",
    }

    def __repr__(self) -> str:
        return f"<WindInstrumentTuning(id={self.id}, name='{self.name}')>"


class PercussionInstrumentTuning(Tuning):
    """
    Tuning for percussion instruments - placeholder implementation.

    Future attributes: head_tensions, pitches, etc.
    """

    __tablename__ = "percussion_instrument_tuning"

    id: Mapped[int] = mapped_column(Integer, ForeignKey("tuning.id"), primary_key=True)

    # Polymorphic configuration
    __mapper_args__ = {
        "polymorphic_identity": "percussion",
    }

    def __repr__(self) -> str:
        return f"<PercussionInstrumentTuning(id={self.id}, name='{self.name}')>"
