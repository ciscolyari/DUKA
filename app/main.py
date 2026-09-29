from fastapi import FastAPI

from app.routers import auth,products,user,sales
from .core.database import engine,Base





app=FastAPI()

Base.metadata.create_all(engine)

app.include_router(auth.router)
app.include_router(user.router)
app.include_router(products.router)

app.include_router(sales.router)
# app.include_router(reports.router)


@app.get("/")
def root():
    return{
        "message":"Welcome to DUKA",
        "docs":"/docs",
        "status":"running"
    }
    
    
@app.get("/Health")
def health_check():
    return{"status":"Health"}   