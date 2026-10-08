from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from decimal import Decimal
from app.models.expense import ExpenseCategory


class ExpenseCreate(BaseModel):
    category: ExpenseCategory = ExpenseCategory.OTHER
    description: str = Field(..., min_length=1, max_length=500)
    amount: Decimal = Field(..., gt=0)
    notes: Optional[str] = Field(None, max_length=1000)


class ExpenseUpdate(BaseModel):
    category: Optional[ExpenseCategory] = None
    description: Optional[str] = Field(None, min_length=1, max_length=500)
    amount: Optional[Decimal] = Field(None, gt=0)
    notes: Optional[str] = Field(None, max_length=1000)


class ExpenseResponse(BaseModel):
    id: int
    shop_id: int
    recorded_by_id: int
    recorded_by_name: Optional[str] = None
    category: ExpenseCategory
    description: str
    amount: Decimal
    notes: Optional[str] = None
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class ExpenseDailySummary(BaseModel):
    date: str
    total_expenses: Decimal
    total_count: int
    by_category: List[dict] = []
    expenses: List[ExpenseResponse] = []