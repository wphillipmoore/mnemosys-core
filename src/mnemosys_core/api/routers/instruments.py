"""
Instrument API endpoints.
"""


from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session as DBSession

from ...db.models import Instrument
from ...db.models.instrument import StringedInstrument
from ..dependencies import get_db
from ..schemas.instruments import InstrumentCreate, InstrumentResponse, InstrumentUpdate

router = APIRouter()


@router.post("/", response_model=InstrumentResponse, status_code=status.HTTP_201_CREATED)
def create_instrument(instrument: InstrumentCreate, db_session: DBSession = Depends(get_db)) -> StringedInstrument:
    """Create a new instrument profile."""
    db_instrument = StringedInstrument(**instrument.model_dump())
    db_session.add(db_instrument)
    db_session.flush()
    return db_instrument


@router.get("/", response_model=list[InstrumentResponse])
def list_instruments(
    db_session: DBSession = Depends(get_db), skip: int = 0, limit: int = 100
) -> list[Instrument]:
    """List all instruments."""
    return db_session.query(Instrument).offset(skip).limit(limit).all()


@router.get("/{instrument_id}", response_model=InstrumentResponse)
def get_instrument(instrument_id: int, db_session: DBSession = Depends(get_db)) -> Instrument:
    """Get instrument by ID."""
    instrument = db_session.query(Instrument).filter(Instrument.id == instrument_id).first()
    if instrument is None:
        raise HTTPException(status_code=404, detail="Instrument not found")
    return instrument


@router.put("/{instrument_id}", response_model=InstrumentResponse)
def update_instrument(
    instrument_id: int, instrument_update: InstrumentUpdate, db_session: DBSession = Depends(get_db)
) -> Instrument:
    """Update instrument by ID."""
    db_instrument = db_session.query(Instrument).filter(Instrument.id == instrument_id).first()
    if db_instrument is None:
        raise HTTPException(status_code=404, detail="Instrument not found")

    update_data = instrument_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_instrument, field, value)

    db_session.flush()
    return db_instrument


@router.delete("/{instrument_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_instrument(instrument_id: int, db_session: DBSession = Depends(get_db)) -> None:
    """Delete instrument by ID."""
    db_instrument = db_session.query(Instrument).filter(Instrument.id == instrument_id).first()
    if db_instrument is None:
        raise HTTPException(status_code=404, detail="Instrument not found")

    db_session.delete(db_instrument)
    db_session.flush()
