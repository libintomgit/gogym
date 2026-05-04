import uuid
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class ShareItemRequest(BaseModel):
    emails: List[str]


class ApprovalActionRequest(BaseModel):
    action: str  # "approve" or "reject"


class SharedItemResponse(BaseModel):
    id: uuid.UUID
    item_type: str
    item_id: uuid.UUID
    shared_with_user_id: uuid.UUID
    shared_by_user_id: uuid.UUID
    created_at: datetime

    model_config = {"from_attributes": True}


class ApprovalQueueItemResponse(BaseModel):
    item_type: str
    item_id: uuid.UUID
    name: str
    owner_id: Optional[uuid.UUID] = None
    sharing_scope: str
    approval_status: str

    model_config = {"from_attributes": True}
