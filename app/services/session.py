import uuid
from datetime import date, datetime
from decimal import Decimal
from typing import List

from sqlalchemy.orm import Session

from app.exceptions import NotFoundError
from app.models.session import WorkoutSession, SetLog
from app.models.user import User


def start_session(
    db: Session, plan_day_id: uuid.UUID, session_date: date, user: User,
) -> WorkoutSession:
    """Create a new in-progress workout session."""
    ws = WorkoutSession(
        user_id=user.id,
        plan_day_id=plan_day_id,
        session_date=session_date,
        status="in_progress",
        started_at=datetime.utcnow(),
    )
    db.add(ws)
    db.flush()
    return ws


def log_set(
    db: Session, session_id: uuid.UUID, exercise_id: uuid.UUID,
    set_number: int, reps_performed: int, weight: Decimal, user: User,
) -> SetLog:
    """Log a single set for an exercise in a session."""
    ws = db.query(WorkoutSession).filter(
        WorkoutSession.id == session_id, WorkoutSession.user_id == user.id,
    ).first()
    if not ws:
        raise NotFoundError("Workout session not found")

    sl = SetLog(
        session_id=session_id,
        exercise_id=exercise_id,
        set_number=set_number,
        reps_performed=reps_performed,
        weight=weight,
    )
    db.add(sl)
    db.flush()
    return sl


def complete_session(db: Session, session_id: uuid.UUID, user: User) -> WorkoutSession:
    """Mark a session as completed."""
    ws = db.query(WorkoutSession).filter(
        WorkoutSession.id == session_id, WorkoutSession.user_id == user.id,
    ).first()
    if not ws:
        raise NotFoundError("Workout session not found")
    ws.status = "completed"
    ws.completed_at = datetime.utcnow()
    db.flush()
    return ws


def end_session_early(db: Session, session_id: uuid.UUID, user: User) -> WorkoutSession:
    """End a session early, marking it as partial."""
    ws = db.query(WorkoutSession).filter(
        WorkoutSession.id == session_id, WorkoutSession.user_id == user.id,
    ).first()
    if not ws:
        raise NotFoundError("Workout session not found")
    ws.status = "partial"
    ws.completed_at = datetime.utcnow()
    db.flush()
    return ws


def get_session_detail(db: Session, session_id: uuid.UUID, user: User) -> WorkoutSession:
    """Get a session with all its set logs."""
    ws = db.query(WorkoutSession).filter(
        WorkoutSession.id == session_id, WorkoutSession.user_id == user.id,
    ).first()
    if not ws:
        raise NotFoundError("Workout session not found")
    return ws


def get_session_history(
    db: Session, user: User, page: int = 1, page_size: int = 20,
) -> dict:
    """Get paginated workout history in reverse chronological order."""
    q = db.query(WorkoutSession).filter(
        WorkoutSession.user_id == user.id,
        WorkoutSession.status.in_(["completed", "partial"]),
    ).order_by(WorkoutSession.session_date.desc())

    total = q.count()
    items = q.offset((page - 1) * page_size).limit(page_size).all()

    return {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size,
    }


def get_previous_performance(
    db: Session, exercise_id: uuid.UUID, user: User,
) -> List[SetLog]:
    """Return SetLogs from the most recent past session for an exercise."""
    # Find the most recent session that has logs for this exercise
    latest_log = (
        db.query(SetLog)
        .join(WorkoutSession)
        .filter(
            WorkoutSession.user_id == user.id,
            SetLog.exercise_id == exercise_id,
            WorkoutSession.status.in_(["completed", "partial"]),
        )
        .order_by(WorkoutSession.session_date.desc())
        .first()
    )
    if not latest_log:
        return []

    # Get all logs from that session for this exercise
    return (
        db.query(SetLog)
        .filter(
            SetLog.session_id == latest_log.session_id,
            SetLog.exercise_id == exercise_id,
        )
        .order_by(SetLog.set_number)
        .all()
    )


def get_exercise_progress(
    db: Session, exercise_id: uuid.UUID, user: User,
) -> List[dict]:
    """Return weight history for an exercise across all sessions."""
    logs = (
        db.query(SetLog)
        .join(WorkoutSession)
        .filter(
            WorkoutSession.user_id == user.id,
            SetLog.exercise_id == exercise_id,
            WorkoutSession.status.in_(["completed", "partial"]),
        )
        .order_by(WorkoutSession.session_date.asc(), SetLog.set_number.asc())
        .all()
    )

    history = []
    for log in logs:
        session = db.query(WorkoutSession).filter(
            WorkoutSession.id == log.session_id
        ).first()
        history.append({
            "session_date": session.session_date,
            "weight": log.weight,
            "reps_performed": log.reps_performed,
            "set_number": log.set_number,
        })
    return history
