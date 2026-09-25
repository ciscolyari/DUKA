from datetime import datetime, timezone
from sqlalchemy import (Column,Integer,String,DateTime,Boolean,ForeignKey,Numeric,Text,CheckConstraint,UniqueConstraint,)
from sqlalchemy.orm import relationship
from app.core.database import Base


class Product(Base):
    __tablename__ = "products"


    id = Column(Integer, primary_key=True)
    shop_id = Column(Integer, ForeignKey("shops.id"), nullable=False, index=True)

    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    selling_price = Column(Numeric(12, 2), nullable=False)
    stock_quantity = Column(Integer, nullable=False, default=0)
    #low_stock = Column(Integer,nullable=True,default=0)
    Active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    shop = relationship("Shop", back_populates="products")
    sale_items = relationship("SaleItem",foreign_keys="SaleItem.product_id ", back_populates="product")
