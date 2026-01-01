"""
Practice API endpoints.
"""


from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session as DBSession

from ...db.models import Practice, PracticeBlock, PracticeBlockLog
from ..dependencies import get_db
from ..schemas.practices import (
    PracticeBlockCreate,
    PracticeBlockLogCreate,
    PracticeBlockLogResponse,
    PracticeBlockLogUpdate,
    PracticeBlockResponse,
    PracticeBlockUpdate,
    PracticeCreate,
    PracticeResponse,
    PracticeUpdate,
)

router = APIRouter()


# Practice endpoints
@router.post("/", response_model=PracticeResponse, status_code=status.HTTP_201_CREATED)
def create_practice(practice: PracticeCreate, db_session: DBSession = Depends(get_db)) -> Practice:
    """Create a new practice session."""
    db_practice = Practice(**practice.model_dump())
    db_session.add(db_practice)
    db_session.flush()
    return db_practice


@router.get("/", response_model=list[PracticeResponse])
def list_practices(db_session: DBSession = Depends(get_db), skip: int = 0, limit: int = 100) -> list[Practice]:
    """List all practices."""
    return db_session.query(Practice).offset(skip).limit(limit).all()


@router.get("/{practice_id}", response_model=PracticeResponse)
def get_practice(practice_id: int, db_session: DBSession = Depends(get_db)) -> Practice:
    """Get practice by ID."""
    practice = db_session.query(Practice).filter(Practice.id == practice_id).first()
    if practice is None:
        raise HTTPException(status_code=404, detail="Practice not found")
    return practice


@router.put("/{practice_id}", response_model=PracticeResponse)
def update_practice(
    practice_id: int, practice_update: PracticeUpdate, db_session: DBSession = Depends(get_db)
) -> Practice:
    """Update practice by ID."""
    db_practice = db_session.query(Practice).filter(Practice.id == practice_id).first()
    if db_practice is None:
        raise HTTPException(status_code=404, detail="Practice not found")

    update_data = practice_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_practice, field, value)

    db_session.flush()
    return db_practice


@router.delete("/{practice_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_practice(practice_id: int, db_session: DBSession = Depends(get_db)) -> None:
    """Delete practice by ID."""
    db_practice = db_session.query(Practice).filter(Practice.id == practice_id).first()
    if db_practice is None:
        raise HTTPException(status_code=404, detail="Practice not found")

    db_session.delete(db_practice)
    db_session.flush()


# Practice block endpoints
@router.post("/blocks/", response_model=PracticeBlockResponse, status_code=status.HTTP_201_CREATED)
def create_practice_block(block: PracticeBlockCreate, db_session: DBSession = Depends(get_db)) -> PracticeBlock:
    """Create a new practice block."""
    db_block = PracticeBlock(**block.model_dump())
    db_session.add(db_block)
    db_session.flush()
    return db_block


@router.get("/blocks/", response_model=list[PracticeBlockResponse])
def list_practice_blocks(
    db_session: DBSession = Depends(get_db), skip: int = 0, limit: int = 100
) -> list[PracticeBlock]:
    """List all practice blocks."""
    return db_session.query(PracticeBlock).offset(skip).limit(limit).all()


@router.get("/blocks/{block_id}", response_model=PracticeBlockResponse)
def get_practice_block(block_id: int, db_session: DBSession = Depends(get_db)) -> PracticeBlock:
    """Get practice block by ID."""
    block = db_session.query(PracticeBlock).filter(PracticeBlock.id == block_id).first()
    if block is None:
        raise HTTPException(status_code=404, detail="Practice block not found")
    return block


@router.put("/blocks/{block_id}", response_model=PracticeBlockResponse)
def update_practice_block(
    block_id: int, block_update: PracticeBlockUpdate, db_session: DBSession = Depends(get_db)
) -> PracticeBlock:
    """Update practice block by ID."""
    db_block = db_session.query(PracticeBlock).filter(PracticeBlock.id == block_id).first()
    if db_block is None:
        raise HTTPException(status_code=404, detail="Practice block not found")

    update_data = block_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_block, field, value)

    db_session.flush()
    return db_block


@router.delete("/blocks/{block_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_practice_block(block_id: int, db_session: DBSession = Depends(get_db)) -> None:
    """Delete practice block by ID."""
    db_block = db_session.query(PracticeBlock).filter(PracticeBlock.id == block_id).first()
    if db_block is None:
        raise HTTPException(status_code=404, detail="Practice block not found")

    db_session.delete(db_block)
    db_session.flush()


# Practice block log endpoints
@router.post("/logs/", response_model=PracticeBlockLogResponse, status_code=status.HTTP_201_CREATED)
def create_practice_block_log(
    log: PracticeBlockLogCreate, db_session: DBSession = Depends(get_db)
) -> PracticeBlockLog:
    """Create a new practice block log."""
    db_log = PracticeBlockLog(**log.model_dump())
    db_session.add(db_log)
    db_session.flush()
    return db_log


@router.get("/logs/", response_model=list[PracticeBlockLogResponse])
def list_practice_block_logs(
    db_session: DBSession = Depends(get_db), skip: int = 0, limit: int = 100
) -> list[PracticeBlockLog]:
    """List all practice block logs."""
    return db_session.query(PracticeBlockLog).offset(skip).limit(limit).all()


@router.get("/logs/{log_id}", response_model=PracticeBlockLogResponse)
def get_practice_block_log(log_id: int, db_session: DBSession = Depends(get_db)) -> PracticeBlockLog:
    """Get practice block log by ID."""
    log = db_session.query(PracticeBlockLog).filter(PracticeBlockLog.id == log_id).first()
    if log is None:
        raise HTTPException(status_code=404, detail="Practice block log not found")
    return log


@router.put("/logs/{log_id}", response_model=PracticeBlockLogResponse)
def update_practice_block_log(
    log_id: int, log_update: PracticeBlockLogUpdate, db_session: DBSession = Depends(get_db)
) -> PracticeBlockLog:
    """Update practice block log by ID."""
    db_log = db_session.query(PracticeBlockLog).filter(PracticeBlockLog.id == log_id).first()
    if db_log is None:
        raise HTTPException(status_code=404, detail="Practice block log not found")

    update_data = log_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_log, field, value)

    db_session.flush()
    return db_log


@router.delete("/logs/{log_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_practice_block_log(log_id: int, db_session: DBSession = Depends(get_db)) -> None:
    """Delete practice block log by ID."""
    db_log = db_session.query(PracticeBlockLog).filter(PracticeBlockLog.id == log_id).first()
    if db_log is None:
        raise HTTPException(status_code=404, detail="Practice block log not found")

    db_session.delete(db_log)
    db_session.flush()
