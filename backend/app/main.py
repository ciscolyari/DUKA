from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import auth,products,user,sales,shop,expense,subscription,reports
from app .routers import billing,subscription_plan
from .core.database import engine,Base


app=FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://duka-omega.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["Authorization", "Content-Type", "X-Shop-ID"],
)

#Base.metadata.create_all(engine)

app.include_router(auth.router)
app.include_router(user.router)
app.include_router(products.router)

app.include_router(sales.router)
app.include_router(shop.router)
app.include_router(expense.router)
app.include_router(reports.router)
app.include_router(subscription_plan.router)
app. include_router(subscription.router)
app. include_router(billing.router)



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
