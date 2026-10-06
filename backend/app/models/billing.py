from datetime import datetime, timezone
import enum
from sqlalchemy import (
    Column, Integer, String, DateTime, Boolean,
    ForeignKey, Enum, Numeric, Text, UniqueConstraint,
)
from sqlalchemy.orm import relationship
from app.core.database import Base


class BillingStatus(str, enum.Enum):
    PENDING = "pending"
    SUCCESS = "success"
    FAILED = "failed"
    REFUNDED = "refunded"


class Billing(Base):
    __tablename__ = "billings"

    id = Column(Integer, primary_key=True, index=True)
    shop_id = Column(Integer, ForeignKey("shops.id"), nullable=False, index=True)
    subscription_id = Column(Integer, ForeignKey("subscriptions.id"), nullable=False, index=True)
    paid_by_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    plan = Column(String(50), nullable=False)
    amount = Column(Numeric(12, 2), nullable=False)
    currency = Column(String(10), nullable=False, default="TZS")
    transaction_ref = Column(String(255), nullable=True, index=True)
    payment_date = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    status = Column(Enum(BillingStatus), nullable=False, default=BillingStatus.SUCCESS)
    notes = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)

    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    shop = relationship("Shop", backref="billings")
    subscription = relationship("Subscription", backref="billings")
    paid_by = relationship("User", backref="billings")
    invoice = relationship("Invoice", back_populates="billing", uselist=False, cascade="all, delete-orphan")


class Invoice(Base):
    __tablename__ = "invoices"
    __table_args__ = (UniqueConstraint("invoice_number", name="uq_invoice_number"),)

    id = Column(Integer, primary_key=True, index=True)
    billing_id = Column(Integer, ForeignKey("billings.id"), nullable=False, unique=True, index=True)
    shop_id = Column(Integer, ForeignKey("shops.id"), nullable=False, index=True)
    subscription_id = Column(Integer, ForeignKey("subscriptions.id"), nullable=False, index=True)

    invoice_number = Column(String(50), nullable=False, index=True)
    amount = Column(Numeric(12, 2), nullable=False)
    currency = Column(String(10), nullable=False, default="TZS")
    issued_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)

    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    billing = relationship("Billing", back_populates="invoice")
    shop = relationship("Shop", backref="invoices")
    subscription = relationship("Subscription", backref="invoices")