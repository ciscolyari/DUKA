from pydantic import AliasChoices, BaseModel, EmailStr, Field
from typing import Optional
from app.models.user import UserRole
from datetime import datetime






class userBase(BaseModel):
    full_name:str
    email: str = Field(
        ...,
        min_length=3,
        validation_alias=AliasChoices("email", "username"),
    )
    role: UserRole = UserRole.EMPLOYEE
    
    
class createuser(userBase):
    password: str=Field( minlength=6)
    
class UserUpdate(BaseModel):
    full_name: Optional[str] = Field(None, min_length=2, max_length=255)
    email: Optional[str] = Field(None, min_length=3)
    password: Optional[str] = Field(None, min_length=6)
    active: Optional[bool] = Field(
        None,
        validation_alias=AliasChoices("active", "Active", "is_active"),
    )
    



class AdminCreate(BaseModel):
    name:str
    email: EmailStr
    password:str
    #shop_id:int=None

    
class UserResponse(BaseModel):
    id: int
    full_name: str
    email: str
    role:UserRole
    active: bool
    created_at: datetime
    shop_id: Optional[int] = None
    shop_name: Optional[str] = None

    class Config:
        from_attributes = True


class UserInDB(UserResponse):
    hashed_password: str   