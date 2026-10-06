from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from decimal import Decimal
from app.models.billing import BillingStatus


class BillingResponse(BaseModel):
    id: int
    shop_id: int
    subscription_id: int
    paid_by_id: int
    paid_by_name: Optional[str] = None
    plan: str
    amount: Decimal
    currency: str
    transaction_ref: Optional[str] = None
    payment_date: datetime
    status: BillingStatus
    notes: Optional[str] = None
    invoice_number: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class InvoiceResponse(BaseModel):
    id: int
    billing_id: int
    shop_id: int
    subscription_id: int
    invoice_number: str
    amount: Decimal
    currency: str
    issued_at: datetime
    plan: Optional[str] = None
    transaction_ref: Optional[str] = None

    class Config:
        from_attributes = True