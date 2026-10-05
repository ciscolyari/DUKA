from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.core.security import hash_password, verify_password, create_access_token
from app.models.user import User, UserRole
from app.models.shop import Shop
from app.schemas.auth import AdminRegisterRequest, LoginRequest,TokenData
from app.services.subscription_service import create_trial


def register_admin(db: Session, data: AdminRegisterRequest):
    existing = db.query(User).filter(User.email == data.email).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Email already taken",)
    
    
    shop = Shop(
        name=data.shop_name,
        location=data.location
    )
    create_trial(shop)   # ← trial 14 days

    db.add(shop)
    db.flush()


    admin = User(
        email=data.email,
        full_name=data.full_name,
        hashed_password=hash_password(data.password),
        role = UserRole.ADMIN,
        shop_id=shop.id
        
    )
    db.add(admin)
    db.commit()
    db.refresh(admin)
    return admin


def authenticate_user(db: Session, data: LoginRequest):
    user = db.query(User).filter(User.email == data.email).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="wrong email")
    if not verify_password(data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.Active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is inactive",
        )
    token = create_access_token( { "sub": str(user.id),
                                  "email": user.email,
                                  "role": user.role.value,
                                  "shop_id": user.shop_id, } )
    return{"access_token":token,
           "token_type":"bearer"
        
    }
    


def userlogin(email:str,password: str,db: Session):
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"incorect user name")
    
    if not verify_password(user.hashed_password,password):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Incorrect password")
    token=create_access_token({"sub":user.email})
    
    return{
        "access_token":token,
        "token_type":"Bearer"
    }
        
        
        
        


    