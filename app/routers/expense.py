from datetime import date
from decimal import Decimal
from typing import List, Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.models.expense import ExpenseCategory
from app.schemas.expense import (
    ExpenseCreate,
    ExpenseUpdate,
    ExpenseResponse,
    ExpenseDailySummary,
)
from app.services import expense_service

router = APIRouter(prefix="/api/expenses", tags=["Expenses"])


def _to_response(expense) -> ExpenseResponse:
    return ExpenseResponse(
        id=expense.id,
        shop_id=expense.shop_id,
        recorded_by_id=expense.recorded_by_id,
        recorded_by_name=expense.recorded_by.full_name if expense.recorded_by else None,
        category=expense.category,
        description=expense.description,
        amount=expense.amount,
        notes=expense.notes,
        is_active=expense.is_active,
        created_at=expense.created_at,
    )


@router.post("", response_model=ExpenseResponse, status_code=201)
def create_expense(data: ExpenseCreate,db: Session = Depends(get_db),current_user: User = Depends(get_current_user),):
    expense = expense_service.create_expense(db, data, current_user)
    return _to_response(expense)


@router.get("", response_model=List[ExpenseResponse])
def list_expenses(
    target_date: Optional[date] = Query(None),
    from_date: Optional[date] = Query(None),
    to_date: Optional[date] = Query(None),
    category: Optional[ExpenseCategory] = Query(None),
    min_amount: Optional[Decimal] = Query(None, ge=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    expenses = expense_service.get_expenses_filtered(
        db,
        current_user,
        target_date=target_date,
        category=category,
        from_date=from_date,
        to_date=to_date,
        min_amount=min_amount,
    )
    return [_to_response(e) for e in expenses]


@router.get("/summary", response_model=ExpenseDailySummary)
def expense_summary(target_date: Optional[date] = Query(None),db: Session = Depends(get_db), current_user: User = Depends(get_current_user),):
    expenses, total, count, date_str, by_category = (
        expense_service.get_daily_expense_summary(db, current_user, target_date)
    )
    return ExpenseDailySummary(  date=date_str,
        total_expenses=total,total_count=count,
        by_category=by_category,expenses=[_to_response(e) for e in expenses],)


@router.get("/{expense_id}", response_model=ExpenseResponse)
def get_expense( expense_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    expense = expense_service.get_expense(db, expense_id, current_user)
    return _to_response(expense)


@router.put("/{expense_id}", response_model=ExpenseResponse)
def update_expense( expense_id: int, data: ExpenseUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user),):
    expense = expense_service.update_expense(db, expense_id, data, current_user)
    return _to_response(expense)


@router.delete("/{expense_id}", status_code=204)
def delete_expense(expense_id: int,db: Session = Depends(get_db),current_user: User = Depends(get_current_user),):
    expense_service.delete_expense(db, expense_id, current_user)
    return None