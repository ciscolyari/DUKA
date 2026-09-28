from pydantic import BaseModel, EmailStr,Field
from typing import Optional
from app.models.user import UserRole
from datetime import datetime






class userBase(BaseModel):
    full_name:str
    email:EmailStr
    role: UserRole = UserRole.EMPLOYEE
    
    
class createuser(userBase):
    password: str=Field( minlength=6)
    
class UserUpdate(BaseModel):
    full_name: Optional[str] = Field(None, min_length=2, max_length=255)
    password: Optional[str] = Field(None, min_length=6)
    Active: Optional[bool] = None    
    



class AdminCreate(BaseModel):
    name:str
    email: EmailStr
    password:str
    #shop_id:int=None

    
class UserResponse(BaseModel):
    id: int
    full_name: str
    email:EmailStr
    role:UserRole
    active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class UserInDB(UserResponse):
    hashed_password: str   