"""
Pydantic schemas for instrument API.
"""


from pydantic import BaseModel, Field


class InstrumentBase(BaseModel):
    """Base instrument fields."""

    name: str = Field(..., min_length=1, max_length=100)
    string_count: int = Field(..., ge=1, le=12)
    tuning: list[str] = Field(..., min_length=1)
    technique_capabilities: list[str] = Field(default_factory=list)
    scale_length: float | None = Field(None, ge=1.0, le=40.0)


class InstrumentCreate(InstrumentBase):
    """Schema for creating instruments."""

    pass


class InstrumentUpdate(BaseModel):
    """Schema for updating instruments."""

    name: str | None = Field(None, min_length=1, max_length=100)
    string_count: int | None = Field(None, ge=1, le=12)
    tuning: list[str] | None = Field(None, min_length=1)
    technique_capabilities: list[str] | None = None
    scale_length: float | None = Field(None, ge=1.0, le=40.0)


class InstrumentResponse(InstrumentBase):
    """Schema for instrument responses."""

    id: int

    model_config = {"from_attributes": True}
