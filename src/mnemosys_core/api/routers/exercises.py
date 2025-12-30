"""
Exercise API endpoints.
"""


from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session as DBSession

from ...db.models import Exercise, ExerciseState
from ..dependencies import get_db
from ..schemas.exercises import (
    ExerciseCreate,
    ExerciseResponse,
    ExerciseStateCreate,
    ExerciseStateResponse,
    ExerciseStateUpdate,
    ExerciseUpdate,
)

router = APIRouter()


# Exercise endpoints
@router.post("/", response_model=ExerciseResponse, status_code=status.HTTP_201_CREATED)
def create_exercise(exercise: ExerciseCreate, db_session: DBSession = Depends(get_db)) -> Exercise:
    """Create a new exercise."""
    db_exercise = Exercise(**exercise.model_dump())
    db_session.add(db_exercise)
    db_session.flush()
    return db_exercise


@router.get("/", response_model=list[ExerciseResponse])
def list_exercises(db_session: DBSession = Depends(get_db), skip: int = 0, limit: int = 100) -> list[Exercise]:
    """List all exercises."""
    return db_session.query(Exercise).offset(skip).limit(limit).all()


@router.get("/{exercise_id}", response_model=ExerciseResponse)
def get_exercise(exercise_id: int, db_session: DBSession = Depends(get_db)) -> Exercise:
    """Get exercise by ID."""
    exercise = db_session.query(Exercise).filter(Exercise.id == exercise_id).first()
    if exercise is None:
        raise HTTPException(status_code=404, detail="Exercise not found")
    return exercise


@router.put("/{exercise_id}", response_model=ExerciseResponse)
def update_exercise(
    exercise_id: int, exercise_update: ExerciseUpdate, db_session: DBSession = Depends(get_db)
) -> Exercise:
    """Update exercise by ID."""
    db_exercise = db_session.query(Exercise).filter(Exercise.id == exercise_id).first()
    if db_exercise is None:
        raise HTTPException(status_code=404, detail="Exercise not found")

    update_data = exercise_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_exercise, field, value)

    db_session.flush()
    return db_exercise


@router.delete("/{exercise_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_exercise(exercise_id: int, db_session: DBSession = Depends(get_db)) -> None:
    """Delete exercise by ID."""
    db_exercise = db_session.query(Exercise).filter(Exercise.id == exercise_id).first()
    if db_exercise is None:
        raise HTTPException(status_code=404, detail="Exercise not found")

    db_session.delete(db_exercise)
    db_session.flush()


# Exercise state endpoints
@router.post("/states/", response_model=ExerciseStateResponse, status_code=status.HTTP_201_CREATED)
def create_exercise_state(state: ExerciseStateCreate, db_session: DBSession = Depends(get_db)) -> ExerciseState:
    """Create a new exercise state."""
    db_state = ExerciseState(**state.model_dump())
    db_session.add(db_state)
    db_session.flush()
    return db_state


@router.get("/states/", response_model=list[ExerciseStateResponse])
def list_exercise_states(
    db_session: DBSession = Depends(get_db), skip: int = 0, limit: int = 100
) -> list[ExerciseState]:
    """List all exercise states."""
    return db_session.query(ExerciseState).offset(skip).limit(limit).all()


@router.get("/states/{state_id}", response_model=ExerciseStateResponse)
def get_exercise_state(state_id: int, db_session: DBSession = Depends(get_db)) -> ExerciseState:
    """Get exercise state by ID."""
    state = db_session.query(ExerciseState).filter(ExerciseState.id == state_id).first()
    if state is None:
        raise HTTPException(status_code=404, detail="Exercise state not found")
    return state


@router.put("/states/{state_id}", response_model=ExerciseStateResponse)
def update_exercise_state(
    state_id: int, state_update: ExerciseStateUpdate, db_session: DBSession = Depends(get_db)
) -> ExerciseState:
    """Update exercise state by ID."""
    db_state = db_session.query(ExerciseState).filter(ExerciseState.id == state_id).first()
    if db_state is None:
        raise HTTPException(status_code=404, detail="Exercise state not found")

    update_data = state_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_state, field, value)

    db_session.flush()
    return db_state


@router.delete("/states/{state_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_exercise_state(state_id: int, db_session: DBSession = Depends(get_db)) -> None:
    """Delete exercise state by ID."""
    db_state = db_session.query(ExerciseState).filter(ExerciseState.id == state_id).first()
    if db_state is None:
        raise HTTPException(status_code=404, detail="Exercise state not found")

    db_session.delete(db_state)
    db_session.flush()
