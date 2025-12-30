"""
Pydantic schemas for exercise API.
"""

from datetime import date

from pydantic import BaseModel, Field

from ...db.models import FatigueProfile


class ExerciseBase(BaseModel):
    """Base exercise fields."""

    name: str = Field(..., min_length=1, max_length=200)
    domains: list[str] = Field(..., min_length=1)
    technique_tags: list[str] = Field(default_factory=list)
    supported_overload_dimensions: list[str] = Field(default_factory=list)
    instrument_compatibility: list[str] | None = None


class ExerciseCreate(ExerciseBase):
    """Schema for creating exercises."""

    pass


class ExerciseUpdate(BaseModel):
    """Schema for updating exercises."""

    name: str | None = Field(None, min_length=1, max_length=200)
    domains: list[str] | None = Field(None, min_length=1)
    technique_tags: list[str] | None = None
    supported_overload_dimensions: list[str] | None = None
    instrument_compatibility: list[str] | None = None


class ExerciseResponse(ExerciseBase):
    """Schema for exercise responses."""

    id: int

    model_config = {"from_attributes": True}


class ExerciseStateBase(BaseModel):
    """Base exercise state fields."""

    exercise_id: int
    last_practiced_date: date | None = None
    rolling_minutes_7d: int = Field(default=0, ge=0)
    rolling_minutes_28d: int = Field(default=0, ge=0)
    mastery_estimate: float = Field(default=0.0, ge=0.0, le=1.0)
    last_fatigue_profile: FatigueProfile | None = None


class ExerciseStateCreate(ExerciseStateBase):
    """Schema for creating exercise states."""

    pass


class ExerciseStateUpdate(BaseModel):
    """Schema for updating exercise states."""

    last_practiced_date: date | None = None
    rolling_minutes_7d: int | None = Field(None, ge=0)
    rolling_minutes_28d: int | None = Field(None, ge=0)
    mastery_estimate: float | None = Field(None, ge=0.0, le=1.0)
    last_fatigue_profile: FatigueProfile | None = None


class ExerciseStateResponse(ExerciseStateBase):
    """Schema for exercise state responses."""

    id: int

    model_config = {"from_attributes": True}
