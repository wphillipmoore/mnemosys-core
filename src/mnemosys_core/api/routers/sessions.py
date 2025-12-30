"""
Session API endpoints.
"""


from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session as DBSession

from ...db.models import BlockLog, Session, SessionBlock
from ..dependencies import get_db
from ..schemas.sessions import (
    BlockLogCreate,
    BlockLogResponse,
    BlockLogUpdate,
    SessionBlockCreate,
    SessionBlockResponse,
    SessionBlockUpdate,
    SessionCreate,
    SessionResponse,
    SessionUpdate,
)

router = APIRouter()


# Session endpoints
@router.post("/", response_model=SessionResponse, status_code=status.HTTP_201_CREATED)
def create_session(session: SessionCreate, db_session: DBSession = Depends(get_db)) -> Session:
    """Create a new practice session."""
    db_session_obj = Session(**session.model_dump())
    db_session.add(db_session_obj)
    db_session.flush()
    return db_session_obj


@router.get("/", response_model=list[SessionResponse])
def list_sessions(db_session: DBSession = Depends(get_db), skip: int = 0, limit: int = 100) -> list[Session]:
    """List all sessions."""
    return db_session.query(Session).offset(skip).limit(limit).all()


@router.get("/{session_id}", response_model=SessionResponse)
def get_session(session_id: int, db_session: DBSession = Depends(get_db)) -> Session:
    """Get session by ID."""
    session = db_session.query(Session).filter(Session.id == session_id).first()
    if session is None:
        raise HTTPException(status_code=404, detail="Session not found")
    return session


@router.put("/{session_id}", response_model=SessionResponse)
def update_session(
    session_id: int, session_update: SessionUpdate, db_session: DBSession = Depends(get_db)
) -> Session:
    """Update session by ID."""
    db_session_obj = db_session.query(Session).filter(Session.id == session_id).first()
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
    db_session_obj = db_session.query(Session).filter(Session.id == session_id).first()
    if db_session_obj is None:
        raise HTTPException(status_code=404, detail="Session not found")

    db_session.delete(db_session_obj)
    db_session.flush()


# Session block endpoints
@router.post("/blocks/", response_model=SessionBlockResponse, status_code=status.HTTP_201_CREATED)
def create_session_block(block: SessionBlockCreate, db_session: DBSession = Depends(get_db)) -> SessionBlock:
    """Create a new session block."""
    db_block = SessionBlock(**block.model_dump())
    db_session.add(db_block)
    db_session.flush()
    return db_block


@router.get("/blocks/", response_model=list[SessionBlockResponse])
def list_session_blocks(
    db_session: DBSession = Depends(get_db), skip: int = 0, limit: int = 100
) -> list[SessionBlock]:
    """List all session blocks."""
    return db_session.query(SessionBlock).offset(skip).limit(limit).all()


@router.get("/blocks/{block_id}", response_model=SessionBlockResponse)
def get_session_block(block_id: int, db_session: DBSession = Depends(get_db)) -> SessionBlock:
    """Get session block by ID."""
    block = db_session.query(SessionBlock).filter(SessionBlock.id == block_id).first()
    if block is None:
        raise HTTPException(status_code=404, detail="Session block not found")
    return block


@router.put("/blocks/{block_id}", response_model=SessionBlockResponse)
def update_session_block(
    block_id: int, block_update: SessionBlockUpdate, db_session: DBSession = Depends(get_db)
) -> SessionBlock:
    """Update session block by ID."""
    db_block = db_session.query(SessionBlock).filter(SessionBlock.id == block_id).first()
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
    db_block = db_session.query(SessionBlock).filter(SessionBlock.id == block_id).first()
    if db_block is None:
        raise HTTPException(status_code=404, detail="Session block not found")

    db_session.delete(db_block)
    db_session.flush()


# Block log endpoints
@router.post("/logs/", response_model=BlockLogResponse, status_code=status.HTTP_201_CREATED)
def create_block_log(log: BlockLogCreate, db_session: DBSession = Depends(get_db)) -> BlockLog:
    """Create a new block log."""
    db_log = BlockLog(**log.model_dump())
    db_session.add(db_log)
    db_session.flush()
    return db_log


@router.get("/logs/", response_model=list[BlockLogResponse])
def list_block_logs(db_session: DBSession = Depends(get_db), skip: int = 0, limit: int = 100) -> list[BlockLog]:
    """List all block logs."""
    return db_session.query(BlockLog).offset(skip).limit(limit).all()


@router.get("/logs/{log_id}", response_model=BlockLogResponse)
def get_block_log(log_id: int, db_session: DBSession = Depends(get_db)) -> BlockLog:
    """Get block log by ID."""
    log = db_session.query(BlockLog).filter(BlockLog.id == log_id).first()
    if log is None:
        raise HTTPException(status_code=404, detail="Block log not found")
    return log


@router.put("/logs/{log_id}", response_model=BlockLogResponse)
def update_block_log(log_id: int, log_update: BlockLogUpdate, db_session: DBSession = Depends(get_db)) -> BlockLog:
    """Update block log by ID."""
    db_log = db_session.query(BlockLog).filter(BlockLog.id == log_id).first()
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
    db_log = db_session.query(BlockLog).filter(BlockLog.id == log_id).first()
    if db_log is None:
        raise HTTPException(status_code=404, detail="Block log not found")

    db_session.delete(db_log)
    db_session.flush()
