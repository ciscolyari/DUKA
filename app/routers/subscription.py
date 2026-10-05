from typing import List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.dependencies.auth import get_current_user, get_current_admin
from app.models.user import User
from app.schemas.subscription import (
    PlanCreate, PlanUpdate, PlanStatusUpdate, PlanResponse,
    SubscribeRequest, ChangePlanRequest, SubscriptionStatusUpdate, SubscriptionResponse,
)
from app.services import subscription_service

router = APIRouter(tags=["Subscription"])


# Plans
@router.post("/api/subscription-plans", response_model=PlanResponse, status_code=201)
def create_plan(data: PlanCreate, db: Session = Depends(get_db), current_admin: User = Depends(get_current_admin)):
    return subscription_service.create_plan(db, data, current_admin)


@router.get("/api/subscription-plans", response_model=List[PlanResponse])
def list_plans(active_only: bool = Query(False), db: Session = Depends(get_db)):
    return subscription_service.list_plans(db, active_only=active_only)


@router.get("/api/subscription-plans/{plan_id}", response_model=PlanResponse)
def get_plan(plan_id: int, db: Session = Depends(get_db)):
    return subscription_service.get_plan(db, plan_id)


@router.put("/api/subscription-plans/{plan_id}", response_model=PlanResponse)
def update_plan(plan_id: int, data: PlanUpdate, db: Session = Depends(get_db), current_admin: User = Depends(get_current_admin)):
    return subscription_service.update_plan(db, plan_id, data, current_admin)


@router.patch("/api/subscription-plans/{plan_id}/status", response_model=PlanResponse)
def set_plan_status(plan_id: int, data: PlanStatusUpdate, db: Session = Depends(get_db), current_admin: User = Depends(get_current_admin)):
    return subscription_service.set_plan_status(db, plan_id, data.is_active, current_admin)


# Subscriptions
@router.post("/api/subscriptions", response_model=SubscriptionResponse, status_code=201)
def subscribe(data: SubscribeRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return subscription_service.subscribe(db, data, current_user)


@router.get("/api/subscriptions/current", response_model=SubscriptionResponse)
def current_subscription(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return subscription_service.get_current_subscription(db, current_user)


@router.get("/api/subscriptions/history", response_model=List[SubscriptionResponse])
@router.get("/api/subscriptions", response_model=List[SubscriptionResponse])
def subscription_history(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return subscription_service.list_subscriptions(db, current_user)


@router.get("/api/subscriptions/{subscription_id}", response_model=SubscriptionResponse)
def get_subscription(subscription_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return subscription_service.get_subscription(db, subscription_id, current_user)


@router.get("/api/subscriptions/{subscription_id}/status")
def get_status(subscription_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    sub = subscription_service.get_subscription(db, subscription_id, current_user)
    return {
        "subscription_id": sub["id"],
        "status": sub["status"],
        "is_valid": sub["is_valid"],
        "days_remaining": sub["days_remaining"],
        "expires_at": sub["expires_at"],
    }


@router.patch("/api/subscriptions/{subscription_id}/status", response_model=SubscriptionResponse)
def update_status(subscription_id: int, data: SubscriptionStatusUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return subscription_service.update_subscription_status(db, subscription_id, data, current_user)


@router.post("/api/subscriptions/{subscription_id}/change-plan", response_model=SubscriptionResponse)
def change_plan(subscription_id: int, data: ChangePlanRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return subscription_service.change_plan(db, subscription_id, data, current_user)


@router.get("/api/subscriptions/{subscription_id}/available-plans", response_model=List[PlanResponse])
def available_plans(subscription_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return subscription_service.available_plans_for_change(db, subscription_id, current_user)


@router.get("/api/subscriptions/{subscription_id}/plan-history", response_model=List[SubscriptionResponse])
def plan_history(subscription_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return subscription_service.list_subscriptions(db, current_user)