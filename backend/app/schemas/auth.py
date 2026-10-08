from pydantic import AliasChoices, BaseModel, Field, EmailStr
from typing import Optional
from app.models.user import UserRole


class LoginUser(BaseModel):
    id: int
    full_name: str
    email: str
    role: UserRole
    active: bool
    shop_id: Optional[int] = None
    shop_name: Optional[str] = None


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: LoginUser


class TokenData(BaseModel):
    user_id: Optional[int] = None
    username: Optional[str] = None
    role: Optional[UserRole] = None
    shop_id: Optional[int] = None


class LoginRequest(BaseModel):
    username: str = Field(
        ...,
        min_length=3,
        validation_alias=AliasChoices("username", "email"),
    )
    password: str = Field(..., min_length=4)


class AdminRegisterRequest(BaseModel):

    full_name: str = Field(..., min_length=2, max_length=255)
    email: EmailStr = Field(..., min_length=3, max_length=100, unique=True)
    password: str = Field(..., min_length=6)
    shop_name: str = Field(..., min_length=2, max_length=255)
    location: str = Field(..., min_length=2, max_length=255)