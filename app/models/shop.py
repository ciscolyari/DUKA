from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Boolean, DateTime,ForeignKey, Enum
import enum
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


# Limits kwa ki
PLAN_LIMITS = {
    SubscriptionPlan.TRIAL:    {"max_employees": 2,  "max_products": 50,    "days": 14},
    SubscriptionPlan.BASIC:    {"max_employees": 5,  "max_products": 200,   "days": 30},
    SubscriptionPlan.STANDARD: {"max_employees": 15, "max_products": 1000,  "days": 30},
    SubscriptionPlan.PREMIUM:  {"max_employees": 50, "max_products": 10000, "days": 30},
}






class Shop(Base):
    __tablename__ = "shops"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    #user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    location = Column(String, nullable=False)
    Active = Column(Boolean, default=True, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)
    
    subscription_starts_at = Column(DateTime(timezone=True), nullable=True)
    subscription_expires_at = Column(DateTime(timezone=True), nullable=True)
    last_payment_ref = Column(String(255), nullable=True)
    
    subscription_status = Column(
            Enum(SubscriptionStatus),
            nullable=False,
            default=SubscriptionStatus.ACTIVE,
        )




    # users = relationship("User", back_populates="shop")
    # products = relationship("Product", back_populates="shop")
    # sales = relationship("Sale", back_populates="shop")
    
    
    users = relationship("User", back_populates="shop", cascade="all, delete-orphan")
    products = relationship("Product", back_populates="shop", cascade="all, delete-orphan")
    sales = relationship("Sale", back_populates="shop", cascade="all, delete-orphan")
    subscription = relationship("Subscription",back_populates="shop")
    
    
    def is_subscription_active(self) -> bool:
        """True kama plan bado haijaisha."""
        if self.subscription_status != SubscriptionStatus.ACTIVE:
            return False
        if not self.subscription_expires_at:
            return False
        now = datetime.now(timezone.utc)
        expires = self.subscription_expires_at
        if expires.tzinfo is None:
            expires = expires.replace(tzinfo=timezone.utc)
        return expires >= now

    def days_remaining(self) -> int:
        """Siku zilizobaki."""
        if not self.subscription_expires_at:
            return 0
        now = datetime.now(timezone.utc)
        expires = self.subscription_expires_at
        if expires.tzinfo is None:
            expires = expires.replace(tzinfo=timezone.utc)
        return max(0, (expires - now).days)








# """
# SHOP + SUBSCRIPTION
# ===================
# Kila duka lina plan na muda wa kuisha.
# """

# from datetime import datetime, timezone
# import enum

# from sqlalchemy import Column, Integer, String, DateTime, Boolean, Enum
# from sqlalchemy.orm import relationship
# from app.core.database import Base




# class Shop(Base):
#     __tablename__ = "shops"

#     id = Column(Integer, primary_key=True, index=True)
#     name = Column(String(255), nullable=False)
#     location = Column(String(255), nullable=True)
#     is_active = Column(Boolean, default=True, nullable=False)

#     # Subscription
#     subscription_plan = Column(
#         Enum(SubscriptionPlan),
#         nullable=False,
#         default=SubscriptionPlan.TRIAL,
#     )
#     subscription_status = Column(
#         Enum(SubscriptionStatus),
#         nullable=False,
#         default=SubscriptionStatus.ACTIVE,
#     )
  
#     created_at = Column(
#         DateTime(timezone=True),
#         default=lambda: datetime.now(timezone.utc),
#         nullable=False,
#     )
#     updated_at = Column(
#         DateTime(timezone=True),
#         default=lambda: datetime.now(timezone.utc),
#         onupdate=lambda: datetime.now(timezone.utc),
#         nullable=False,
#     )

#     # users = relationship("User", back_populates="shop", cascade="all, delete-orphan")
#     # products = relationship("Product", back_populates="shop", cascade="all, delete-orphan")
#     # sales = relationship("Sale", back_populates="shop", cascade="all, delete-orphan")

#     # def is_subscription_active(self) -> bool:
#     #     """True kama plan bado haijaisha."""
#     #     if self.subscription_status != SubscriptionStatus.ACTIVE:
#     #         return False
#     #     if not self.subscription_expires_at:
#     #         return False
#     #     now = datetime.now(timezone.utc)
#     #     expires = self.subscription_expires_at
#     #     if expires.tzinfo is None:
#     #         expires = expires.replace(tzinfo=timezone.utc)
#     #     return expires >= now

#     # def days_remaining(self) -> int:
#     #     """Siku zilizobaki."""
#     #     if not self.subscription_expires_at:
#     #         return 0
#     #     now = datetime.now(timezone.utc)
#     #     expires = self.subscription_expires_at
#     #     if expires.tzinfo is None:
#     #         expires = expires.replace(tzinfo=timezone.utc)
#     #     return max(0, (expires - now).days)