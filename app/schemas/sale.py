from pydantic import BaseModel,Field
from typing import List, Optional
from decimal import Decimal
from app.models.sale import SaleStatus
from datetime import datetime



class SaleItemCreate(BaseModel):
    product_id: int
    quantity: int=Field(gt=0)
    price:Decimal=Field(gt=0, description="selling price")
    
    
class SaleCreate(BaseModel):
    items: List[SaleItemCreate] = Field(min_length=2)
    
    
class SaleItemResponse(BaseModel):
    id: int
    product_id:int
    product_name:Optional[str] = None  
    quantity: int
    price: Decimal      
    subtotal: Decimal
    
    class config:
        from_attributes = True
        
        
        
class SaleResponse(BaseModel):
    id : int
    shop_id:int
    employee_id:int
    #price: Decimal
    employee_name: Optional[str]= None
    total_amount: Decimal
    status: SaleStatus
    is_locked:bool
    items: List[SaleItemResponse] = []
    created_at: datetime        
    
    class config:
        from_attributes = True
        
class MySalesSummary(BaseModel):
    date: str
    total_transactions:int
    main_total: Decimal
    sales: List[SaleResponse] = []
    
    
class DailySaleSummary(BaseModel):
    date: int
    total_sales: Decimal
    total_transactions: int
    by_employee:List[dict] = []
    by_product: List[dict] = []            