"""
Pydantic schemas for session API.
"""

from datetime import date

from pydantic import BaseModel, Field

from ...db.models import BlockType, CompletionStatus, QualityRating, SessionType


class SessionBase(BaseModel):
    """Base session fields."""

    instrument_id: int
    session_date: date
    session_type: SessionType
    total_minutes: int = Field(..., ge=1)


class SessionCreate(SessionBase):
    """Schema for creating sessions."""

    pass


class SessionUpdate(BaseModel):
    """Schema for updating sessions."""

    instrument_id: int | None = None
    session_date: date | None = None
    session_type: SessionType | None = None
    total_minutes: int | None = Field(None, ge=1)


class SessionResponse(SessionBase):
    """Schema for session responses."""

    id: int

    model_config = {"from_attributes": True}


class SessionBlockBase(BaseModel):
    """Base session block fields."""

    session_id: int
    exercise_id: int
    block_order: int = Field(..., ge=0)
    block_type: BlockType
    duration_minutes: int = Field(..., ge=1)


class SessionBlockCreate(SessionBlockBase):
    """Schema for creating session blocks."""

    pass


class SessionBlockUpdate(BaseModel):
    """Schema for updating session blocks."""

    exercise_id: int | None = None
    block_order: int | None = Field(None, ge=0)
    block_type: BlockType | None = None
    duration_minutes: int | None = Field(None, ge=1)


class SessionBlockResponse(SessionBlockBase):
    """Schema for session block responses."""

    id: int

    model_config = {"from_attributes": True}


class BlockLogBase(BaseModel):
    """Base block log fields."""

    session_block_id: int
    completed: CompletionStatus
    quality: QualityRating
    notes: str | None = None


class BlockLogCreate(BlockLogBase):
    """Schema for creating block logs."""

    pass


class BlockLogUpdate(BaseModel):
    """Schema for updating block logs."""

    completed: CompletionStatus | None = None
    quality: QualityRating | None = None
    notes: str | None = None


class BlockLogResponse(BlockLogBase):
    """Schema for block log responses."""

    id: int

    model_config = {"from_attributes": True}
