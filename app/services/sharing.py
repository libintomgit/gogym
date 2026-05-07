import uuid
from typing import List, Optional

from sqlalchemy.orm import Session

from app.exceptions import ForbiddenError, NotFoundError
from app.models.inventory import Category, SubCategory, Exercise
from app.models.plan import WorkoutPlan
from app.models.sharing import SharedItem
from app.models.user import User


# Map item_type string to the SQLAlchemy model
_TYPE_MODEL_MAP = {
    "category": Category,
    "subcategory": SubCategory,
    "exercise": Exercise,
    "workout_plan": WorkoutPlan,
}


def _get_item(db: Session, item_type: str, item_id: uuid.UUID):
    """Look up a shareable resource by type and id."""
    model = _TYPE_MODEL_MAP.get(item_type)
    if not model:
        raise NotFoundError(f"Unknown item type: {item_type}")
    item = db.query(model).filter(model.id == item_id).first()
    if not item:
        raise NotFoundError(f"{item_type.replace('_', ' ').title()} not found")
    return item


def share_with_users(
    db: Session, item_type: str, item_id: uuid.UUID,
    emails: List[str], current_user: User,
) -> List[SharedItem]:
    """Share a resource with specific users by email."""
    item = _get_item(db, item_type, item_id)

    # Only the owner (or admin) can share
    if current_user.role != "admin" and item.owner_id != current_user.id:
        raise ForbiddenError()

    shared_items = []
    for email in emails:
        target_user = db.query(User).filter(User.email == email).first()
        if not target_user:
            continue  # skip unknown emails silently

        # Don't create duplicate shares
        existing = db.query(SharedItem).filter(
            SharedItem.item_type == item_type,
            SharedItem.item_id == item_id,
            SharedItem.shared_with_user_id == target_user.id,
        ).first()
        if existing:
            shared_items.append(existing)
            continue

        si = SharedItem(
            item_type=item_type,
            item_id=item_id,
            shared_with_user_id=target_user.id,
            shared_by_user_id=current_user.id,
        )
        db.add(si)
        shared_items.append(si)

    # Update sharing_scope to "shared" if it was private
    if item.sharing_scope == "private":
        item.sharing_scope = "shared"

    db.flush()
    return shared_items


def submit_for_approval(
    db: Session, item_type: str, item_id: uuid.UUID, current_user: User,
):
    """Submit a user-owned resource for global approval."""
    item = _get_item(db, item_type, item_id)

    if current_user.role != "admin" and item.owner_id != current_user.id:
        raise ForbiddenError()

    item.approval_status = "pending"
    db.flush()
    return item


def approve_item(db: Session, item_type: str, item_id: uuid.UUID):
    """Admin approves a pending item for global visibility."""
    item = _get_item(db, item_type, item_id)
    item.sharing_scope = "global"
    item.approval_status = "approved"
    db.flush()
    return item


def reject_item(db: Session, item_type: str, item_id: uuid.UUID):
    """Admin rejects a pending item."""
    item = _get_item(db, item_type, item_id)
    item.approval_status = "rejected"
    db.flush()
    return item


def get_approval_queue(
    db: Session, status_filter: Optional[str] = None,
) -> List[dict]:
    """Return items in the approval queue, optionally filtered by status."""
    results = []
    for item_type, model in _TYPE_MODEL_MAP.items():
        q = db.query(model).filter(model.approval_status.isnot(None))
        if status_filter:
            q = q.filter(model.approval_status == status_filter)
        for item in q.all():
            results.append({
                "item_type": item_type,
                "item_id": item.id,
                "name": item.name,
                "owner_id": item.owner_id,
                "sharing_scope": item.sharing_scope,
                "approval_status": item.approval_status,
            })
    return results
