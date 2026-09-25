from fastapi import APIRouter,Depends,Query
from typing import Optional,List
from app.dependencies.auth import get_current_user,get_current_admin
from app. core.database import get_db
from sqlalchemy.orm import Session
from app. models.user import User
from app.services import product_service
from app.schemas.product import productcreate,Response,productUpdate,Restock


router = APIRouter(
    prefix="/products",
    tags=["products"]
)


def to_response(product):
    return Response(
        id=product.id,
        shop_id=product.shop_id,
        name=product.name,
        description=product.description,
        sku=product.sku,
        selling_price=product.selling_price,
        stock_quantity=product.stock_quantity,
        low_stock=product.low_stock_threshold,
        is_low_stock=product.is_low_stock,
        active=product.is_active,
        created_at=product.created_at,
        updated_at=product.updated_at,)
    


@router.post("", response_model=Response, status_code=201)
def create_product(
    data: productcreate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin),
):
    product = product_service.createProduct(db, data, current_admin)
    return to_response(product)


@router.get("", response_model=List[Response])
def list_products(
    active_only: bool = Query(True),
    search: Optional[str] = Query(None),
    low_stock_only: bool = Query(False),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    products = product_service.get_products(
        db, current_user, active_only, search, low_stock_only
    )
    return [to_response(p) for p in products]

@router.get("/{product_id}", response_model=Response)
def get_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    product = product_service.get_product(db, product_id, current_user)
    return to_response(product)


@router.put("/{product_id}", response_model=Response)
def update_product(
    product_id: int,
    data: productUpdate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin),
):
    product = product_service.update_product(db, product_id, data, current_admin)
    return to_response(product)

@router.post("/{product_id}/restock", response_model=Response)
def restock_product(
    product_id: int,
    data: Restock,db: Session = Depends(get_db),current_admin: User = Depends(get_current_admin),):
    product = product_service.restock_product(db, product_id, data, current_admin)
    return to_response(product)


@router.delete("/{product_id}", status_code=204)
def delete_product(product_id: int, db: Session = Depends(get_db), current_admin: User = Depends(get_current_admin),):
    product_service.delete_product(db, product_id, current_admin)
    return None

