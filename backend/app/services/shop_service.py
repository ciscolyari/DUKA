
from datetime import datetime, timezone
from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.shop import Shop
from app.models.user import User, UserRole
from app.models.product import Product
from app.models.sale import Sale, SaleStatus
from app.schemas.shop import ShopUpdate


def get_my_shop(db: Session, current_admin: User):
    shop = db.query(Shop).filter(Shop.id == current_admin.shop_id).first()
    if not shop:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Shop not found")
    return shop


def update_my_shop(db: Session, current_admin: User, data: ShopUpdate):
    shop = get_my_shop(db, current_admin)

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(shop, field, value)

    db.commit()
    db.refresh(shop)
    return shop


def get_shop_dashboard(db: Session, current_admin: User) -> dict:
    shop = get_my_shop(db, current_admin)
    shop_id = current_admin.shop_id

    today = datetime.now(timezone.utc).date()
    start = datetime.combine(today, datetime.min.time()).replace(tzinfo=timezone.utc)
    end = datetime.combine(today, datetime.max.time()).replace(tzinfo=timezone.utc)

    # Mauzo ya leo — duka lake tu
    sales_totals = (
        db.query(func.coalesce(func.sum(Sale.total_amount), 0).label("total_sales"), func.count(Sale.id).label("transactions") )
        .filter(
            Sale.shop_id == shop_id,
            Sale.created_at >= start,
            Sale.created_at <= end,
            Sale.status == SaleStatus.SUBMITTED,
        )
        .one()
    )

    total_products = (
        db.query(func.count(Product.id))
        .filter(Product.shop_id == shop_id, Product.Active == True)
        .scalar()
    )

    total_employees = (
        db.query(func.count(User.id))
        .filter(
            User.shop_id == shop_id,
            User.role == UserRole.EMPLOYEE,
            User.active == True,
        )
        .scalar()
    )

    products = (db.query(Product).filter(Product.shop_id == shop_id, Product.Active == True).all())
    low_stock_count = sum( 1 for p in products if p.stock_quantity <= p.low_stock )

    return {
        "shop": shop,
        "today_date": today.isoformat(),
        "today_total_sales": Decimal(str(sales_totals.total_sales)),
        "today_transactions": sales_totals.transactions,
        "total_products": total_products or 0,
        "total_employees": total_employees or 0,
        "low_stock_count": low_stock_count,
    }