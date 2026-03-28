import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import Enum, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

class Category(Base):
    __tablename__ = "categories"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, default=uuid.uuid4
    )

    name: Mapped[str] = mapped_column(
        String(100), nullable=False
    )

    owner_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("users.id"), nullable=True
    )
    sharing_scope: Mapped[str] = mapped_column(
        Enum("private", "shared", "global", name="sharing_scope"),
        nullable=False,
        default="private",
    )
    approval_status: Mapped[Optional[str]] = mapped_column(
        Enum("pending", "approved", "rejected", name="approval_status"),
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        nullable=False, server_default=func.now(), onupdate=func.now()
    )
    subcategories = relationship(
        "SubCategory", back_populates="category", cascade="all, delete-orphan"
    )

class SubCategory(Base):
    __tablename__ = "subcategories"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(
        String(100), nullable=False
    )
    category_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("categories.id"), nullable=False
    )
    owner_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("users.id"), nullable=True
    )
    sharing_scope: Mapped[str] = mapped_column(
        Enum("private", "shared", "global", name="sharing_scope", create_type=False),
        nullable=False,
        default="private",
    )
    approval_status: Mapped[Optional[str]] = mapped_column(
        Enum("pending", "approved", "rejected", name="approval_status", create_type=False),
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        nullable=False, server_default=func.now(), onupdate=func.now()
    )
    category = relationship(
        "Category", back_populates="subcategories"
    )
    exercises = relationship(
        "Exercise", back_populates="subcategory", cascade="all, delete-orphan"
    )

class Exercise(Base):
    __tablename__ = "exercises"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(
        String(150), nullable=False
    )
    description: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True
    )
    target_muscles: Mapped[Optional[str]] = mapped_column(
        String(255), nullable=True
    )
    subcategory_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("subcategories.id"), nullable=False
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

    subcategory = relationship(
        "SubCategory", back_populates="exercises"
    )