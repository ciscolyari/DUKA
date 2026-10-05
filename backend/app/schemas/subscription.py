from pydantic import BaseModel, Field
from typing import Optional
from decimal import Decimal
from datetime import datetime
from app.models.shop import SubscriptionPlan, SubscriptionStatus


class SubscriptionResponse(BaseModel):
    shop_id: int
    shop_name: str
    plan: SubscriptionPlan
    status: SubscriptionStatus
    starts_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    days_remaining: int
    is_active: bool
    max_employees: int
    max_products: int
    last_payment_ref: Optional[str] = None
    
    
class ActivateSubscriptionRequest(BaseModel):
    plan: SubscriptionPlan = SubscriptionPlan.BASIC
    payment_ref: Optional[str] = None
    amount_paid: Optional[Decimal] = None
    days: Optional[int] = None


class ActivateSubscriptionRequest(BaseModel):
    plan: SubscriptionPlan = SubscriptionPlan.BASIC
    payment_ref: Optional[str] = Field(None, max_length=255)
    days: Optional[int] = Field(None, gt=0)


class PlanInfo(BaseModel):
    plan: SubscriptionPlan
    max_employees: int
    max_products: int
    days: int
    description: str