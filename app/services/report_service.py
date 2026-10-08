from datetime import date, datetime, time, timedelta, timezone
from decimal import Decimal

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.expense import Expense
from app.models.product import Product
from app.models.sale import Sale, SaleStatus
from app.models.sale_item import SaleItem
from app.models.subscription import Subscription
from app.models.user import User, UserRole


def _as_float(value) -> float:
    return float(value or Decimal("0"))


def _date_range(start_date: date, end_date: date) -> tuple[datetime, datetime]:
    start = datetime.combine(start_date, time.min, tzinfo=timezone.utc)
    end = datetime.combine(end_date + timedelta(days=1), time.min, tzinfo=timezone.utc)
    return start, end


def _daily_values(query, start_date: date, end_date: date) -> dict[date, float]:
    return {
        row_date: _as_float(total)
        for row_date, total in query
        if row_date is not None and start_date <= row_date <= end_date
    }


def summary(
    db: Session,
    admin: User,
    from_date: date,
    to_date: date,
) -> dict:
    if from_date > to_date:
        raise ValueError("from_date must be on or before to_date")

    start, end = _date_range(from_date, to_date)
    sales_scope = (
        db.query(Sale)
        .filter(
            Sale.shop_id == admin.shop_id,
            Sale.status == SaleStatus.SUBMITTED,
            Sale.created_at >= start,
            Sale.created_at < end,
        )
    )
    expense_scope = (
        db.query(Expense)
        .filter(
            Expense.shop_id == admin.shop_id,
            Expense.is_active.is_(True),
            Expense.created_at >= start,
            Expense.created_at < end,
        )
    )

    sales_by_date = _daily_values(
        db.query(func.date(Sale.created_at), func.sum(Sale.total_amount))
        .filter(
            Sale.shop_id == admin.shop_id,
            Sale.status == SaleStatus.SUBMITTED,
            Sale.created_at >= start,
            Sale.created_at < end,
        )
        .group_by(func.date(Sale.created_at)),
        from_date,
        to_date,
    )
    expenses_by_date = _daily_values(
        db.query(func.date(Expense.created_at), func.sum(Expense.amount))
        .filter(
            Expense.shop_id == admin.shop_id,
            Expense.is_active.is_(True),
            Expense.created_at >= start,
            Expense.created_at < end,
        )
        .group_by(func.date(Expense.created_at)),
        from_date,
        to_date,
    )

    trend = []
    current_date = from_date
    while current_date <= to_date:
        trend.append(
            {
                "date": current_date.isoformat(),
                "sales": sales_by_date.get(current_date, 0),
                "expenses": expenses_by_date.get(current_date, 0),
            }
        )
        current_date += timedelta(days=1)

    top_products = (
        db.query(Product.name, func.sum(SaleItem.quantity))
        .join(SaleItem, SaleItem.product_id == Product.id)
        .join(Sale, Sale.id == SaleItem.sale_id)
        .filter(
            Sale.shop_id == admin.shop_id,
            Sale.status == SaleStatus.SUBMITTED,
            Sale.created_at >= start,
            Sale.created_at < end,
        )
        .group_by(Product.id, Product.name)
        .order_by(func.sum(SaleItem.quantity).desc())
        .limit(10)
        .all()
    )
    employee_totals = (
        db.query(User.full_name, func.sum(Sale.total_amount))
        .join(Sale, Sale.employee_id == User.id)
        .filter(
            Sale.shop_id == admin.shop_id,
            Sale.status == SaleStatus.SUBMITTED,
            Sale.created_at >= start,
            Sale.created_at < end,
        )
        .group_by(User.id, User.full_name)
        .order_by(func.sum(Sale.total_amount).desc())
        .all()
    )
    category_totals = (
        db.query(Expense.category, func.sum(Expense.amount))
        .filter(
            Expense.shop_id == admin.shop_id,
            Expense.is_active.is_(True),
            Expense.created_at >= start,
            Expense.created_at < end,
        )
        .group_by(Expense.category)
        .order_by(func.sum(Expense.amount).desc())
        .all()
    )

    today = date.today()
    today_start, today_end = _date_range(today, today)
    today_sales = _as_float(
        db.query(func.sum(Sale.total_amount))
        .filter(
            Sale.shop_id == admin.shop_id,
            Sale.status == SaleStatus.SUBMITTED,
            Sale.created_at >= today_start,
            Sale.created_at < today_end,
        )
        .scalar()
    )
    today_expenses = _as_float(
        db.query(func.sum(Expense.amount))
        .filter(
            Expense.shop_id == admin.shop_id,
            Expense.is_active.is_(True),
            Expense.created_at >= today_start,
            Expense.created_at < today_end,
        )
        .scalar()
    )

    subscription = (
        db.query(Subscription)
        .filter(
            Subscription.shop_id == admin.shop_id,
            Subscription.is_current.is_(True),
            Subscription.is_active.is_(True),
        )
        .order_by(Subscription.created_at.desc())
        .first()
    )
    subscription_plan = subscription.plan if subscription else None
    days_left = subscription.days_remaining() if subscription else None

    return {
        "today_sales": today_sales,
        "today_expenses": today_expenses,
        "total_sales": _as_float(sales_scope.with_entities(func.sum(Sale.total_amount)).scalar()),
        "total_expenses": _as_float(expense_scope.with_entities(func.sum(Expense.amount)).scalar()),
        "products": db.query(func.count(Product.id))
        .filter(Product.shop_id == admin.shop_id, Product.Active.is_(True))
        .scalar(),
        "low_stock": db.query(func.count(Product.id))
        .filter(
            Product.shop_id == admin.shop_id,
            Product.Active.is_(True),
            Product.stock_quantity <= 10,
        )
        .scalar(),
        "employees": db.query(func.count(User.id))
        .filter(
            User.shop_id == admin.shop_id,
            User.role == UserRole.EMPLOYEE,
            User.active.is_(True),
        )
        .scalar(),
        "plan": subscription_plan.name if subscription_plan else None,
        "days_left": days_left,
        "trend": trend,
        "top_products": [
            {"name": name, "qty": int(quantity or 0)}
            for name, quantity in top_products
        ],
        "by_employee": [
            {"name": name, "total": _as_float(total)}
            for name, total in employee_totals
        ],
        "by_category": [
            {"category": category.value, "total": _as_float(total)}
            for category, total in category_totals
        ],
    }


def employee_summary(db: Session, employee: User, today: date | None = None) -> dict:
    today = today or date.today()
    from_date = today - timedelta(days=6)
    start, end = _date_range(from_date, today)
    totals = _daily_values(
        db.query(func.date(Sale.created_at), func.sum(Sale.total_amount))
        .filter(
            Sale.shop_id == employee.shop_id,
            Sale.employee_id == employee.id,
            Sale.status == SaleStatus.SUBMITTED,
            Sale.created_at >= start,
            Sale.created_at < end,
        )
        .group_by(func.date(Sale.created_at)),
        from_date,
        today,
    )

    trend = []
    current_date = from_date
    while current_date <= today:
        trend.append(
            {
                "date": current_date.isoformat(),
                "total": totals.get(current_date, 0),
            }
        )
        current_date += timedelta(days=1)

    return {
        "week_total": sum(day["total"] for day in trend),
        "trend": trend,
    }