"""
Pydantic schemas for session API.
"""

from datetime import date
from typing import List, Optional

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

    instrument_id: Optional[int] = None
    session_date: Optional[date] = None
    session_type: Optional[SessionType] = None
    total_minutes: Optional[int] = Field(None, ge=1)


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

    exercise_id: Optional[int] = None
    block_order: Optional[int] = Field(None, ge=0)
    block_type: Optional[BlockType] = None
    duration_minutes: Optional[int] = Field(None, ge=1)


class SessionBlockResponse(SessionBlockBase):
    """Schema for session block responses."""

    id: int

    model_config = {"from_attributes": True}


class BlockLogBase(BaseModel):
    """Base block log fields."""

    session_block_id: int
    completed: CompletionStatus
    quality: QualityRating
    notes: Optional[str] = None


class BlockLogCreate(BlockLogBase):
    """Schema for creating block logs."""

    pass


class BlockLogUpdate(BaseModel):
    """Schema for updating block logs."""

    completed: Optional[CompletionStatus] = None
    quality: Optional[QualityRating] = None
    notes: Optional[str] = None


class BlockLogResponse(BlockLogBase):
    """Schema for block log responses."""

    id: int

    model_config = {"from_attributes": True}
