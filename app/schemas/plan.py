import uuid
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


# --- WorkoutPlan ---

class WorkoutPlanCreate(BaseModel):
    name: str
    description: Optional[str] = None
    num_days: int


class WorkoutPlanUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    num_days: Optional[int] = None


# --- PlanDay ---

class PlanDayCreate(BaseModel):
    day_number: int
    name: Optional[str] = None


class PlanDayUpdate(BaseModel):
    day_number: Optional[int] = None
    name: Optional[str] = None


# --- PlanDayExercise ---

class PlanDayExerciseCreate(BaseModel):
    exercise_id: uuid.UUID
    display_order: int
    prescribed_sets: int
    prescribed_reps: int


class PlanDayExerciseUpdate(BaseModel):
    display_order: Optional[int] = None
    prescribed_sets: Optional[int] = None
    prescribed_reps: Optional[int] = None


# --- Responses ---

class PlanDayExerciseResponse(BaseModel):
    id: uuid.UUID
    exercise_id: uuid.UUID
    display_order: int
    prescribed_sets: int
    prescribed_reps: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class PlanDayResponse(BaseModel):
    id: uuid.UUID
    plan_id: uuid.UUID
    day_number: int
    name: Optional[str] = None
    exercises: List[PlanDayExerciseResponse] = []
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class WorkoutPlanResponse(BaseModel):
    id: uuid.UUID
    name: str
    description: Optional[str] = None
    num_days: int
    owner_id: Optional[uuid.UUID] = None
    sharing_scope: str
    days: List[PlanDayResponse] = []
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
