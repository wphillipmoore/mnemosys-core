"""
Instrument API endpoints.
"""

from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..dependencies import get_db
from ..schemas.instruments import InstrumentCreate, InstrumentResponse, InstrumentUpdate
from ...db.models import Instrument

router = APIRouter()


@router.post("/", response_model=InstrumentResponse, status_code=status.HTTP_201_CREATED)
def create_instrument(instrument: InstrumentCreate, db: Session = Depends(get_db)) -> Instrument:
    """Create a new instrument profile."""
    db_instrument = Instrument(**instrument.model_dump())
    db.add(db_instrument)
    db.flush()
    return db_instrument


@router.get("/", response_model=List[InstrumentResponse])
def list_instruments(
    db: Session = Depends(get_db), skip: int = 0, limit: int = 100
) -> List[Instrument]:
    """List all instruments."""
    return db.query(Instrument).offset(skip).limit(limit).all()


@router.get("/{instrument_id}", response_model=InstrumentResponse)
def get_instrument(instrument_id: int, db: Session = Depends(get_db)) -> Instrument:
    """Get instrument by ID."""
    instrument = db.query(Instrument).filter(Instrument.id == instrument_id).first()
    if instrument is None:
        raise HTTPException(status_code=404, detail="Instrument not found")
    return instrument


@router.put("/{instrument_id}", response_model=InstrumentResponse)
def update_instrument(
    instrument_id: int, instrument_update: InstrumentUpdate, db: Session = Depends(get_db)
) -> Instrument:
    """Update instrument by ID."""
    db_instrument = db.query(Instrument).filter(Instrument.id == instrument_id).first()
    if db_instrument is None:
        raise HTTPException(status_code=404, detail="Instrument not found")

    update_data = instrument_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_instrument, field, value)

    db.flush()
    return db_instrument


@router.delete("/{instrument_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_instrument(instrument_id: int, db: Session = Depends(get_db)) -> None:
    """Delete instrument by ID."""
    db_instrument = db.query(Instrument).filter(Instrument.id == instrument_id).first()
    if db_instrument is None:
        raise HTTPException(status_code=404, detail="Instrument not found")

    db.delete(db_instrument)
    db.flush()
