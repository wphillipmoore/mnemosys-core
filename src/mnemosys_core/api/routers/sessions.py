"""
Session API endpoints.
"""


from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session as DBSession

from ...db.models import Practice, PracticeBlock, PracticeBlockLog
from ..dependencies import get_db
from ..schemas.sessions import (
    PracticeBlockLogCreate,
    PracticeBlockLogResponse,
    PracticeBlockLogUpdate,
    PracticeBlockCreate,
    PracticeBlockResponse,
    PracticeBlockUpdate,
    PracticeCreate,
    PracticeResponse,
    PracticeUpdate,
)

router = APIRouter()


# Session endpoints
@router.post("/", response_model=PracticeResponse, status_code=status.HTTP_201_CREATED)
def create_session(session: PracticeCreate, db_session: DBSession = Depends(get_db)) -> Practice:
    """Create a new practice session."""
    db_session_obj = Practice(**session.model_dump())
    db_session.add(db_session_obj)
    db_session.flush()
    return db_session_obj


@router.get("/", response_model=list[PracticeResponse])
def list_sessions(db_session: DBSession = Depends(get_db), skip: int = 0, limit: int = 100) -> list[Practice]:
    """List all sessions."""
    return db_session.query(Practice).offset(skip).limit(limit).all()


@router.get("/{session_id}", response_model=PracticeResponse)
def get_session(session_id: int, db_session: DBSession = Depends(get_db)) -> Practice:
    """Get session by ID."""
    session = db_session.query(Practice).filter(Practice.id == session_id).first()
    if session is None:
        raise HTTPException(status_code=404, detail="Session not found")
    return session


@router.put("/{session_id}", response_model=PracticeResponse)
def update_session(
    session_id: int, session_update: PracticeUpdate, db_session: DBSession = Depends(get_db)
) -> Practice:
    """Update session by ID."""
    db_session_obj = db_session.query(Practice).filter(Practice.id == session_id).first()
    if db_session_obj is None:
        raise HTTPException(status_code=404, detail="Session not found")

    update_data = session_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_session_obj, field, value)

    db_session.flush()
    return db_session_obj


@router.delete("/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_session(session_id: int, db_session: DBSession = Depends(get_db)) -> None:
    """Delete session by ID."""
    db_session_obj = db_session.query(Practice).filter(Practice.id == session_id).first()
    if db_session_obj is None:
        raise HTTPException(status_code=404, detail="Session not found")

    db_session.delete(db_session_obj)
    db_session.flush()


# Session block endpoints
@router.post("/blocks/", response_model=PracticeBlockResponse, status_code=status.HTTP_201_CREATED)
def create_session_block(block: PracticeBlockCreate, db_session: DBSession = Depends(get_db)) -> PracticeBlock:
    """Create a new session block."""
    db_block = PracticeBlock(**block.model_dump())
    db_session.add(db_block)
    db_session.flush()
    return db_block


@router.get("/blocks/", response_model=list[PracticeBlockResponse])
def list_session_blocks(
    db_session: DBSession = Depends(get_db), skip: int = 0, limit: int = 100
) -> list[PracticeBlock]:
    """List all session blocks."""
    return db_session.query(PracticeBlock).offset(skip).limit(limit).all()


@router.get("/blocks/{block_id}", response_model=PracticeBlockResponse)
def get_session_block(block_id: int, db_session: DBSession = Depends(get_db)) -> PracticeBlock:
    """Get session block by ID."""
    block = db_session.query(PracticeBlock).filter(PracticeBlock.id == block_id).first()
    if block is None:
        raise HTTPException(status_code=404, detail="Session block not found")
    return block


@router.put("/blocks/{block_id}", response_model=PracticeBlockResponse)
def update_session_block(
    block_id: int, block_update: PracticeBlockUpdate, db_session: DBSession = Depends(get_db)
) -> PracticeBlock:
    """Update session block by ID."""
    db_block = db_session.query(PracticeBlock).filter(PracticeBlock.id == block_id).first()
    if db_block is None:
        raise HTTPException(status_code=404, detail="Session block not found")

    update_data = block_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_block, field, value)

    db_session.flush()
    return db_block


@router.delete("/blocks/{block_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_session_block(block_id: int, db_session: DBSession = Depends(get_db)) -> None:
    """Delete session block by ID."""
    db_block = db_session.query(PracticeBlock).filter(PracticeBlock.id == block_id).first()
    if db_block is None:
        raise HTTPException(status_code=404, detail="Session block not found")

    db_session.delete(db_block)
    db_session.flush()


# Block log endpoints
@router.post("/logs/", response_model=PracticeBlockLogResponse, status_code=status.HTTP_201_CREATED)
def create_block_log(log: PracticeBlockLogCreate, db_session: DBSession = Depends(get_db)) -> PracticeBlockLog:
    """Create a new block log."""
    db_log = PracticeBlockLog(**log.model_dump())
    db_session.add(db_log)
    db_session.flush()
    return db_log


@router.get("/logs/", response_model=list[PracticeBlockLogResponse])
def list_block_logs(db_session: DBSession = Depends(get_db), skip: int = 0, limit: int = 100) -> list[PracticeBlockLog]:
    """List all block logs."""
    return db_session.query(PracticeBlockLog).offset(skip).limit(limit).all()


@router.get("/logs/{log_id}", response_model=PracticeBlockLogResponse)
def get_block_log(log_id: int, db_session: DBSession = Depends(get_db)) -> PracticeBlockLog:
    """Get block log by ID."""
    log = db_session.query(PracticeBlockLog).filter(PracticeBlockLog.id == log_id).first()
    if log is None:
        raise HTTPException(status_code=404, detail="Block log not found")
    return log


@router.put("/logs/{log_id}", response_model=PracticeBlockLogResponse)
def update_block_log(log_id: int, log_update: PracticeBlockLogUpdate, db_session: DBSession = Depends(get_db)) -> PracticeBlockLog:
    """Update block log by ID."""
    db_log = db_session.query(PracticeBlockLog).filter(PracticeBlockLog.id == log_id).first()
    if db_log is None:
        raise HTTPException(status_code=404, detail="Block log not found")

    update_data = log_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_log, field, value)

    db_session.flush()
    return db_log


@router.delete("/logs/{log_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_block_log(log_id: int, db_session: DBSession = Depends(get_db)) -> None:
    """Delete block log by ID."""
    db_log = db_session.query(PracticeBlockLog).filter(PracticeBlockLog.id == log_id).first()
    if db_log is None:
        raise HTTPException(status_code=404, detail="Block log not found")

    db_session.delete(db_log)
    db_session.flush()
