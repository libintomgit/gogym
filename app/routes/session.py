import uuid
from typing import List

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.dependencies import get_db, get_current_user
from app.models.user import User
from app.schemas.session import (
    SessionStartRequest, SetLogCreate, SetLogResponse,
    SessionResponse, SessionListResponse,
    ExerciseProgressResponse,
)
from app.services import session as session_service

router = APIRouter(prefix="/sessions", tags=["sessions"])


@router.post("", response_model=SessionResponse, status_code=201)
def start_session(
    request: SessionStartRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return session_service.start_session(
        db, request.plan_day_id, request.session_date, user,
    )


@router.post("/{session_id}/sets", response_model=SetLogResponse, status_code=201)
def log_set(
    session_id: uuid.UUID,
    request: SetLogCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return session_service.log_set(
        db, session_id, request.exercise_id, request.set_number,
        request.reps_performed, request.weight, user,
    )


@router.put("/{session_id}/complete", response_model=SessionResponse)
def complete_session(
    session_id: uuid.UUID,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return session_service.complete_session(db, session_id, user)


@router.put("/{session_id}/end", response_model=SessionResponse)
def end_session_early(
    session_id: uuid.UUID,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return session_service.end_session_early(db, session_id, user)


@router.get("", response_model=SessionListResponse)
def get_session_history(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return session_service.get_session_history(db, user, page, page_size)


@router.get("/{session_id}", response_model=SessionResponse)
def get_session_detail(
    session_id: uuid.UUID,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return session_service.get_session_detail(db, session_id, user)


@router.get("/exercises/{exercise_id}/history", response_model=ExerciseProgressResponse)
def get_exercise_progress(
    exercise_id: uuid.UUID,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    history = session_service.get_exercise_progress(db, exercise_id, user)
    return {"exercise_id": exercise_id, "history": history}


@router.get("/exercises/{exercise_id}/previous", response_model=List[SetLogResponse])
def get_previous_performance(
    exercise_id: uuid.UUID,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return session_service.get_previous_performance(db, exercise_id, user)
