from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.schemas.auth import (
    UserRegistrationRequest,
    UserLoginRequest,
    TokenRespose,
    UserResponse,
)
from app.services.auth import register_user, login_user

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register", response_model=TokenRespose, status_code=201)
def register(request: UserRegistrationRequest, db: Session = Depends(get_db)):
    token, user = register_user(db, request.email, request.password, request.name)
    return TokenRespose(
        access_token=token,
        user=UserResponse.model_validate(user),
    )

@router.post("/login", response_model=TokenRespose)
def login(request: UserLoginRequest, db: Session = Depends(get_db)):
    try:
        token, user = login_user(db, request.email, request.password)
    except ValueError:
        raise HTTPException(status_code=401, details="Invalid Credentials")
    return TokenRespose(
        access_token=token,
        user=UserResponse.model_validate(user),
    )