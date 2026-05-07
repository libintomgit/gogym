import uuid
from datetime import datetime

from sqlalchemy import Enum, ForeignKey, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class SharedItem(Base):
    __tablename__ = "shared_items"
    __table_args__ = (
        UniqueConstraint("item_type", "item_id", "shared_with_user_id",
                         name="uq_shared_item_user"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, default=uuid.uuid4
    )
    item_type: Mapped[str] = mapped_column(
        Enum("category", "subcategory", "exercise", "workout_plan",
             name="shared_item_type"),
        nullable=False,
    )
    item_id: Mapped[uuid.UUID] = mapped_column(nullable=False)
    shared_with_user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id"), nullable=False
    )
    shared_by_user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id"), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        nullable=False, server_default=func.now()
    )
