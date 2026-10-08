from sqlalchemy.orm import Session
from typing import Optional
from fastapi import HTTPException, status
from sqlalchemy import func
from app.models.product import Product
from app.schemas.product import productcreate,Restock,productUpdate
from app.models.user import User


def createProduct(
    db: Session, data: productcreate, current_user: User, shop_id: Optional[int] = None
):
    shop_id = shop_id if shop_id is not None else current_user.shop_id
    if shop_id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Select a shop before creating products",
        )
    existing = db.query(Product).filter(Product.shop_id == shop_id,Product.name == data.name).first()
   
    if  existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"product'{data.name}' already exist in this shop")
    product = Product(shop_id=shop_id,
                      name=data.name,
                      description=data.description,
                     
                      #sku=data.sku,
                      selling_price=data.selling_price,
                      stock_quantity=data.stock_quantity,
                     low_stock=data.low_stock
                      )
    db.add(product)
    db.commit()
    db.refresh(product)
    return product
    
    
    
def get_products(db: Session,current_user: User,active_only : bool = True,
    search:Optional[str]=None,
    low_stock_only:bool = False,
    out_of_stock_only: bool = False,
    shop_id: Optional[int] = None,
):
    shop_id = shop_id if shop_id is not None else current_user.shop_id
    if shop_id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Select a shop before listing products",
        )
    query = db.query(Product).filter(Product.shop_id == shop_id)
    if active_only:
        query = query.filter(Product.Active == True)
    if search:
        term = f"%{search.strip()}%"
        query = query.filter((Product.name.ilike(term)))
    if low_stock_only:
        query = query.filter(Product.stock_quantity <= func.coalesce(Product.low_stock, 0))
    if out_of_stock_only:
        query = query.filter(Product.stock_quantity == 0)
    return query.order_by(Product.name).all()



def get_product(
    db: Session,
    product_id: int,
    current_user: User,
    shop_id: Optional[int] = None,
):
    shop_id = shop_id if shop_id is not None else current_user.shop_id
    product = (
        db.query(Product)
        .filter(Product.id == product_id, Product.shop_id == shop_id)
        .first()
    )
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    return product


def update_product(
    db: Session,
    product_id: int,
    data: productUpdate,
    current_user: User,
    shop_id: Optional[int] = None,
):
    """Admin updates product fields."""
    shop_id = shop_id if shop_id is not None else current_user.shop_id
    product = get_product(db, product_id, current_user, shop_id)
    update_data = data.model_dump(exclude_unset=True)

    if "name" in update_data and update_data["name"] != product.name:
      existing = db.query(Product).filter(Product.shop_id == shop_id, Product.name == update_data["name"], Product.id != product_id,).first()
      if existing:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail=f"Product '{update_data['name']}' already exists in this shop",)

    for field, value in update_data.items():
        setattr(product, "Active" if field == "active" else field, value)

    db.commit()
    db.refresh(product)
    return product    



def restock_product(
    db: Session,
    product_id: int,
    data: Restock,
    current_user: User,
    shop_id: Optional[int] = None,
):
   
    product = get_product(db, product_id, current_user, shop_id)

    if not product.Active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot restock an inactive product",
        )

    product.stock_quantity = product.stock_quantity + data.quantity
    db.commit()
    db.refresh(product)
    return product

def delete_product(
    db: Session,
    product_id: int,
    current_user: User,
    shop_id: Optional[int] = None,
):
    product = get_product(db, product_id, current_user, shop_id)
    product.Active = False
    db.commit()
    

def adjust_stock(db: Session, product: Product, quantity_change: int):
    new_stock = product.stock_quantity + quantity_change

    if new_stock < 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "Insufficient stock",
                "product": product.name,
                "available": product.stock_quantity,
                "requested": abs(quantity_change),
            },
        )    
    product.stock_quantity = new_stock
    return product