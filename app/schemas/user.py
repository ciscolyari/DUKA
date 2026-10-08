from pydantic import AliasChoices, BaseModel, EmailStr, Field, field_validator, model_validator
from typing import Optional
from app.models.user import UserRole
from datetime import datetime






class userBase(BaseModel):
    full_name:str
    email:EmailStr
    role: UserRole = UserRole.EMPLOYEE
    
    
class createuser(BaseModel):
    full_name: str = Field(min_length=2, max_length=255)
    email: str = Field(validation_alias=AliasChoices("username", "email"), min_length=1, max_length=100)
    role: UserRole = UserRole.EMPLOYEE
    password: str = Field(min_length=6)

    @field_validator("email")
    @classmethod
    def normalize_username(cls, value: str) -> str:
        value = value.strip().lower()
        if not value or any(character.isspace() for character in value):
            raise ValueError("username cannot be empty or contain spaces")
        return value
    
class UserUpdate(BaseModel):
    full_name: Optional[str] = Field(None, min_length=2, max_length=255)
    email: Optional[str] = Field(
        None,
        validation_alias=AliasChoices("username", "email"),
        min_length=1,
        max_length=100,
    )
    password: Optional[str] = Field(None, min_length=6)
    active: Optional[bool] = None

    @field_validator("email")
    @classmethod
    def normalize_username(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value
        value = value.strip().lower()
        if not value or any(character.isspace() for character in value):
            raise ValueError("username cannot be empty or contain spaces")
        return value


class EmployeePasswordReset(BaseModel):
    new_password: str = Field(min_length=6)


class EmployeeStatusUpdate(BaseModel):
    is_active: bool
    



class AdminCreate(BaseModel):
    name:str
    email: EmailStr
    password:str
    #shop_id:int=None

    
class UserResponse(BaseModel):
    id: int
    full_name: str
    email: str
    username: str
    role:UserRole
    shop_name: Optional[str] = None
    active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class UserInDB(UserResponse):
    hashed_password: str   