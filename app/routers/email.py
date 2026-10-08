# from fastapi import APIRouter, Depends, HTTPException, status
# from sqlalchemy.orm import Session
# from pydantic import BaseModel
# from app.models.user import User
# from datetime import date,timedelta,datetime
# from app.services.email import generate_otp,send_verification_email
# from app.core.database import get_db



# router = APIRouter(
    
# )


# @router.post("/register")
# async def register_user(email: str, password: str, db: Session = Depends(get_db)):
#   # Angalia kama email ipo tayari
#   existing_user = db.query(User).filter(User.email == email).first()
#   if existing_user:
#     raise HTTPException(
#         status_code=400, detail="Barua pepe hii imeshasajiliwa tayari."
#     )

#   # Tengeneza OTP na muda wa kuisha (dakika 10)
#   code = generate_otp()
#   expires_at = datetime.utcnow() + timedelta(minutes=10)

#   # Hifadhi mtumiaji (hapa utahash password kwanza kama kawaida yako)
#   new_user = User(
#       email=email,
#       hashed_password=password,  # Tumia password_context yako kushepu
#       is_verified=False,
#       verification_code=code,
#       code_expires_at=expires_at,
#   )
#   db.add(new_user)
#   db.commit()

#   # Tuma email
#   await send_verification_email(email, code)

#   return {
#       "message": (
#           "Usajili umefanikiwa. Tafadhali angalia barua pepe yako kupata"
#           " namba ya uthibitisho."
#       )
#   }
  
  
  
#   from pydantic import BaseModel


# class VerifyRequest(BaseModel):
#   email: str
#   code: str


# @router.post("/verify-email")
# def verify_email(payload: VerifyRequest, db: Session = Depends(get_db)):
#   user = db.query(User).filter(User.email == payload.email).first()

#   if not user:
#     raise HTTPException(
#         status_code=404, detail="Mtumiaji hapatikani kwenye mfumo."
#     )

#   if user.is_verified:
#     return {"message": "Barua pepe hii imeshathibitishwa tayari."}

#   # Angalia kama code inafanana
#   if user.verification_code != payload.code:
#     raise HTTPException(status_code=400, detail="Namba ya uthibitisho si sahihi.")

#   # Angalia kama muda wa code umeisha
#   if user.code_expires_at and datetime.utcnow() > user.code_expires_at:
#     raise HTTPException(
#         status_code=400,
#         detail="Namba ya uthibitisho imeisha muda wake. Omba nyingine.",
#     )

#   # Thibitisha mtumiaji na futa code iliyotumika
#   user.is_verified = True
#   user.verification_code = None
#   user.code_expires_at = None
#   db.commit()

#   return {"message": "Barua pepe imethibitishwa mafanikio!"}


# @router.post("/resend-code")
# async def resend_code(email: str, db: Session = Depends(get_db)):
#   user = db.query(User).filter(User.email == email).first()

#   if not user:
#     raise HTTPException(status_code=404, detail="Mtumiaji hapatikani.")

#   if user.is_verified:
#     return {"message": "Akaunti hii imeshathibitishwa tayari."}

#   # Tengeneza code mpya na muda mpya
#   code = generate_otp()
#   user.verification_code = code
#   user.code_expires_at = datetime.utcnow() + timedelta(minutes=10)
#   db.commit()

#   # Tuma email mpya
#   await send_verification_email(email, code)

#   return {"message": "Namba mpya ya uthibitisho imetumwa kwenye barua pepe yako."}