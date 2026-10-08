
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.dependencies.auth import get_current_admin
from app.models.user import User
from app.schemas.shop import ShopResponse, ShopUpdate, ShopDashboardResponse
from app.services import shop_service

router = APIRouter(prefix="/api/shop",
                   tags=["Shop"])


@router.get("", response_model=ShopResponse)
def get_my_shop( db: Session = Depends(get_db),  current_admin: User = Depends(get_current_admin)):
    return shop_service.get_my_shop(db, current_admin)


@router.get("/dashboard", response_model=ShopDashboardResponse)
def shop_dashboard( db: Session = Depends(get_db), current_admin: User = Depends(get_current_admin),):
    data = shop_service.get_shop_dashboard(db, current_admin)
    shop = data["shop"]
    return ShopDashboardResponse(
        shop=ShopResponse(
            id=shop.id,
            name=shop.name,
            location=shop.location,
            Active=shop.Active,
            created_at=shop.created_at,
        ),
        today_date=data["today_date"],
        today_total_sales=data["today_total_sales"],
        today_transactions=data["today_transactions"],
        total_products=data["total_products"],
        total_employees=data["total_employees"],
        low_stock_count=data["low_stock_count"],
    )


@router.put("", response_model=ShopResponse)
def update_my_shop( data: ShopUpdate, db: Session = Depends(get_db), current_admin: User = Depends(get_current_admin)):
    return shop_service.update_my_shop(db, current_admin, data)