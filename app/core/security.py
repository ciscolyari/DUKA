from fastapi import HTTPException, Depends, status
from datetime import datetime, timedelta
from pwdlib import PasswordHash
from sqlalchemy.orm import Session
from app.core.database import get_db
from jose import JWTError, jwt
from fastapi.security import OAuth2PasswordBearer


password_hash=PasswordHash.recommended()

SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cfec4333d00c3"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES=30

Oauth2_scheme= OAuth2PasswordBearer(tokenUrl="user_login")

#class Hashing:
    #@staticmethod
def hash_password(password: str):
        return password_hash.hash(password)

    #@staticmethod
def verify_password(hashed_password, plain_password):
        return password_hash.verify(plain_password, hashed_password)
    
def create_access_token(data:dict):
    to_encode=data.copy()
    expire= datetime.now()+timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES) 
    to_encode.update({"exp":expire})
    token= jwt.encode(to_encode,SECRET_KEY, algorithm=ALGORITHM)
    return token
        
def verify_token(token: str):
    payload=jwt.decode(token,SECRET_KEY, algorithms=[ALGORITHM])
    if not payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid token")
    return payload

def create_current_user(token:str=Depends(Oauth2_scheme),db:Session=Depends(get_db)):
    payload= verify_token(token)
    email= payload.get("sub")
    if not email:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid credential", headers={"WWW-auntheicated":"Bearer"})
    user=db.query(user).filter(user.email==email).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="user not found")
    return user