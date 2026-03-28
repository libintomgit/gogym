import uuid
from datetime import date, datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import (
    CheckConstraint, Date, DateTime, Enum, ForeignKey, Integer,
    Numeric, UniqueConstraint, func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class WorkoutSession(Base):
    __tablename__ = "workout_sessions"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id"), nullable=False
    )
    plan_day_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("plan_days.id"), nullable=False
    )
    session_date: Mapped[date] = mapped_column(
        Date, nullable=False
    )
    status: Mapped[str] = mapped_column(
        Enum("in_progress", "completed", "partial",
             name="session_status"),
        nullable=False,
        default="in_progress",
    )
    started_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )
    completed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        nullable=False, server_default=func.now(), onupdate=func.now()
    )

    set_logs = relationship(
        "SetLog", back_populates="session", cascade="all, delete-orphan"
    )


class SetLog(Base):
    __tablename__ = "set_logs"
    __table_args__ = (
        UniqueConstraint("session_id", "exercise_id", "set_number",
                         name="uq_session_exercise_set"),
        CheckConstraint("weight > 0", name="ck_weight_positive"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, default=uuid.uuid4
    )
    session_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("workout_sessions.id"), nullable=False
    )
    exercise_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("exercises.id"), nullable=False
    )
    set_number: Mapped[int] = mapped_column(Integer, nullable=False)
    reps_performed: Mapped[int] = mapped_column(Integer, nullable=False)
    weight: Mapped[Decimal] = mapped_column(
        Numeric(7, 2), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        nullable=False, server_default=func.now()
    )

    session = relationship("WorkoutSession", back_populates="set_logs")
