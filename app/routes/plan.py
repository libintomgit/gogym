import uuid
from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.dependencies import get_db, get_current_user
from app.models.user import User
from app.schemas.plan import (
    WorkoutPlanCreate, WorkoutPlanUpdate, WorkoutPlanResponse,
    PlanDayCreate, PlanDayUpdate, PlanDayResponse,
    PlanDayExerciseCreate, PlanDayExerciseUpdate, PlanDayExerciseResponse,
)
from app.services import plan as plan_service

router = APIRouter(prefix="/plans", tags=["plans"])


# --- WorkoutPlan ---

@router.get("", response_model=List[WorkoutPlanResponse])
def list_plans(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return plan_service.list_plans(db, user)


@router.post("", response_model=WorkoutPlanResponse, status_code=201)
def create_plan(
    request: WorkoutPlanCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return plan_service.create_plan(
        db, request.name, request.description, request.num_days, user,
    )


@router.get("/{plan_id}", response_model=WorkoutPlanResponse)
def get_plan(
    plan_id: uuid.UUID,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return plan_service.get_plan(db, plan_id, user)


@router.put("/{plan_id}", response_model=WorkoutPlanResponse)
def update_plan(
    plan_id: uuid.UUID,
    request: WorkoutPlanUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return plan_service.update_plan(
        db, plan_id, user, request.name, request.description, request.num_days,
    )


@router.delete("/{plan_id}", status_code=204)
def delete_plan(
    plan_id: uuid.UUID,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    plan_service.delete_plan(db, plan_id, user)


# --- PlanDay ---

@router.post("/{plan_id}/days", response_model=PlanDayResponse, status_code=201)
def create_plan_day(
    plan_id: uuid.UUID,
    request: PlanDayCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return plan_service.create_plan_day(
        db, plan_id, request.day_number, request.name, user,
    )


@router.put("/{plan_id}/days/{day_id}", response_model=PlanDayResponse)
def update_plan_day(
    plan_id: uuid.UUID,
    day_id: uuid.UUID,
    request: PlanDayUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return plan_service.update_plan_day(
        db, plan_id, day_id, user, request.day_number, request.name,
    )


@router.delete("/{plan_id}/days/{day_id}", status_code=204)
def delete_plan_day(
    plan_id: uuid.UUID,
    day_id: uuid.UUID,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    plan_service.delete_plan_day(db, plan_id, day_id, user)


# --- PlanDayExercise ---

@router.post("/days/{day_id}/exercises", response_model=PlanDayExerciseResponse, status_code=201)
def add_exercise_to_day(
    day_id: uuid.UUID,
    request: PlanDayExerciseCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return plan_service.add_exercise_to_day(
        db, day_id, request.exercise_id, request.display_order,
        request.prescribed_sets, request.prescribed_reps, user,
    )


@router.put("/day-exercises/{pde_id}", response_model=PlanDayExerciseResponse)
def update_day_exercise(
    pde_id: uuid.UUID,
    request: PlanDayExerciseUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return plan_service.update_day_exercise(
        db, pde_id, user, request.display_order,
        request.prescribed_sets, request.prescribed_reps,
    )


@router.delete("/day-exercises/{pde_id}", status_code=204)
def delete_day_exercise(
    pde_id: uuid.UUID,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    plan_service.delete_day_exercise(db, pde_id, user)
