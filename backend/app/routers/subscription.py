from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.dependencies.auth import get_current_admin
from app.models.user import User
from app.schemas.subscription import (
    SubscriptionResponse,
    ActivateSubscriptionRequest,
    PlanInfo,
)
from app.services import subscription_service

router = APIRouter(prefix="/api/subscription", tags=["Subscription"])


@router.get("", response_model=SubscriptionResponse)
def get_my_subscription(
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin),
):
    
    return subscription_service.get_subscription(db, current_admin)


@router.get("/plans", response_model=List[PlanInfo])
def list_plans():
   
    return subscription_service.list_plans()


@router.post("/activate", response_model=SubscriptionResponse)
def activate_subscription(
    data: ActivateSubscriptionRequest,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin),
):

    return subscription_service.activate_subscription(db, current_admin, data)