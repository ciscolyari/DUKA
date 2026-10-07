from datetime import date, datetime, time, timedelta, timezone
from decimal import Decimal
from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.expense import Expense
from app.models.product import Product
from app.models.sale import Sale, SaleStatus
from app.models.sale_item import SaleItem
from app.models.shop import Shop
from app.models.subscription import Subscription, SubscriptionPlan
from app.models.user import User, UserRole


def _period(
    from_date: Optional[date],
    to_date: Optional[date],
) -> tuple[date, date]:
    today = datetime.now(timezone.utc).date()
    start_date = from_date or to_date or today
    end_date = to_date or (today if from_date else start_date)
    if start_date > end_date:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="from_date must be on or before to_date",
        )
    return start_date, end_date


def _day_start(day: date) -> datetime:
    return datetime.combine(day, time.min).replace(tzinfo=timezone.utc)


def _day_end(day: date) -> datetime:
    return datetime.combine(day, time.max).replace(tzinfo=timezone.utc)


def _decimal(value) -> Decimal:
    return Decimal(str(value or 0))


def _date_key(value) -> str:
    return value.isoformat() if isinstance(value, date) else str(value)


def _sales_total(db: Session, shop_id: int, start: datetime, end: datetime) -> Decimal:
    total = (
        db.query(func.coalesce(func.sum(Sale.total_amount), 0))
        .filter(
            Sale.shop_id == shop_id,
            Sale.status == SaleStatus.SUBMITTED,
            Sale.created_at >= start,
            Sale.created_at <= end,
        )
        .scalar()
    )
    return _decimal(total)


def _expenses_total(db: Session, shop_id: int, start: datetime, end: datetime) -> Decimal:
    total = (
        db.query(func.coalesce(func.sum(Expense.amount), 0))
        .filter(
            Expense.shop_id == shop_id,
            Expense.is_active == True,
            Expense.created_at >= start,
            Expense.created_at <= end,
        )
        .scalar()
    )
    return _decimal(total)


