from datetime import datetime, timezone
import enum
from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Numeric, Enum
from sqlalchemy.orm import relationship
from app.core.database import Base


class SaleStatus(str, enum.Enum):
    SUBMITTED = "submitted"
    CANCELLED = "cancelled"


class Sale(Base):
    __tablename__ = "sales"

    id = Column(Integer, primary_key=True)
    shop_id = Column(Integer, ForeignKey("shops.id",ondelete="CASCADE"))
    employee_id = Column(Integer, ForeignKey("users.id",ondelete="CASCADE"))

    total_amount = Column(Numeric(12, 2), nullable=False)
    note = Column(String(120), nullable=True)
    status = Column(Enum(SaleStatus), nullable=False, default=SaleStatus.SUBMITTED)
    is_locked = Column(Boolean, default=True, nullable=False)

    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False, index=True)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    shop = relationship("Shop", back_populates="sales")
    employee = relationship("User", back_populates="sales")
    items = relationship("SaleItem", back_populates="sale")

 