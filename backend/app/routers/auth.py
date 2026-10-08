from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.auth import Token, AdminRegisterRequest, LoginRequest
from app.schemas.user import UserResponse
from app.services.auth_service import register_admin, authenticate_user
from app.dependencies.auth import get_current_user
from app.models.user import User

router = APIRouter(prefix="/api/auth",
                   tags=["Authentication"])


@router.post("/register", response_model=UserResponse, status_code=201)
def register(data: AdminRegisterRequest, db: Session = Depends(get_db)):
   
    admin = register_admin(db, data)
    return admin


@router.post("/login", response_model=Token)
def login(data: LoginRequest, db: Session = Depends(get_db)):
    return authenticate_user(db, data)
    # login_data = LoginRequest(username=form_data.username, password=form_data.password)
    

@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    """Return the currently authenticated user."""
    return {
        "id": current_user.id,
        "full_name": current_user.full_name,
        "email": current_user.email,
        "role": current_user.role,
        "active": current_user.active,
        "created_at": current_user.created_at,
        "shop_id": current_user.shop_id,
        "shop_name": current_user.shop.name if current_user.shop else None,
    }
    
