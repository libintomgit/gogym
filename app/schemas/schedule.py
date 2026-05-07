import uuid
from datetime import date, datetime
from typing import List, Optional

from pydantic import BaseModel


class ScheduleCreateSingle(BaseModel):
    plan_day_id: uuid.UUID
    plan_id: uuid.UUID
    scheduled_date: date
    force: bool = False  # set True to allow a 2nd workout on the same day


class ScheduleCreatePlan(BaseModel):
    plan_id: uuid.UUID
    start_date: date
    force: bool = False


class ScheduleUpdate(BaseModel):
    scheduled_date: Optional[date] = None
    plan_day_id: Optional[uuid.UUID] = None


class ScheduleResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    plan_day_id: uuid.UUID
    plan_id: uuid.UUID
    scheduled_date: date
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class DailyExerciseDetail(BaseModel):
    exercise_id: uuid.UUID
    name: str
    target_muscles: Optional[str] = None
    display_order: int
    prescribed_sets: int
    prescribed_reps: int


class DailyWorkoutResponse(BaseModel):
    schedule_id: uuid.UUID
    plan_name: str
    plan_day_name: Optional[str] = None
    day_number: int
    exercises: List[DailyExerciseDetail] = []
