"""
Instrument profile models with polymorphic hierarchy.
"""

from typing import TYPE_CHECKING

from sqlalchemy import Column, Float, ForeignKey, Integer, String, Table
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..base import Base

if TYPE_CHECKING:
    from .practice import Practice
    from .technique import Technique
    from .tuning import StringedInstrumentTuning


# Association table for StringedInstrument ↔ StringedInstrumentTuning
stringed_instrument_tuning_association = Table(
    "stringed_instrument_tuning_association",
    Base.metadata,
    Column("stringed_instrument_id", Integer, ForeignKey("stringed_instrument.id"), primary_key=True),
    Column("stringed_instrument_tuning_id", Integer, ForeignKey("stringed_instrument_tuning.id"), primary_key=True),
)

# Association table for Instrument ↔ Technique
instrument_technique_association = Table(
    "instrument_technique_association",
    Base.metadata,
    Column("instrument_id", Integer, ForeignKey("instrument.id"), primary_key=True),
    Column("technique_id", Integer, ForeignKey("technique.id"), primary_key=True),
)


class Instrument(Base):
    """
    Base instrument class for polymorphic hierarchy.

    Uses joined table inheritance - each subclass gets its own table
    with a foreign key to the base instrument table.

    Attributes:
        id: Primary key
        name: Instrument identifier (e.g., "Strat 6-string", "Yamaha P-125")
        instrument_type: Discriminator for polymorphism
    """

    __tablename__ = "instrument"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    instrument_type: Mapped[str] = mapped_column(String(50), nullable=False)

    # Polymorphic configuration
    __mapper_args__ = {
        "polymorphic_identity": "instrument",
        "polymorphic_on": instrument_type,
    }

    # Relationships
    practices: Mapped[list["Practice"]] = relationship(
        "Practice", back_populates="instrument", cascade="all, delete-orphan"
    )
    techniques: Mapped[list["Technique"]] = relationship(
        "Technique",
        secondary=instrument_technique_association,
        back_populates="instruments",
    )

    def __repr__(self) -> str:
        return f"<Instrument(id={self.id}, name='{self.name}', type={self.instrument_type})>"


class StringedInstrument(Instrument):
    """
    Stringed instrument (guitar, bass, etc.) - full implementation.

    Attributes:
        string_count: Number of strings
        scale_length: Scale length in inches (e.g., 25.5)
        tunings: References to StringedInstrumentTuning entities (many-to-many)
        techniques: Supported techniques (many-to-many, inherited from Instrument)
    """

    __tablename__ = "stringed_instrument"

    id: Mapped[int] = mapped_column(Integer, ForeignKey("instrument.id"), primary_key=True)
    string_count: Mapped[int] = mapped_column(Integer, nullable=False)
    scale_length: Mapped[float | None] = mapped_column(Float, nullable=True)

    # Relationships
    tunings: Mapped[list["StringedInstrumentTuning"]] = relationship(
        "StringedInstrumentTuning",
        secondary=stringed_instrument_tuning_association,
        back_populates="instruments",
    )

    # Polymorphic configuration
    __mapper_args__ = {
        "polymorphic_identity": "stringed",
    }

    def __repr__(self) -> str:
        return (
            f"<StringedInstrument(id={self.id}, name='{self.name}', "
            f"strings={self.string_count})>"
        )


class KeyboardInstrument(Instrument):
    """
    Keyboard instrument (piano, synthesizer, etc.) - placeholder implementation.

    Minimal attributes for architectural placeholder. Will be expanded in future iterations.
    """

    __tablename__ = "keyboard_instrument"

    id: Mapped[int] = mapped_column(Integer, ForeignKey("instrument.id"), primary_key=True)

    # Polymorphic configuration
    __mapper_args__ = {
        "polymorphic_identity": "keyboard",
    }

    def __repr__(self) -> str:
        return f"<KeyboardInstrument(id={self.id}, name='{self.name}')>"


class WindInstrument(Instrument):
    """
    Wind instrument (saxophone, flute, etc.) - placeholder implementation.

    Minimal attributes for architectural placeholder. Will be expanded in future iterations.
    """

    __tablename__ = "wind_instrument"

    id: Mapped[int] = mapped_column(Integer, ForeignKey("instrument.id"), primary_key=True)

    # Polymorphic configuration
    __mapper_args__ = {
        "polymorphic_identity": "wind",
    }

    def __repr__(self) -> str:
        return f"<WindInstrument(id={self.id}, name='{self.name}')>"


class PercussionInstrument(Instrument):
    """
    Percussion instrument (drums, etc.) - placeholder implementation.

    Minimal attributes for architectural placeholder. Will be expanded in future iterations.
    """

    __tablename__ = "percussion_instrument"

    id: Mapped[int] = mapped_column(Integer, ForeignKey("instrument.id"), primary_key=True)

    # Polymorphic configuration
    __mapper_args__ = {
        "polymorphic_identity": "percussion",
    }

    def __repr__(self) -> str:
        return f"<PercussionInstrument(id={self.id}, name='{self.name}')>"
