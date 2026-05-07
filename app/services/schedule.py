import uuid
from datetime import date, timedelta
from typing import List, Optional

from sqlalchemy.orm import Session

from app.exceptions import ConflictError, NotFoundError
from app.models.plan import PlanDay, PlanDayExercise, WorkoutPlan
from app.models.inventory import Exercise
from app.models.schedule import Schedule
from app.models.user import User

MAX_WORKOUTS_PER_DAY = 2


def _count_on_date(db: Session, user_id: uuid.UUID, d: date) -> int:
    """Count how many workouts a user has scheduled on a given date."""
    return db.query(Schedule).filter(
        Schedule.user_id == user_id,
        Schedule.scheduled_date == d,
    ).count()


def _check_date_limit(db: Session, user_id: uuid.UUID, d: date, force: bool):
    """Enforce the max-2-per-day rule with force override for the 2nd."""
    count = _count_on_date(db, user_id, d)
    if count >= MAX_WORKOUTS_PER_DAY:
        raise ConflictError(
            f"Maximum {MAX_WORKOUTS_PER_DAY} workouts per day reached for {d}"
        )
    if count == 1 and not force:
        raise ConflictError(
            f"You already have a workout planned for {d}. "
            f"Set force=true to add a second workout."
        )


def assign_plan_to_dates(
    db: Session, plan_id: uuid.UUID, start_date: date,
    user: User, force: bool = False,
) -> List[Schedule]:
    """Assign a full plan across consecutive dates starting from start_date."""
    plan = db.query(WorkoutPlan).filter(WorkoutPlan.id == plan_id).first()
    if not plan:
        raise NotFoundError("Workout plan not found")

    days = (
        db.query(PlanDay)
        .filter(PlanDay.plan_id == plan_id)
        .order_by(PlanDay.day_number)
        .all()
    )
    if not days:
        raise NotFoundError("Workout plan has no days")

    entries = []
    for i, day in enumerate(days):
        d = start_date + timedelta(days=i)
        _check_date_limit(db, user.id, d, force)
        entry = Schedule(
            user_id=user.id,
            plan_day_id=day.id,
            plan_id=plan_id,
            scheduled_date=d,
        )
        db.add(entry)
        entries.append(entry)

    db.flush()
    return entries


def assign_single_day(
    db: Session, plan_day_id: uuid.UUID, plan_id: uuid.UUID,
    scheduled_date: date, user: User, force: bool = False,
) -> Schedule:
    """Assign a single plan day to a specific date."""
    day = db.query(PlanDay).filter(PlanDay.id == plan_day_id).first()
    if not day:
        raise NotFoundError("Plan day not found")

    _check_date_limit(db, user.id, scheduled_date, force)

    entry = Schedule(
        user_id=user.id,
        plan_day_id=plan_day_id,
        plan_id=plan_id,
        scheduled_date=scheduled_date,
    )
    db.add(entry)
    db.flush()
    return entry


def update_schedule(
    db: Session, schedule_id: uuid.UUID, user: User,
    scheduled_date: date = None, plan_day_id: uuid.UUID = None,
) -> Schedule:
    entry = db.query(Schedule).filter(
        Schedule.id == schedule_id, Schedule.user_id == user.id,
    ).first()
    if not entry:
        raise NotFoundError("Schedule entry not found")
    if scheduled_date is not None:
        entry.scheduled_date = scheduled_date
    if plan_day_id is not None:
        entry.plan_day_id = plan_day_id
    db.flush()
    return entry


def delete_schedule(db: Session, schedule_id: uuid.UUID, user: User):
    entry = db.query(Schedule).filter(
        Schedule.id == schedule_id, Schedule.user_id == user.id,
    ).first()
    if not entry:
        raise NotFoundError("Schedule entry not found")
    db.delete(entry)
    db.flush()


def get_schedule_range(
    db: Session, user: User, start: date, end: date,
) -> List[Schedule]:
    """Return all schedule entries within a date range (inclusive)."""
    return (
        db.query(Schedule)
        .filter(
            Schedule.user_id == user.id,
            Schedule.scheduled_date >= start,
            Schedule.scheduled_date <= end,
        )
        .order_by(Schedule.scheduled_date)
        .all()
    )


def get_today_workout(db: Session, user: User) -> List[dict]:
    """Return today's scheduled workouts with full exercise details."""
    from datetime import date as date_type
    today = date_type.today()

    entries = (
        db.query(Schedule)
        .filter(Schedule.user_id == user.id, Schedule.scheduled_date == today)
        .all()
    )
    if not entries:
        return []

    results = []
    for entry in entries:
        day = db.query(PlanDay).filter(PlanDay.id == entry.plan_day_id).first()
        plan = db.query(WorkoutPlan).filter(WorkoutPlan.id == entry.plan_id).first()
        exercises = _get_day_exercises(db, day.id)
        results.append({
            "schedule_id": entry.id,
            "plan_name": plan.name if plan else "",
            "plan_day_name": day.name if day else None,
            "day_number": day.day_number if day else 0,
            "exercises": exercises,
        })
    return results


def get_plan_day_detail(db: Session, day_id: uuid.UUID) -> dict:
    """Return a plan day with all exercises in prescribed order."""
    day = db.query(PlanDay).filter(PlanDay.id == day_id).first()
    if not day:
        raise NotFoundError("Plan day not found")
    plan = db.query(WorkoutPlan).filter(WorkoutPlan.id == day.plan_id).first()
    exercises = _get_day_exercises(db, day_id)
    return {
        "schedule_id": None,
        "plan_name": plan.name if plan else "",
        "plan_day_name": day.name,
        "day_number": day.day_number,
        "exercises": exercises,
    }


def _get_day_exercises(db: Session, day_id: uuid.UUID) -> List[dict]:
    """Fetch exercises for a plan day in display order."""
    pdes = (
        db.query(PlanDayExercise)
        .filter(PlanDayExercise.plan_day_id == day_id)
        .order_by(PlanDayExercise.display_order)
        .all()
    )
    exercises = []
    for pde in pdes:
        ex = db.query(Exercise).filter(Exercise.id == pde.exercise_id).first()
        exercises.append({
            "exercise_id": pde.exercise_id,
            "name": ex.name if ex else "",
            "target_muscles": ex.target_muscles if ex else None,
            "display_order": pde.display_order,
            "prescribed_sets": pde.prescribed_sets,
            "prescribed_reps": pde.prescribed_reps,
        })
    return exercises
