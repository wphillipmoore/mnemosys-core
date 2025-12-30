"""
Database models for FSIPS schema.

This module exports all ORM models and enums.
"""

import enum


# Domain enums
class DomainType(enum.Enum):
    """Exercise domains."""

    TECHNIQUE = "Technique"
    HARMONY = "Harmony"
    RHYTHM = "Rhythm"
    MUSICIANSHIP = "Musicianship"


class FatigueProfile(enum.Enum):
    """Fatigue states for exercise tracking."""

    F0 = "F0"  # Fresh
    F1 = "F1"  # Light fatigue
    F2 = "F2"  # Heavy fatigue


class SessionType(enum.Enum):
    """Practice session intensity."""

    NORMAL = "normal"
    LIGHT = "light"
    HEAVY = "heavy"
    DELOAD = "deload"


class BlockType(enum.Enum):
    """Session block categories."""

    WARMUP = "Warmup"
    TECHNIQUE = "Technique"
    HARMONY = "Harmony"
    RHYTHM = "Rhythm"
    APPLICATION = "Application"


class CompletionStatus(enum.Enum):
    """Block completion states."""

    YES = "yes"
    PARTIAL = "partial"
    NO = "no"


class QualityRating(enum.Enum):
    """Practice quality assessment."""

    CLEAN = "clean"
    ACCEPTABLE = "acceptable"
    SLOPPY = "sloppy"


# Import models for convenience
from .exercises import Exercise, ExerciseState
from .instruments import Instrument
from .sessions import BlockLog, Session, SessionBlock

__all__ = [
    # Enums
    "BlockType",
    "CompletionStatus",
    "DomainType",
    "FatigueProfile",
    "QualityRating",
    "SessionType",
    # Models
    "BlockLog",
    "Exercise",
    "ExerciseState",
    "Instrument",
    "Session",
    "SessionBlock",
]
