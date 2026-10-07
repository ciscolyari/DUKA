"""
EXPENSE MODEL
=============
Matumizi: umeme, taka, maji, usafiri, n.k.
"""

from datetime import datetime, timezone
import enum

from sqlalchemy import (
    Column, Integer, String, DateTime, Boolean,
    ForeignKey, Numeric, Text, Enum,
)
from sqlalchemy.orm import relationship
from app.core.database import Base


class ExpenseCategory(str, enum.Enum):
    ELECTRICITY = "electricity"   
    WATER = "water"               
    WASTE = "waste"               
    TRANSPORT = "transport"       
    RENT = "rent"                 
    SUPPLIES = "supplies"         
    OTHER = "other"               


class Expense(Base):
    __tablename__ = "expenses"

    id = Column(Integer, primary_key=True, index=True)
    shop_id = Column(Integer, ForeignKey("shops.id"), nullable=False, index=True)
    recorded_by_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    category = Column(Enum(ExpenseCategory), nullable=False, default=ExpenseCategory.OTHER)
    description = Column(String(500), nullable=False)
    amount = Column(Numeric(12, 2), nullable=False)
    notes = Column(Text, nullable=True)

    is_active = Column(Boolean, default=True, nullable=False)

    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True,
    )
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    shop = relationship("Shop", backref="expenses")
    recorded_by = relationship("User", backref="expenses")
    recorded_by = relationship("User", back_populates="expenses")