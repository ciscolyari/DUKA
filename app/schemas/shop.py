
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from decimal import Decimal


class ShopResponse(BaseModel):
    id: int
    name: str
    location: Optional[str] = None
    Active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class ShopUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    location: Optional[str] = Field(None, max_length=255)


class ShopDashboardResponse(BaseModel):
    shop: ShopResponse
    today_date: str
    today_total_sales: Decimal
    today_transactions: int
    total_products: int
    total_employees: int
    low_stock_count: int

