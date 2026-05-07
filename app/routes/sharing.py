import uuid
from typing import List, Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.dependencies import get_db, get_current_user, require_admin
from app.models.user import User
from app.schemas.sharing import (
    ShareItemRequest, ApprovalActionRequest,
    SharedItemResponse, ApprovalQueueItemResponse,
)
from app.services import sharing as sharing_service

router = APIRouter(prefix="/sharing", tags=["sharing"])


@router.post(
    "/items/{item_type}/{item_id}/share",
    response_model=List[SharedItemResponse],
    status_code=201,
)
def share_with_users(
    item_type: str,
    item_id: uuid.UUID,
    request: ShareItemRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return sharing_service.share_with_users(
        db, item_type, item_id, request.emails, user,
    )


@router.post("/items/{item_type}/{item_id}/submit")
def submit_for_approval(
    item_type: str,
    item_id: uuid.UUID,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    sharing_service.submit_for_approval(db, item_type, item_id, user)
    return {"detail": "Submitted for approval"}


@router.get(
    "/approval-queue",
    response_model=List[ApprovalQueueItemResponse],
)
def get_approval_queue(
    status: Optional[str] = Query(None, description="Filter by status: pending, approved, rejected"),
    db: Session = Depends(get_db),
    user: User = Depends(require_admin),
):
    return sharing_service.get_approval_queue(db, status)


@router.put("/approval-queue/{item_type}/{item_id}")
def approve_or_reject(
    item_type: str,
    item_id: uuid.UUID,
    request: ApprovalActionRequest,
    db: Session = Depends(get_db),
    user: User = Depends(require_admin),
):
    if request.action == "approve":
        sharing_service.approve_item(db, item_type, item_id)
        return {"detail": "Item approved"}
    elif request.action == "reject":
        sharing_service.reject_item(db, item_type, item_id)
        return {"detail": "Item rejected"}
    else:
        return {"detail": "Invalid action. Use 'approve' or 'reject'."}
