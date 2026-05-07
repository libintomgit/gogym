import uuid
from typing import List

from sqlalchemy.orm import Session

from app.exceptions import ForbiddenError, NotFoundError
from app.models.plan import WorkoutPlan, PlanDay, PlanDayExercise
from app.models.sharing import SharedItem
from app.models.user import User


# --- Helpers ---

def _check_ownership(resource, user: User):
    """Allow if user is admin or owns the resource."""
    if user.role == "admin":
        return
    if resource.owner_id != user.id:
        raise ForbiddenError()


def _visible_plan_filter(query, user: User):
    """Return global + user's own + shared-with-user plans."""
    shared_ids = [
        row.item_id
        for row in query.session.query(SharedItem.item_id)
        .filter(
            SharedItem.shared_with_user_id == user.id,
            SharedItem.item_type == "workout_plan",
        )
        .all()
    ]

    if shared_ids:
        return query.filter(
            (WorkoutPlan.sharing_scope == "global")
            | (WorkoutPlan.owner_id == user.id)
            | (WorkoutPlan.id.in_(shared_ids))
        )
    return query.filter(
        (WorkoutPlan.sharing_scope == "global")
        | (WorkoutPlan.owner_id == user.id)
    )


# --- WorkoutPlan ---

def list_plans(db: Session, user: User) -> List[WorkoutPlan]:
    q = db.query(WorkoutPlan)
    return _visible_plan_filter(q, user).all()


def get_plan(db: Session, plan_id: uuid.UUID, user: User) -> WorkoutPlan:
    plan = db.query(WorkoutPlan).filter(WorkoutPlan.id == plan_id).first()
    if not plan:
        raise NotFoundError("Workout plan not found")
    return plan


def create_plan(
    db: Session, name: str, description: str, num_days: int, user: User,
) -> WorkoutPlan:
    scope = "global" if user.role == "admin" else "private"
    plan = WorkoutPlan(
        name=name,
        description=description,
        num_days=num_days,
        owner_id=user.id,
        sharing_scope=scope,
    )
    db.add(plan)
    db.flush()
    return plan


def update_plan(
    db: Session, plan_id: uuid.UUID, user: User,
    name: str = None, description: str = None, num_days: int = None,
) -> WorkoutPlan:
    plan = db.query(WorkoutPlan).filter(WorkoutPlan.id == plan_id).first()
    if not plan:
        raise NotFoundError("Workout plan not found")
    _check_ownership(plan, user)
    if name is not None:
        plan.name = name
    if description is not None:
        plan.description = description
    if num_days is not None:
        plan.num_days = num_days
    db.flush()
    return plan


def delete_plan(db: Session, plan_id: uuid.UUID, user: User):
    plan = db.query(WorkoutPlan).filter(WorkoutPlan.id == plan_id).first()
    if not plan:
        raise NotFoundError("Workout plan not found")
    _check_ownership(plan, user)
    db.delete(plan)
    db.flush()


# --- PlanDay ---

def create_plan_day(
    db: Session, plan_id: uuid.UUID, day_number: int, name: str, user: User,
) -> PlanDay:
    plan = db.query(WorkoutPlan).filter(WorkoutPlan.id == plan_id).first()
    if not plan:
        raise NotFoundError("Workout plan not found")
    _check_ownership(plan, user)
    day = PlanDay(plan_id=plan_id, day_number=day_number, name=name)
    db.add(day)
    db.flush()
    return day


def update_plan_day(
    db: Session, plan_id: uuid.UUID, day_id: uuid.UUID, user: User,
    day_number: int = None, name: str = None,
) -> PlanDay:
    plan = db.query(WorkoutPlan).filter(WorkoutPlan.id == plan_id).first()
    if not plan:
        raise NotFoundError("Workout plan not found")
    _check_ownership(plan, user)
    day = db.query(PlanDay).filter(
        PlanDay.id == day_id, PlanDay.plan_id == plan_id
    ).first()
    if not day:
        raise NotFoundError("Plan day not found")
    if day_number is not None:
        day.day_number = day_number
    if name is not None:
        day.name = name
    db.flush()
    return day


def delete_plan_day(
    db: Session, plan_id: uuid.UUID, day_id: uuid.UUID, user: User,
):
    plan = db.query(WorkoutPlan).filter(WorkoutPlan.id == plan_id).first()
    if not plan:
        raise NotFoundError("Workout plan not found")
    _check_ownership(plan, user)
    day = db.query(PlanDay).filter(
        PlanDay.id == day_id, PlanDay.plan_id == plan_id
    ).first()
    if not day:
        raise NotFoundError("Plan day not found")
    db.delete(day)
    db.flush()


# --- PlanDayExercise ---

def add_exercise_to_day(
    db: Session, day_id: uuid.UUID, exercise_id: uuid.UUID,
    display_order: int, prescribed_sets: int, prescribed_reps: int,
    user: User,
) -> PlanDayExercise:
    day = db.query(PlanDay).filter(PlanDay.id == day_id).first()
    if not day:
        raise NotFoundError("Plan day not found")
    plan = db.query(WorkoutPlan).filter(WorkoutPlan.id == day.plan_id).first()
    _check_ownership(plan, user)
    pde = PlanDayExercise(
        plan_day_id=day_id,
        exercise_id=exercise_id,
        display_order=display_order,
        prescribed_sets=prescribed_sets,
        prescribed_reps=prescribed_reps,
    )
    db.add(pde)
    db.flush()
    return pde


def update_day_exercise(
    db: Session, pde_id: uuid.UUID, user: User,
    display_order: int = None, prescribed_sets: int = None,
    prescribed_reps: int = None,
) -> PlanDayExercise:
    pde = db.query(PlanDayExercise).filter(PlanDayExercise.id == pde_id).first()
    if not pde:
        raise NotFoundError("Plan day exercise not found")
    day = db.query(PlanDay).filter(PlanDay.id == pde.plan_day_id).first()
    plan = db.query(WorkoutPlan).filter(WorkoutPlan.id == day.plan_id).first()
    _check_ownership(plan, user)
    if display_order is not None:
        pde.display_order = display_order
    if prescribed_sets is not None:
        pde.prescribed_sets = prescribed_sets
    if prescribed_reps is not None:
        pde.prescribed_reps = prescribed_reps
    db.flush()
    return pde


def delete_day_exercise(db: Session, pde_id: uuid.UUID, user: User):
    pde = db.query(PlanDayExercise).filter(PlanDayExercise.id == pde_id).first()
    if not pde:
        raise NotFoundError("Plan day exercise not found")
    day = db.query(PlanDay).filter(PlanDay.id == pde.plan_day_id).first()
    plan = db.query(WorkoutPlan).filter(WorkoutPlan.id == day.plan_id).first()
    _check_ownership(plan, user)
    db.delete(pde)
    db.flush()
