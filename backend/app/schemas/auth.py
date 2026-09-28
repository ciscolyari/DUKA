from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from app.models.user import UserRole


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    user_id: Optional[int] = None
    username: Optional[str] = None
    role: Optional[UserRole] = None
    shop_id: Optional[int] = None


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=4)


class AdminRegisterRequest(BaseModel):

    full_name: str = Field(..., min_length=2, max_length=255)
    email: EmailStr = Field(..., min_length=3, max_length=100, unique=True)
    password: str = Field(..., min_length=6)
    shop_id: int