from fastapi import FastAPI, APIRouter, Depends
#from app.schemas.user import createuser
from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.auth import Token, AdminRegisterRequest, LoginRequest
from app.services.auth_service import userlogin
from app.schemas.user import UserResponse
from app.services.auth_service import register_admin, authenticate_user
from app.dependencies.auth import get_current_user
from app.models.user import User

router = APIRouter(prefix="/api/auth",
                   tags=["Authentication"])


@router.post("/register", response_model=UserResponse, status_code=201)
def register(
    data: AdminRegisterRequest,
    db: Session = Depends(get_db)
):
    admin = register_admin(db, data)
    return admin

@router.post("/login", response_model=Token)
def login(data: OAuth2PasswordRequestForm = Depends(),db: Session = Depends(get_db),
):
    return userlogin(data.username,data.password,db)
    # login_data = LoginRequest(username=form_data.username, password=form_data.password)
    # user = authenticate_user(db, login_data)
    # access_token = create_token_for_user(user)
    # return Token(access_token=access_token)
    

@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    """Return the currently authenticated user."""
    return current_user
    