def get_admin_summary(
    db: Session,
    current_admin: User,
    from_date: Optional[date] = None,
    to_date: Optional[date] = None,
) -> dict:
    start_date, end_date = _period(from_date, to_date)
    start, end = _day_start(start_date), _day_end(end_date)
    shop_id = current_admin.shop_id
    shop = db.query(Shop).filter(Shop.id == shop_id).first()
    if shop is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Shop not found")

    sales_by_day = {
        _date_key(day): total
        for day, total in db.query(func.date(Sale.created_at), func.sum(Sale.total_amount))
        .filter(
            Sale.shop_id == shop_id,
            Sale.status == SaleStatus.SUBMITTED,
            Sale.created_at >= start,
            Sale.created_at <= end,
        )
        .group_by(func.date(Sale.created_at))
        .all()
    }
    expenses_by_day = {
        _date_key(day): total
        for day, total in db.query(func.date(Expense.created_at), func.sum(Expense.amount))
        .filter(
            Expense.shop_id == shop_id,
            Expense.is_active == True,
            Expense.created_at >= start,
            Expense.created_at <= end,
        )
        .group_by(func.date(Expense.created_at))
        .all()
    }

    trend = []
    day = start_date
    while day <= end_date:
        key = day.isoformat()
        trend.append({
            "date": key,
            "sales": _decimal(sales_by_day.get(key)),
            "expenses": _decimal(expenses_by_day.get(key)),
        })
        day += timedelta(days=1)

    top_products = (
        db.query(Product.name, func.sum(SaleItem.quantity).label("qty"))
        .join(SaleItem, SaleItem.product_id == Product.id)
        .join(Sale, Sale.id == SaleItem.sale_id)
        .filter(
            Sale.shop_id == shop_id,
            Sale.status == SaleStatus.SUBMITTED,
            Sale.created_at >= start,
            Sale.created_at <= end,
        )
        .group_by(Product.id, Product.name)
        .order_by(func.sum(SaleItem.quantity).desc())
        .limit(10)
        .all()
    )
    by_employee = (
        db.query(User.full_name.label("name"), func.sum(Sale.total_amount).label("total"))
        .join(Sale, Sale.employee_id == User.id)
        .filter(
            Sale.shop_id == shop_id,
            Sale.status == SaleStatus.SUBMITTED,
            Sale.created_at >= start,
            Sale.created_at <= end,
        )
        .group_by(User.id, User.full_name)
        .order_by(func.sum(Sale.total_amount).desc())
        .all()
    )
    by_category = (
        db.query(Expense.category, func.sum(Expense.amount).label("total"))
        .filter(
            Expense.shop_id == shop_id,
            Expense.is_active == True,
            Expense.created_at >= start,
            Expense.created_at <= end,
        )
        .group_by(Expense.category)
        .order_by(func.sum(Expense.amount).desc())
        .all()
    )

    today = datetime.now(timezone.utc).date()
    today_start, today_end = _day_start(today), _day_end(today)
    total_products = (
        db.query(func.count(Product.id))
        .filter(Product.shop_id == shop_id, Product.Active == True)
        .scalar()
    )
    low_stock = (
        db.query(func.count(Product.id))
        .filter(
            Product.shop_id == shop_id,
            Product.Active == True,
            Product.stock_quantity <= func.coalesce(Product.low_stock, 0),
        )
        .scalar()
    )
    employees = (
        db.query(func.count(User.id))
        .filter(
            User.shop_id == shop_id,
            User.role == UserRole.EMPLOYEE,
            User.active == True,
        )
        .scalar()
    )

    current_plan = (
        db.query(SubscriptionPlan.name, Subscription.expires_at)
        .join(Subscription, Subscription.plan_id == SubscriptionPlan.id)
        .filter(
            Subscription.shop_id == shop_id,
            Subscription.is_current == True,
            Subscription.is_active == True,
        )
        .order_by(Subscription.created_at.desc())
        .first()
    )
    plan = current_plan.name if current_plan else None
    if current_plan and current_plan.expires_at:
        expires_at = current_plan.expires_at
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)
        days_left = max(0, (expires_at.date() - today).days)
    else:
        days_left = shop.days_remaining()

    return {
        "today_sales": _sales_total(db, shop_id, today_start, today_end),
        "today_expenses": _expenses_total(db, shop_id, today_start, today_end),
        "total_sales": _sales_total(db, shop_id, start, end),
        "total_expenses": _expenses_total(db, shop_id, start, end),
        "products": total_products or 0,
        "low_stock": low_stock or 0,
        "employees": employees or 0,
        "plan": plan,
        "days_left": days_left,
        "trend": trend,
        "top_products": [{"name": name, "qty": qty} for name, qty in top_products],
        "by_employee": [{"name": name, "total": _decimal(total)} for name, total in by_employee],
        "by_category": [
            {"category": category.value, "total": _decimal(total)}
            for category, total in by_category
        ],
    }


def get_employee_summary(db: Session, current_user: User) -> dict:
    today = datetime.now(timezone.utc).date()
    start_date = today - timedelta(days=6)
    start, end = _day_start(start_date), _day_end(today)
    rows = (
        db.query(func.date(Sale.created_at), func.sum(Sale.total_amount))
        .filter(
            Sale.shop_id == current_user.shop_id,
            Sale.employee_id == current_user.id,
            Sale.status == SaleStatus.SUBMITTED,
            Sale.created_at >= start,
            Sale.created_at <= end,
        )
        .group_by(func.date(Sale.created_at))
        .all()
    )
    totals_by_day = {_date_key(day): _decimal(total) for day, total in rows}
    trend = []
    day = start_date
    while day <= today:
        key = day.isoformat()
        trend.append({"date": key, "total": totals_by_day.get(key, Decimal("0.00"))})
        day += timedelta(days=1)

    return {
        "week_total": sum(totals_by_day.values(), Decimal("0.00")),
        "trend": trend,
    }