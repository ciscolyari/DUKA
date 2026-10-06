from datetime import datetime, timezone, date
from decimal import Decimal
from typing import List, Optional, Tuple

from fastapi import HTTPException, status
from sqlalchemy.orm import Session, joinedload

from app.models.expense import Expense, ExpenseCategory
from app.models.user import User, UserRole
from app.schemas.expense import ExpenseCreate, ExpenseUpdate


def create_expense(db: Session, data: ExpenseCreate, current_user: User):
    expense = Expense(
        shop_id=current_user.shop_id,
        recorded_by_id=current_user.id,
        category=data.category,
        description=data.description,
        amount=data.amount,
        notes=data.notes,
    )
    db.add(expense)
    db.commit()
    db.refresh(expense)

    return (
        db.query(Expense).options(joinedload(Expense.recorded_by)) .filter(Expense.id == expense.id) .first())


def get_expenses(
    db: Session,
    current_user: User,
    target_date: Optional[date] = None,
    category: Optional[ExpenseCategory] = None,
    my_only: bool = False,):
    if target_date is None:
        target_date = datetime.now(timezone.utc).date()

    start = datetime.combine(target_date, datetime.min.time()).replace(tzinfo=timezone.utc)
    end = datetime.combine(target_date, datetime.max.time()).replace(tzinfo=timezone.utc)

    query = (
        db.query(Expense)
        .options(joinedload(Expense.recorded_by))
        .filter(
            Expense.shop_id == current_user.shop_id,
            Expense.is_active == True,
            Expense.created_at >= start,
            Expense.created_at <= end,
        )
    )

    if current_user.role == UserRole.EMPLOYEE or my_only:
        query = query.filter(Expense.recorded_by_id == current_user.id)

    if category is not None:
        query = query.filter(Expense.category == category)

    return query.order_by(Expense.created_at.desc()).all()


def get_expense(db: Session, expense_id: int, current_user: User):
    expense = (db.query(Expense).options(joinedload(Expense.recorded_by)) .filter(Expense.id == expense_id, Expense.shop_id == current_user.shop_id,
            Expense.is_active == True,
        ) .first())
    if not expense:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Expense not found")

    if current_user.role == UserRole.EMPLOYEE and expense.recorded_by_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only view your own expenses",
        )
    return expense


def update_expense(
    db: Session, expense_id: int, data: ExpenseUpdate, current_user: User):
    expense = get_expense(db, expense_id, current_user)

    if current_user.role == UserRole.EMPLOYEE and expense.recorded_by_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only edit your own expenses",
        )

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(expense, field, value)

    db.commit()
    db.refresh(expense)
    return expense


def delete_expense(db: Session, expense_id: int, current_user: User) -> None:
    expense = get_expense(db, expense_id, current_user)

    if current_user.role == UserRole.EMPLOYEE and expense.recorded_by_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete your own expenses",
        )

    expense.is_active = False
    db.commit()


def get_daily_expense_summary(db: Session,current_user: User,target_date: Optional[date] = None,):
    expenses = get_expenses(db,current_user,target_date=target_date,my_only=(current_user.role == UserRole.EMPLOYEE))

    if target_date is None:
        target_date = datetime.now(timezone.utc).date()

    total_expenses = sum((e.amount for e in expenses), Decimal("0.00"))
    total_count = len(expenses)

    category_totals: dict = {}
    for e in expenses:
        key = e.category.value
        category_totals[key] = category_totals.get(key, Decimal("0.00")) + e.amount

    by_category = [
        {"category": cat, "total": total}
        for cat, total in sorted(category_totals.items(), key=lambda x: x[1], reverse=True)
    ]

    return expenses, total_expenses, total_count, target_date.isoformat(), by_category