"""
Pydantic schemas for exercise API.
"""

from datetime import date
from typing import List, Optional

from pydantic import BaseModel, Field

from ...db.models import FatigueProfile


class ExerciseBase(BaseModel):
    """Base exercise fields."""

    name: str = Field(..., min_length=1, max_length=200)
    domains: List[str] = Field(..., min_length=1)
    technique_tags: List[str] = Field(default_factory=list)
    supported_overload_dimensions: List[str] = Field(default_factory=list)
    instrument_compatibility: Optional[List[str]] = None


class ExerciseCreate(ExerciseBase):
    """Schema for creating exercises."""

    pass


class ExerciseUpdate(BaseModel):
    """Schema for updating exercises."""

    name: Optional[str] = Field(None, min_length=1, max_length=200)
    domains: Optional[List[str]] = Field(None, min_length=1)
    technique_tags: Optional[List[str]] = None
    supported_overload_dimensions: Optional[List[str]] = None
    instrument_compatibility: Optional[List[str]] = None


class ExerciseResponse(ExerciseBase):
    """Schema for exercise responses."""

    id: int

    model_config = {"from_attributes": True}


class ExerciseStateBase(BaseModel):
    """Base exercise state fields."""

    exercise_id: int
    last_practiced_date: Optional[date] = None
    rolling_minutes_7d: int = Field(default=0, ge=0)
    rolling_minutes_28d: int = Field(default=0, ge=0)
    mastery_estimate: float = Field(default=0.0, ge=0.0, le=1.0)
    last_fatigue_profile: Optional[FatigueProfile] = None


class ExerciseStateCreate(ExerciseStateBase):
    """Schema for creating exercise states."""

    pass


class ExerciseStateUpdate(BaseModel):
    """Schema for updating exercise states."""

    last_practiced_date: Optional[date] = None
    rolling_minutes_7d: Optional[int] = Field(None, ge=0)
    rolling_minutes_28d: Optional[int] = Field(None, ge=0)
    mastery_estimate: Optional[float] = Field(None, ge=0.0, le=1.0)
    last_fatigue_profile: Optional[FatigueProfile] = None


class ExerciseStateResponse(ExerciseStateBase):
    """Schema for exercise state responses."""

    id: int

    model_config = {"from_attributes": True}
