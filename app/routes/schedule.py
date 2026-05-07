import uuid
from datetime import date
from typing import List, Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.dependencies import get_db, get_current_user
from app.models.user import User
from app.schemas.schedule import (
    ScheduleCreateSingle, ScheduleCreatePlan, ScheduleUpdate,
    ScheduleResponse, DailyWorkoutResponse,
)
from app.services import schedule as schedule_service

router = APIRouter(prefix="/schedule", tags=["schedule"])


@router.get("", response_model=List[ScheduleResponse])
def get_schedule(
    start_date: date = Query(...),
    end_date: date = Query(...),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return schedule_service.get_schedule_range(db, user, start_date, end_date)


@router.post("", response_model=ScheduleResponse, status_code=201)
def assign_single_day(
    request: ScheduleCreateSingle,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return schedule_service.assign_single_day(
        db, request.plan_day_id, request.plan_id,
        request.scheduled_date, user, request.force,
    )


@router.post("/plan", response_model=List[ScheduleResponse], status_code=201)
def assign_plan_to_dates(
    request: ScheduleCreatePlan,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return schedule_service.assign_plan_to_dates(
        db, request.plan_id, request.start_date, user, request.force,
    )


@router.put("/{schedule_id}", response_model=ScheduleResponse)
def update_schedule(
    schedule_id: uuid.UUID,
    request: ScheduleUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return schedule_service.update_schedule(
        db, schedule_id, user, request.scheduled_date, request.plan_day_id,
    )


@router.delete("/{schedule_id}", status_code=204)
def delete_schedule(
    schedule_id: uuid.UUID,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    schedule_service.delete_schedule(db, schedule_id, user)


@router.get("/today", response_model=List[DailyWorkoutResponse])
def get_today_workout(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return schedule_service.get_today_workout(db, user)


@router.get("/days/{day_id}", response_model=DailyWorkoutResponse)
def get_plan_day_detail(
    day_id: uuid.UUID,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return schedule_service.get_plan_day_detail(db, day_id)
