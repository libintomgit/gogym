import uuid
from typing import List

from sqlalchemy.orm import Session

from app.exceptions import ForbiddenError, NotFoundError
from app.models.inventory import Category, SubCategory, Exercise
from app.models.sharing import SharedItem
from app.models.user import User

# --- Helpers ---

def _check_ownership(resource, user: User):
    """Allow if user is admin or owns the resources"""
    if user.role == "admin":
        return
    if resource.owner_id != user.id:
        raise ForbiddenError()

def _visible_filter(query, model, user: User):
    """Return global + user's own + shared with user."""
    table_to_type = {
        "categories": "category",
        "subcategories": "subcategory",
        "exercises": "exercise",
        "workout_plans": "workout_plan",
    }
    item_type = table_to_type.get(model.__tablename__, model.__tablename__)

    shared_ids = [
        row.item_id
        for row in query.session.query(SharedItem.item_id)
        .filter(
            SharedItem.shared_with_user_id == user.id,
            SharedItem.item_type == item_type,
        )
        .all()
    ]

    if shared_ids:
        return query.filter(
            (model.sharing_scope == "global")
            | (model.owner_id == user.id)
            | (model.id.in_(shared_ids))
        )
    return query.filter(
        (model.sharing_scope == "global")
        | (model.owner_id == user.id)
    )

# --- Category ---

def list_categories(db: Session, user: User) -> List[Category]:
    q = db.query(Category)
    return _visible_filter(q, Category, user).all()

def create_category(db: Session, name: str, user: User) -> Category:
    scope = "global" if user.role == "admin" else "private"
    cat = Category(name=name, owner_id=user.id, sharing_scope=scope)
    db.add(cat)
    db.flush()
    return cat

def update_category(db: Session, cat_id: uuid.UUID, name: str, user: User) -> Category:
    cat = db.query(Category).filter(Category.id == cat_id).first()
    if not cat:
        raise NotFoundError("Category not found")
    _check_ownership(cat, user)
    if name is not None:
        cat.name = name
    db.flush()
    return cat

def delete_category(db: Session, cat_id: uuid.UUID, user: User):
    cat = db.query(Category).filter(Category.id == cat_id).first()
    if not cat:
        raise NotFoundError("Category not found")
    _check_ownership(cat, user)
    db.delete(cat)
    db.flush()


# --- SubCategory ---

def list_subcategories(db: Session, category_id: uuid.UUID, user: User) -> List[SubCategory]:
    q = db.query(SubCategory).filter(SubCategory.category_id == category_id)
    return _visible_filter(q, SubCategory, user).all()


def create_subcategory(db: Session, category_id: uuid.UUID, name: str, user: User) -> SubCategory:
    cat = db.query(Category).filter(Category.id == category_id).first()
    if not cat:
        raise NotFoundError("Category not found")
    scope = "global" if user.role == "admin" else "private"
    sub = SubCategory(
        name=name, category_id=category_id, owner_id=user.id, sharing_scope=scope
    )
    db.add(sub)
    db.flush()
    return sub


def update_subcategory(db: Session, sub_id: uuid.UUID, name: str, user: User) -> SubCategory:
    sub = db.query(SubCategory).filter(SubCategory.id == sub_id).first()
    if not sub:
        raise NotFoundError("SubCategory not found")
    _check_ownership(sub, user)
    if name is not None:
        sub.name = name
    db.flush()
    return sub


def delete_subcategory(db: Session, sub_id: uuid.UUID, user: User):
    sub = db.query(SubCategory).filter(SubCategory.id == sub_id).first()
    if not sub:
        raise NotFoundError("SubCategory not found")
    _check_ownership(sub, user)
    db.delete(sub)
    db.flush()


# --- Exercise ---

def list_exercises(db: Session, subcategory_id: uuid.UUID, user: User) -> List[Exercise]:
    q = db.query(Exercise).filter(Exercise.subcategory_id == subcategory_id)
    return _visible_filter(q, Exercise, user).all()


def create_exercise(
    db: Session, subcategory_id: uuid.UUID, name: str,
    description: str, target_muscles: str, user: User,
) -> Exercise:
    sub = db.query(SubCategory).filter(SubCategory.id == subcategory_id).first()
    if not sub:
        raise NotFoundError("SubCategory not found")
    scope = "global" if user.role == "admin" else "private"
    ex = Exercise(
        name=name, description=description, target_muscles=target_muscles,
        subcategory_id=subcategory_id, owner_id=user.id, sharing_scope=scope,
    )
    db.add(ex)
    db.flush()
    return ex


def update_exercise(
    db: Session, ex_id: uuid.UUID, user: User,
    name: str = None, description: str = None, target_muscles: str = None,
) -> Exercise:
    ex = db.query(Exercise).filter(Exercise.id == ex_id).first()
    if not ex:
        raise NotFoundError("Exercise not found")
    _check_ownership(ex, user)
    if name is not None:
        ex.name = name
    if description is not None:
        ex.description = description
    if target_muscles is not None:
        ex.target_muscles = target_muscles
    db.flush()
    return ex


def delete_exercise(db: Session, ex_id: uuid.UUID, user: User):
    ex = db.query(Exercise).filter(Exercise.id == ex_id).first()
    if not ex:
        raise NotFoundError("Exercise not found")
    _check_ownership(ex, user)
    db.delete(ex)
    db.flush()