from datetime import datetime, timezone
import enum
from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Enum, Numeric
from sqlalchemy.orm import relationship
from app.core.database import Base


class SubscriptionPlan(str, enum.Enum):
    TRIAL = "trial"
    BASIC = "basic"
    STANDARD = "standard"
    PREMIUM = "premium"


class SubscriptionStatus(str, enum.Enum):
    ACTIVE = "active"
    EXPIRED = "expired"
    CANCELLED = "cancelled"


PLAN_LIMITS = {
    SubscriptionPlan.TRIAL:    {"max_employees": 2,  "max_products": 50,    "days": 14, "price": 0},
    SubscriptionPlan.BASIC:    {"max_employees": 5,  "max_products": 200,   "days": 30, "price": 15000},
    SubscriptionPlan.STANDARD: {"max_employees": 15, "max_products": 1000,  "days": 30, "price": 35000},
    SubscriptionPlan.PREMIUM:  {"max_employees": 50, "max_products": 10000, "days": 30, "price": 75000},
}


class Subscription(Base):
    __tablename__ = "subscriptions"

    id = Column(Integer, primary_key=True, index=True)
    shop_id = Column(Integer, ForeignKey("shops.id"), nullable=False, unique=True, index=True)

    plan = Column(Enum(SubscriptionPlan), nullable=False, default=SubscriptionPlan.TRIAL)
    status = Column(Enum(SubscriptionStatus), nullable=False, default=SubscriptionStatus.ACTIVE)

    starts_at = Column(DateTime(timezone=True), nullable=True)
    expires_at = Column(DateTime(timezone=True), nullable=True)

    amount_paid = Column(Numeric(12, 2), nullable=True)
    payment_ref = Column(String(255), nullable=True)

    is_active = Column(Boolean, default=True, nullable=False)

    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    shop = relationship("Shop", back_populates="subscription")

    def is_valid(self) -> bool:
        if self.status != SubscriptionStatus.ACTIVE:
            return False
        if not self.expires_at:
            return False
        now = datetime.now(timezone.utc)
        expires = self.expires_at
        if expires.tzinfo is None:
            expires = expires.replace(tzinfo=timezone.utc)
        return expires >= now

    def days_remaining(self) -> int:
        if not self.expires_at:
            return 0
        now = datetime.now(timezone.utc)
        expires = self.expires_at
        if expires.tzinfo is None:
            expires = expires.replace(tzinfo=timezone.utc)
        return max(0, (expires - now).days)