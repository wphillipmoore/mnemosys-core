"""
Pydantic schemas for practice API.
"""

from datetime import date

from pydantic import BaseModel, Field

from ...db.models import BlockType, CompletionStatus, QualityRating, SessionType


class PracticeBase(BaseModel):
    """Base practice fields."""

    instrument_id: int
    session_date: date
    session_type: SessionType
    total_minutes: int = Field(..., ge=1)


class PracticeCreate(PracticeBase):
    """Schema for creating practices."""

    pass


class PracticeUpdate(BaseModel):
    """Schema for updating practices."""

    instrument_id: int | None = None
    session_date: date | None = None
    session_type: SessionType | None = None
    total_minutes: int | None = Field(None, ge=1)


class PracticeResponse(PracticeBase):
    """Schema for practice responses."""

    id: int

    model_config = {"from_attributes": True}


class PracticeBlockBase(BaseModel):
    """Base practice block fields."""

    practice_id: int
    exercise_id: int
    block_order: int = Field(..., ge=0)
    block_type: BlockType
    duration_minutes: int = Field(..., ge=1)


class PracticeBlockCreate(PracticeBlockBase):
    """Schema for creating practice blocks."""

    pass


class PracticeBlockUpdate(BaseModel):
    """Schema for updating practice blocks."""

    exercise_id: int | None = None
    block_order: int | None = Field(None, ge=0)
    block_type: BlockType | None = None
    duration_minutes: int | None = Field(None, ge=1)


class PracticeBlockResponse(PracticeBlockBase):
    """Schema for practice block responses."""

    id: int

    model_config = {"from_attributes": True}


class PracticeBlockLogBase(BaseModel):
    """Base practice block log fields."""

    practice_block_id: int
    completed: CompletionStatus
    quality: QualityRating
    notes: str | None = None


class PracticeBlockLogCreate(PracticeBlockLogBase):
    """Schema for creating practice block logs."""

    pass


class PracticeBlockLogUpdate(BaseModel):
    """Schema for updating practice block logs."""

    completed: CompletionStatus | None = None
    quality: QualityRating | None = None
    notes: str | None = None


class PracticeBlockLogResponse(PracticeBlockLogBase):
    """Schema for practice block log responses."""

    id: int

    model_config = {"from_attributes": True}
