from datetime import date
from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.dependencies.auth import get_current_user, get_current_admin, get_active_shop_id
from app.models.user import User
from app.schemas.sale import SaleCreate, SaleResponse, SaleItemResponse
from app.services import sale_service

router = APIRouter(
    prefix="/api/sales", 
    tags=["Sales"])


def _build_sale_response(sale) -> SaleResponse:
    items = [
        SaleItemResponse(
            id=item.id,
            product_id=item.product_id,
            product_name=item.product.name if item.product else None,
            quantity=item.quantity,
            price=item.price,
            subtotal=item.subtotal,
        )
        for item in sale.items
    ]
    return SaleResponse(
        id=sale.id,
        shop_id=sale.shop_id,
        employee_id=sale.employee_id,
        employee_name=sale.employee.full_name if sale.employee else None,
        total_amount=sale.total_amount,
        status=sale.status,
        is_locked=sale.is_locked,
        note=sale.note,
        items=items,
        created_at=sale.created_at,
    )



@router.post("", response_model=SaleResponse, status_code=201)
def create_sale(
    data: SaleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    shop_id: int = Depends(get_active_shop_id),
):
    sale = sale_service.create_sale(db, data, current_user, shop_id)
    return _build_sale_response(sale)



@router.get("/me", response_model=List[SaleResponse])
def my_sales(
    target_date: Optional[date] = Query(None, description="YYYY-MM-DD (default: today)"),
    from_date: Optional[date] = Query(None, description="Inclusive start date"),
    to_date: Optional[date] = Query(None, description="Inclusive end date"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    shop_id: int = Depends(get_active_shop_id),
):
    sales = sale_service.get_my_sales(
        db, current_user, target_date, from_date, to_date, shop_id
    )
    return [_build_sale_response(s) for s in sales]



@router.get("", response_model=List[SaleResponse])
def list_all_sales(
    target_date: Optional[date] = Query(None, description="YYYY-MM-DD (default: today)"),
    employee_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin),
    shop_id: int = Depends(get_active_shop_id),
):
   
    sales = sale_service.get_all_sales(
        db, current_admin, target_date, employee_id, shop_id
    )
    return [_build_sale_response(s) for s in sales]



@router.get("/{sale_id}", response_model=SaleResponse)
def get_sale(
    sale_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    shop_id: int = Depends(get_active_shop_id),
):
  
    sale = sale_service.get_sale(db, sale_id, current_user, shop_id)
    return _build_sale_response(sale)



@router.put("/{sale_id}")
def update_sale(
    sale_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    shop_id: int = Depends(get_active_shop_id),
):
   
    sale_service.update_sale(db, sale_id, current_user, shop_id)



@router.delete("/{sale_id}")
def delete_sale(
    sale_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    shop_id: int = Depends(get_active_shop_id),
):
   
    sale_service.delete_sale(db, sale_id, current_user, shop_id)



@router.post("/{sale_id}/cancel", response_model=SaleResponse)
def cancel_sale(
    sale_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin),
    shop_id: int = Depends(get_active_shop_id),
):
   
    sale = sale_service.cancel_sale(db, sale_id, current_admin, shop_id)
    return _build_sale_response(sale)