import uuid

from pydantic import BaseModel, EmailStr

class UserRegistrationRequest(BaseModel):
    email: str
    password: str
    name: str

class UserLoginRequest(BaseModel):
    email: str
    password: str

class UserResponse(BaseModel):
    id: uuid.UUID
    email: str
    name: str
    role: str

    model_config = {"from_attributes": True}

class TokenRespose(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse