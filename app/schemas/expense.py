from pydantic import BaseModel, Field, field_validator, model_validator
from typing import List, Optional
from datetime import datetime
from decimal import Decimal
from app.models.expense import ExpenseCategory


def _normalize_enum_value(value):
    if isinstance(value, str):
        return value.strip().lower()
    return value


class ExpenseCreate(BaseModel):
    category: ExpenseCategory = ExpenseCategory.OTHER
    description: Optional[str] = Field(None, min_length=1, max_length=500)
    title: Optional[str] = None
    amount: Decimal = Field(..., gt=0)
    notes: Optional[str] = Field(None, max_length=1000)
    date: Optional[str] = None
    payment_method: Optional[str] = None

    @model_validator(mode="before")
    @classmethod
    def normalize_input(cls, values):
        if not isinstance(values, dict):
            return values

        if values.get("description") is None and values.get("title"):
            values["description"] = values["title"]
        if values.get("category") is not None:
            values["category"] = _normalize_enum_value(values["category"])
        if values.get("notes") is None:
            parts = []
            if values.get("payment_method"):
                parts.append(f"Payment method: {values['payment_method']}")
            if values.get("date"):
                parts.append(f"Date: {values['date']}")
            if parts:
                values["notes"] = "; ".join(parts)
        return values

    @field_validator("description")
    @classmethod
    def ensure_description(cls, value):
        if value is None:
            return None
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("description is required")
        return cleaned

    @model_validator(mode="after")
    def require_description(self):
        if not self.description:
            raise ValueError("description is required")
        return self


class ExpenseUpdate(BaseModel):
    category: Optional[ExpenseCategory] = None
    description: Optional[str] = Field(None, min_length=1, max_length=500)
    amount: Optional[Decimal] = Field(None, gt=0)
    notes: Optional[str] = Field(None, max_length=1000)

    @field_validator("category", mode="before")
    @classmethod
    def normalize_category(cls, value):
        return _normalize_enum_value(value)


class ExpenseResponse(BaseModel):
    id: int
    shop_id: int
    recorded_by_id: int
    recorded_by_name: Optional[str] = None
    recorded_by: Optional[str] = None
    title: str
    category: ExpenseCategory
    description: str
    date: datetime
    amount: Decimal
    notes: Optional[str] = None
    payment_method: Optional[str] = None
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