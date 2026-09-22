from fastapi import FastAPI
# from sqlalchemy.orm import Session 
from app.routers import auth
from .core.database import engine,Base





app=FastAPI()

Base.metadata.create_all(engine)

app.include_router(auth.router)
# app.include_router(notes.router)

