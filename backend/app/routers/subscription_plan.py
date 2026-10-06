from typing import List

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.dependencies.auth import get_current_user, get_current_admin
from app.models.user import User
from app.schemas.subscription import (
    PlanCreate,
    PlanUpdate,
    PlanStatusUpdate,
    PlanResponse,
    SubscribeRequest,
    ChangePlanRequest,
    SubscriptionStatusUpdate,
    SubscriptionResponse,
)
from app.services import subscription_service

router = APIRouter(tags=["Subscription plans"])


# ===================== PLANS =====================

@router.post("/api/subscription-plans", response_model=PlanResponse, status_code=201)
def create_plan(
    data: PlanCreate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin),
):
    return subscription_service.create_plan(db, data, current_admin)


@router.get("/api/subscription-plans", response_model=List[PlanResponse])
def list_plans(
    active_only: bool = Query(False),
    db: Session = Depends(get_db),
):
    return subscription_service.list_plans(db, active_only=active_only)


@router.get("/api/subscription-plans/{plan_id}", response_model=PlanResponse)
def get_plan(plan_id: int, db: Session = Depends(get_db)):
    return subscription_service.get_plan(db, plan_id)


@router.put("/api/subscription-plans/{plan_id}", response_model=PlanResponse)
def update_plan(
    plan_id: int,
    data: PlanUpdate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin),
):
    return subscription_service.update_plan(db, plan_id, data, current_admin)


@router.patch("/api/subscription-plans/{plan_id}/status", response_model=PlanResponse)
def set_plan_status(
    plan_id: int,
    data: PlanStatusUpdate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin),
):
    return subscription_service.set_plan_status(db, plan_id, data.is_active, current_admin)
