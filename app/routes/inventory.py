import uuid
from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.dependencies import get_db, get_current_user
from app.models.user import User
from app.schemas.inventory import (
    CategoryCreate, CategoryUpdate, CategoryResponse,
    SubCategoryCreate, SubCategoryUpdate, SubCategoryResponse,
    ExerciseCreate, ExerciseUpdate, ExerciseResponse,
)
from app.services import inventory as inv_service

router = APIRouter(prefix="/inventory", tags=["inventory"])

# --- Categories ---

@router.get("/categories", response_model=List[CategoryResponse])
def list_categories(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return inv_service.list_categories(db, user)


@router.post("/categories", response_model=CategoryResponse, status_code=201)
def create_category(
    request: CategoryCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return inv_service.create_category(db, request.name, user)


@router.put("/categories/{cat_id}", response_model=CategoryResponse)
def update_category(
    cat_id: uuid.UUID,
    request: CategoryUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return inv_service.update_category(db, cat_id, request.name, user)


@router.delete("/categories/{cat_id}", status_code=204)
def delete_category(
    cat_id: uuid.UUID,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    inv_service.delete_category(db, cat_id, user)

# --- SubCategories ---

@router.get("/categories/{cat_id}/subcategories", response_model=List[SubCategoryResponse])
def list_subcategories(
    cat_id: uuid.UUID,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return inv_service.list_subcategories(db, cat_id, user)


@router.post("/categories/{cat_id}/subcategories", response_model=SubCategoryResponse, status_code=201)
def create_subcategory(
    cat_id: uuid.UUID,
    request: SubCategoryCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return inv_service.create_subcategory(db, cat_id, request.name, user)


@router.put("/subcategories/{sub_id}", response_model=SubCategoryResponse)
def update_subcategory(
    sub_id: uuid.UUID,
    request: SubCategoryUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return inv_service.update_subcategory(db, sub_id, request.name, user)


@router.delete("/subcategories/{sub_id}", status_code=204)
def delete_subcategory(
    sub_id: uuid.UUID,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    inv_service.delete_subcategory(db, sub_id, user)

# --- Exercises ---

@router.get("/subcategories/{sub_id}/exercises", response_model=List[ExerciseResponse])
def list_exercises(
    sub_id: uuid.UUID,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return inv_service.list_exercises(db, sub_id, user)


@router.post("/subcategories/{sub_id}/exercises", response_model=ExerciseResponse, status_code=201)
def create_exercise(
    sub_id: uuid.UUID,
    request: ExerciseCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return inv_service.create_exercise(
        db, sub_id, request.name, request.description,
        request.target_muscles, user,
    )


@router.put("/exercises/{ex_id}", response_model=ExerciseResponse)
def update_exercise(
    ex_id: uuid.UUID,
    request: ExerciseUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return inv_service.update_exercise(
        db, ex_id, user, request.name, request.description,
        request.target_muscles,
    )


@router.delete("/exercises/{ex_id}", status_code=204)
def delete_exercise(
    ex_id: uuid.UUID,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    inv_service.delete_exercise(db, ex_id, user)