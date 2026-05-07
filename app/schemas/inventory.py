import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel

class CategoryCreate(BaseModel):
    name: str

class CategoryUpdate(BaseModel):
    name: Optional[str] = None

class CategoryResponse(BaseModel):
    id: uuid.UUID
    name: str
    owner_id: Optional[uuid.UUID] = None
    sharing_scope: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}

class SubCategoryCreate(BaseModel):
    name: str

class SubCategoryUpdate(BaseModel):
    name: Optional[str] = None

class SubCategoryResponse(BaseModel):
    id: uuid.UUID
    name: str
    category_id: uuid.UUID
    owner_id: Optional[uuid.UUID] = None
    sharing_scope: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}

class ExerciseCreate(BaseModel):
    name: str
    description: Optional[str] = None
    target_muscles: Optional[str] = None

class ExerciseUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    target_muscles: Optional[str] = None

class ExerciseResponse(BaseModel):
    id: uuid.UUID
    name: str
    description: Optional[str] = None
    target_muscles: Optional[str] = None
    subcategory_id: uuid.UUID
    owner_id: Optional[uuid.UUID] = None
    sharing_scope: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}