from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Boolean, DateTime,ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base


class Shop(Base):
    __tablename__ = "shops"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    location = Column(String, nullable=False)
    Active = Column(Boolean, default=True, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    users = relationship("User", back_populates="shop")
    products = relationship("Product", back_populates="shop")
    sales = relationship("Sale", back_populates="shop")

