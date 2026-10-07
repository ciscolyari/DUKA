from app.models.user import User,UserRole
from app.models.product import Product
from app.models.sale_item import SaleItem
from app.models.sale import SaleStatus,Sale
from typing import Optional
from app.schemas.sale import SaleCreate
from app.services.product_service import adjust_stock
from fastapi import HTTPException,status
from sqlalchemy.orm import Session, joinedload
from decimal import Decimal
from datetime import datetime, timezone,date




def employee_sale_lock(sale:Sale, current_user:User):
    if current_user.role == UserRole.EMPLOYEE and (sale.is_locked or sale.status == SaleStatus.SUBMITTED):
        raise HTTPException(status_code=status.HTTP_403_FORBIDEN, detail={"message":"This sale is locked cannot modified", "sale_id": sale.id})
    
    
def employee_not_delete(sale: Sale, current_user: User):
    if current_user.role == UserRole.EMPLOYEE:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail={"message":"employeee cannot delete sales", "sale_id":sale.id}) 
    
def create_sale(db: Session, data: SaleCreate, current_user: User) -> Sale:
    if not data.items:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Sale must contain at least one item",
        )

    
    # product_quantity: dict[int, int] = {}
    # for item in data.items:
    #     product_quantity[item.product_id] = (
    #         product_quantity.get(item.product_id, 0) + item.quantity
        

    sale_item_data = []
    total_amount = Decimal("0.00")

    # for product_id, quantity in product_quantity.items():
    for item in data.items:
        product = (
            db.query(Product)
            .filter(
                Product.id == item.product_id,
                Product.shop_id == current_user.shop_id,
                Product.Active == True,  
            )
            .first()
        )
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Product with id {item.product_id} not found",
            )

        if product.stock_quantity < item.quantity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "message": "Insufficient stock",
                    "product": product.name,
                    "available": product.stock_quantity,
                    "requested": item.quantity,
                },
            )

        price = product.selling_price
        subtotal = price * item.quantity
        total_amount += subtotal   # ← MUHIMU

        sale_item_data.append({
            "product": product,
            "quantity": item.quantity,
            "price": price,  
            "subtotal": subtotal,
        })

    
    sale = Sale(
        shop_id=current_user.shop_id,
        employee_id=current_user.id,
        total_amount=total_amount,
        status=SaleStatus.SUBMITTED,
        is_locked=True,
    )
    db.add(sale)
    db.flush()  

    for item_data in sale_item_data:
        sale_item = SaleItem(
            sale_id=sale.id,
            product_id=item_data["product"].id,
            quantity=item_data["quantity"],
            price=item_data["price"],
            subtotal=item_data["subtotal"],
        )
        db.add(sale_item)
        adjust_stock(db, item_data["product"], -item_data["quantity"])

    db.commit()
    db.refresh(sale)

    sale = (
        db.query(Sale)
        .options(
            joinedload(Sale.items).joinedload(SaleItem.product),
            joinedload(Sale.employee),
        )
        .filter(Sale.id == sale.id)
        .first()
    )
    return sale  
    
    
    
def get_my_sales(
    db: Session,
    current_user: User,
    target_date: Optional[date] = None,
    from_date: Optional[date] = None,
    to_date: Optional[date] = None,
):
    if from_date and to_date and from_date > to_date:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="from_date must be on or before to_date",
        )

    query = (
        db.query(Sale)
        .options(
            joinedload(Sale.items).joinedload(SaleItem.product),
            joinedload(Sale.employee),
        )
        .filter(
            Sale.employee_id == current_user.id,
            Sale.shop_id == current_user.shop_id,
            Sale.status == SaleStatus.SUBMITTED,
        )
    )

    if from_date or to_date:
        if from_date:
            start = datetime.combine(from_date, datetime.min.time()).replace(tzinfo=timezone.utc)
            query = query.filter(Sale.created_at >= start)
        if to_date:
            end = datetime.combine(to_date, datetime.max.time()).replace(tzinfo=timezone.utc)
            query = query.filter(Sale.created_at <= end)
    else:
        target_date = target_date or datetime.now(timezone.utc).date()
        start = datetime.combine(target_date, datetime.min.time()).replace(tzinfo=timezone.utc)
        end = datetime.combine(target_date, datetime.max.time()).replace(tzinfo=timezone.utc)
        query = query.filter(Sale.created_at >= start, Sale.created_at <= end)

    return query.order_by(Sale.created_at.desc()).all()
        
        
        
        
def get_all_sales(db: Session,current_admin: User,target_date: Optional[date] = None,employee_id: Optional[int] = None,):
    if target_date is None:
        target_date = datetime.now(timezone.utc).date()

    start = datetime.combine(target_date, datetime.min.time()).replace(tzinfo=timezone.utc)
    end = datetime.combine(target_date, datetime.max.time()).replace(tzinfo=timezone.utc)

    query = (db.query(Sale).options(joinedload(Sale.items).joinedload(SaleItem.product), joinedload(Sale.employee),).filter( Sale.shop_id == current_admin.shop_id, Sale.created_at >= start, Sale.created_at <= end,
            Sale.status == SaleStatus.SUBMITTED,
        ))

    if employee_id is not None:
        query = query.filter(Sale.employee_id == employee_id)

    return query.order_by(Sale.created_at.desc()).all()



def get_sale(db: Session,sale_id: int,current_user: User,):
    query = (db.query(Sale).options(joinedload(Sale.items).joinedload(SaleItem.product),joinedload(Sale.employee),
        ).filter(Sale.id == sale_id,Sale.shop_id == current_user.shop_id,))

    if current_user.role == UserRole.EMPLOYEE:
        query = query.filter(Sale.employee_id == current_user.id)

    sale = query.first()
    if not sale:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Sale not found")
    return sale


def update_sale(db: Session,sale_id: int,current_user: User):
   
    sale = get_sale(db, sale_id, current_user)
    employee_sale_lock(sale, current_user)

    if current_user.role == UserRole.EMPLOYEE:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="Employees cannot edit sales",)

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN, detail="Sales cannot be edited after submission. Use cancel (Admin only) if needed.")


def delete_sale(db: Session,sale_id: int,current_user: User):
    sale = get_sale(db, sale_id, current_user)
    employee_not_delete(sale, current_user)

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail=("Sales cannot be deleted. ""An Administrator can cancel a sale using POST /api/sales/{id}/cancel."),)



def cancel_sale(db: Session,sale_id: int,current_admin: User,):
    sale = db.query(Sale).options(joinedload(Sale.items)).filter(Sale.id == sale_id,Sale.shop_id == current_admin.shop_id,).first()
    
    if not sale:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Sale not found",)

    if sale.status == SaleStatus.CANCELLED:
        raise HTTPException( status_code=status.HTTP_400_BAD_REQUEST, detail="Sale is already cancelled",)

    for item in sale.items:
        product = db.query(Product).filter(Product.id == item.product_id).first()
        if product:
            adjust_stock(db, product, item.quantity)

    sale.status = SaleStatus.CANCELLED
    sale.is_locked = True
    db.commit()
    db.refresh(sale)
    return sale