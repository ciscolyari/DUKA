

from pydantic import BaseModel, Field
from typing import Optional, Any
from datetime import datetime
from decimal import Decimal
from app.models.subscription import BillingInterval, SubscriptionStatus
from app.models.shop import SubscriptionPlan, SubscriptionStatus

# ---------- Plans ----------

class PlanCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    price: Decimal = Field(..., ge=0)
    currency: str = "TZS"
    duration_days: int = Field(30, gt=0)
    billing_interval: BillingInterval = BillingInterval.MONTHLY
    features: Optional[dict] = None
    is_active: bool = True


class PlanUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    price: Optional[Decimal] = Field(None, ge=0)
    currency: Optional[str] = None
    duration_days: Optional[int] = Field(None, gt=0)
    billing_interval: Optional[BillingInterval] = None
    features: Optional[dict] = None


class PlanStatusUpdate(BaseModel):
    is_active: bool


class PlanResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    price: Decimal
    currency: str
    duration_days: int
    billing_interval: BillingInterval
    features: Optional[Any] = None
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


# ---------- Subscriptions ----------

class SubscribeRequest(BaseModel):
    plan_id: int
    payment_ref: Optional[str] = None
    amount_paid: Optional[Decimal] = None
    notes: Optional[str] = None


class ChangePlanRequest(BaseModel):
    new_plan_id: int
    payment_ref: Optional[str] = None
    amount_paid: Optional[Decimal] = None
    notes: Optional[str] = None


class SubscriptionStatusUpdate(BaseModel):
    status: SubscriptionStatus
    notes: Optional[str] = None


class SubscriptionResponse(BaseModel):
    id: int
    shop_id: int
    plan_id: int
    plan_name: Optional[str] = None
    status: SubscriptionStatus
    starts_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    days_remaining: int = 0
    is_valid: bool = False
    is_current: bool
    amount_paid: Optional[Decimal] = None
    payment_ref: Optional[str] = None
    notes: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True





# from pydantic import BaseModel, Field
# from typing import Optional
# from decimal import Decimal
# from datetime import datetime



# class SubscriptionResponse(BaseModel):
#     shop_id: int
#     shop_name: str
#     plan: SubscriptionPlan
#     status: SubscriptionStatus
#     starts_at: Optional[datetime] = None
#     expires_at: Optional[datetime] = None
#     days_remaining: int
#     is_active: bool
#     max_employees: int
#     max_products: int
#     last_payment_ref: Optional[str] = None
    
    
class ActivateSubscriptionRequest(BaseModel):
    plan: SubscriptionPlan = SubscriptionPlan.BASIC
    payment_ref: Optional[str] = None
    amount_paid: Optional[Decimal] = None
    days: Optional[int] = None


# class ActivateSubscriptionRequest(BaseModel):
#     plan: SubscriptionPlan = SubscriptionPlan.BASIC
#     payment_ref: Optional[str] = Field(None, max_length=255)
#     days: Optional[int] = Field(None, gt=0)


# class PlanInfo(BaseModel):
#     plan: SubscriptionPlan
#     max_employees: int
#     max_products: int
#     days: int
#     description: str