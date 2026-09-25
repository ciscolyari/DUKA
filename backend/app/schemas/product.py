from pydantic import BaseModel,Field
from typing import Optional
from decimal import Decimal
from datetime import datetime


class Product(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    description: Optional[str] = None
    #sku:Optional[str] = Field(None, max_length=100)
    selling_price: Decimal =Field(gt=0)
    stock_quantity: int = Field(ge=0)
    #low_stock: int = Field(10, ge=0)
    
class productcreate(Product):
    pass


class productUpdate(BaseModel):
        name: Optional[str]= Field(None)
        description: Optional[str] = None
        #sku: Optional[str] = None
        selling_price: Decimal = Field(gt=0)
        stock_quantity: int =Field(ge=0)
        #low_stock: Optional[int] = Field(None, ge=0)
        active: Optional[bool]=None
        
class Restock(BaseModel):
    quantity: int =Field(gt=0)
    note: str = Field(max_length=100)
    


class Response(BaseModel):
    id:int
    shop_id: int
    name : str
    description: Optional[str]
    #sku: Optional[str]
    selling_price: Decimal
    stock_quantity: int
    #low_stock: bool= False
    active:bool
    created_at:datetime
    updated_at:datetime
    
    
    class Config:
        from_attributes =True
            