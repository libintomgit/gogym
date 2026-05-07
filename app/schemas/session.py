import uuid
from datetime import date, datetime
from decimal import Decimal
from typing import List, Optional

from pydantic import BaseModel, Field


class SessionStartRequest(BaseModel):
    plan_day_id: uuid.UUID
    session_date: date


class SetLogCreate(BaseModel):
    exercise_id: uuid.UUID
    set_number: int
    reps_performed: int
    weight: Decimal = Field(gt=0, description="Weight must be positive")


class SetLogResponse(BaseModel):
    id: uuid.UUID
    exercise_id: uuid.UUID
    set_number: int
    reps_performed: int
    weight: Decimal
    created_at: datetime

    model_config = {"from_attributes": True}


class SessionResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    plan_day_id: uuid.UUID
    session_date: date
    status: str
    started_at: datetime
    completed_at: Optional[datetime] = None
    set_logs: List[SetLogResponse] = []
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class SessionListResponse(BaseModel):
    items: List[SessionResponse]
    total: int
    page: int
    page_size: int


class ExerciseProgressEntry(BaseModel):
    session_date: date
    weight: Decimal
    reps_performed: int
    set_number: int


class ExerciseProgressResponse(BaseModel):
    exercise_id: uuid.UUID
    history: List[ExerciseProgressEntry]
