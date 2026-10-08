
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.dependencies.auth import get_current_admin
from app.models.shop import Shop
from app.models.user import User
from app.schemas.shop import ShopCreate, ShopResponse, ShopUpdate, ShopDashboardResponse
from app.services import shop_service

router = APIRouter(prefix="/api/shops", tags=["Shop"])


def _serialize_shop(shop: Shop) -> ShopResponse:
    return ShopResponse(
        id=shop.id,
        name=shop.name,
        location=shop.location,
        address=shop.address,
        phone=shop.phone,
        Active=shop.Active,
        created_at=shop.created_at,
    )


@router.get("", response_model=list[ShopResponse])
def list_my_shops(db: Session = Depends(get_db), current_admin: User = Depends(get_current_admin)):
    shops = db.query(Shop).order_by(Shop.created_at.desc()).all()
    return [_serialize_shop(s) for s in shops]


@router.post("", response_model=ShopResponse, status_code=status.HTTP_201_CREATED)
def create_my_shop(data: ShopCreate, db: Session = Depends(get_db), current_admin: User = Depends(get_current_admin)):
    shop = Shop(
        name=data.name,
        location=data.location or "",
        address=data.address,
        phone=data.phone,
        is_active=True,
    )
    db.add(shop)
    db.flush()

    if current_admin.shop_id is None:
        current_admin.shop_id = shop.id
        db.add(current_admin)

    db.commit()
    db.refresh(shop)
    return _serialize_shop(shop)


@router.get("/me", response_model=ShopResponse)
def get_my_shop(db: Session = Depends(get_db), current_admin: User = Depends(get_current_admin)):
    if current_admin.shop_id is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Shop not found")
    return _serialize_shop(shop_service.get_my_shop(db, current_admin))


@router.get("/{shop_id}", response_model=ShopResponse)
def get_shop(shop_id: int, db: Session = Depends(get_db), current_admin: User = Depends(get_current_admin)):
    shop = db.query(Shop).filter(Shop.id == shop_id).first()
    if not shop:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Shop not found")
    return _serialize_shop(shop)


@router.get("/dashboard", response_model=ShopDashboardResponse)
def shop_dashboard(db: Session = Depends(get_db), current_admin: User = Depends(get_current_admin)):
    data = shop_service.get_shop_dashboard(db, current_admin)
    shop = data["shop"]
    return ShopDashboardResponse(
        shop=_serialize_shop(shop),
        today_date=data["today_date"],
        today_total_sales=data["today_total_sales"],
        today_transactions=data["today_transactions"],
        total_products=data["total_products"],
        total_employees=data["total_employees"],
        low_stock_count=data["low_stock_count"],
    )


@router.put("/{shop_id}", response_model=ShopResponse)
def update_shop(shop_id: int, data: ShopUpdate, db: Session = Depends(get_db), current_admin: User = Depends(get_current_admin)):
    shop = db.query(Shop).filter(Shop.id == shop_id).first()
    if not shop:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Shop not found")

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(shop, field, value)

    db.commit()
    db.refresh(shop)
    return _serialize_shop(shop)


@router.put("", response_model=ShopResponse)
def update_my_shop(data: ShopUpdate, db: Session = Depends(get_db), current_admin: User = Depends(get_current_admin)):
    if current_admin.shop_id is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Shop not found")
    return update_shop(current_admin.shop_id, data, db, current_admin)