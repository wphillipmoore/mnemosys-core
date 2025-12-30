"""
Pydantic schemas for instrument API.
"""

from typing import List, Optional

from pydantic import BaseModel, Field


class InstrumentBase(BaseModel):
    """Base instrument fields."""

    name: str = Field(..., min_length=1, max_length=100)
    string_count: int = Field(..., ge=1, le=12)
    tuning: List[str] = Field(..., min_length=1)
    technique_capabilities: List[str] = Field(default_factory=list)
    scale_length: Optional[float] = Field(None, ge=1.0, le=40.0)


class InstrumentCreate(InstrumentBase):
    """Schema for creating instruments."""

    pass


class InstrumentUpdate(BaseModel):
    """Schema for updating instruments."""

    name: Optional[str] = Field(None, min_length=1, max_length=100)
    string_count: Optional[int] = Field(None, ge=1, le=12)
    tuning: Optional[List[str]] = Field(None, min_length=1)
    technique_capabilities: Optional[List[str]] = None
    scale_length: Optional[float] = Field(None, ge=1.0, le=40.0)


class InstrumentResponse(InstrumentBase):
    """Schema for instrument responses."""

    id: int

    model_config = {"from_attributes": True}
