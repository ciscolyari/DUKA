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
    email: Optional[EmailStr] = None
    password: Optional[str] = Field(None, min_length=6)
    active: Optional[bool] = None


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
    email:EmailStr
    role:UserRole
    shop_name: Optional[str] = None
    active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class UserInDB(UserResponse):
    hashed_password: str   