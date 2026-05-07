import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import Enum, ForeignKey, Integer, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

class WorkoutPlan(Base):
    __tablename__ = "workout_plans"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(
        String(150), nullable=False
    )
    description: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True
    )
    num_days: Mapped[int] = mapped_column(
        Integer, nullable=False
    )
    owner_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("users.id"), nullable=True
    )
    sharing_scope: Mapped[str] = mapped_column(
        Enum("private", "shared", "global", name="sharing_scope",
             create_type=False),
        nullable=False,
        default="private",
    )
    approval_status: Mapped[Optional[str]] = mapped_column(
        Enum("pending", "approved", "rejected", name="approval_status",
             create_type=False),
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        nullable=False, server_default=func.now(), onupdate=func.now()
    )

    days = relationship(
        "PlanDay", back_populates="plan", cascade="all, delete-orphan"
    )

class PlanDay(Base):
    __tablename__ = "plan_days"
    __table_args__ = (
        UniqueConstraint("plan_id", "day_number", name="uq_plan_day_number"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, default=uuid.uuid4
    )
    plan_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("workout_plans.id"), nullable=False
    )
    day_number: Mapped[int] = mapped_column(
        Integer, nullable=False
    )
    name: Mapped[Optional[str]] = mapped_column(
        String(100), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        nullable=False, server_default=func.now(), onupdate=func.now()
    )

    plan = relationship("WorkoutPlan", back_populates="days")
    exercises = relationship(
        "PlanDayExercise", back_populates="plan_day",
        cascade="all, delete-orphan"
    )


class PlanDayExercise(Base):
    __tablename__ = "plan_day_exercises"
    __table_args__ = (
        UniqueConstraint("plan_day_id", "display_order",
                         name="uq_plan_day_display_order"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, default=uuid.uuid4
    )
    plan_day_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("plan_days.id"), nullable=False
    )
    exercise_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("exercises.id"), nullable=False
    )
    display_order: Mapped[int] = mapped_column(Integer, nullable=False)
    prescribed_sets: Mapped[int] = mapped_column(Integer, nullable=False)
    prescribed_reps: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        nullable=False, server_default=func.now(), onupdate=func.now()
    )

    plan_day = relationship("PlanDay", back_populates="exercises")