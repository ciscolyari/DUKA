from datetime import datetime, timezone, timedelta
from decimal import Decimal
from typing import List

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.shop import Shop
from app.models.subscription import (
    Subscription,
    SubscriptionPlan,
    SubscriptionStatus,
    PLAN_LIMITS,
)
from app.models.user import User
from app.schemas.subscription import ActivateSubscriptionRequest
from app.services.billing_service import create_billing_and_invoice


def create_trial(db: Session, shop_id: int) -> Subscription:
    """Unda trial wakati wa register."""
    now = datetime.now(timezone.utc)
    sub = Subscription(
        shop_id=shop_id,
        plan=SubscriptionPlan.TRIAL,
        status=SubscriptionStatus.ACTIVE,
        starts_at=now,
        expires_at=now + timedelta(days=14),
        amount_paid=0,
    )
    db.add(sub)
    return sub


def get_subscription(db: Session, current_admin: User) -> dict:
    shop = db.query(Shop).filter(Shop.id == current_admin.shop_id).first()
    if not shop:
        raise HTTPException(status_code=404, detail="Shop not found")

    sub = (
        db.query(Subscription)
        .filter(Subscription.shop_id == current_admin.shop_id)
        .first()
    )
    if not sub:
        raise HTTPException(status_code=404, detail="Subscription not found")

    # Auto-expire
    if sub.status == SubscriptionStatus.ACTIVE and not sub.is_valid():
        sub.status = SubscriptionStatus.EXPIRED
        db.commit()
        db.refresh(sub)

    limits = PLAN_LIMITS.get(sub.plan, PLAN_LIMITS[SubscriptionPlan.BASIC])

    return {
        "id": sub.id,
        "shop_id": sub.shop_id,
        "shop_name": shop.name,
        "plan": sub.plan,
        "status": sub.status,
        "starts_at": sub.starts_at,
        "expires_at": sub.expires_at,
        "days_remaining": sub.days_remaining(),
        "is_valid": sub.is_valid(),
        "max_employees": limits["max_employees"],
        "max_products": limits["max_products"],
        "amount_paid": sub.amount_paid,
        "payment_ref": sub.payment_ref,
    }


def activate_subscription(
    db: Session,
    current_admin: User,
    data: ActivateSubscriptionRequest,
) -> dict:
    """
    Activate / renew subscription.
    Baada ya success → unda Billing + Invoice.
    """
    sub = (
        db.query(Subscription)
        .filter(Subscription.shop_id == current_admin.shop_id)
        .first()
    )
    if not sub:
        raise HTTPException(status_code=404, detail="Subscription not found")

    limits = PLAN_LIMITS.get(data.plan, PLAN_LIMITS[SubscriptionPlan.BASIC])
    days = data.days if data.days else limits["days"]
    now = datetime.now(timezone.utc)

    # Kama bado valid → ongeza siku; else anza upya
    if sub.is_valid() and sub.expires_at:
        base = sub.expires_at
        if base.tzinfo is None:
            base = base.replace(tzinfo=timezone.utc)
        if base < now:
            base = now
    else:
        base = now

    # 1. Sasisha subscription
    sub.plan = data.plan
    sub.status = SubscriptionStatus.ACTIVE
    sub.starts_at = now
    sub.expires_at = base + timedelta(days=days)

    if data.payment_ref:
        sub.payment_ref = data.payment_ref

    if data.amount_paid is not None:
        sub.amount_paid = data.amount_paid
    else:
        sub.amount_paid = limits.get("price", 0)

    # 2. Unda Billing + Invoice (kama kuna malipo)
    amount = Decimal(str(sub.amount_paid or 0))
    if amount > 0:
        create_billing_and_invoice(
            db,
            shop_id=sub.shop_id,
            subscription_id=sub.id,
            paid_by_id=current_admin.id,
            plan=sub.plan.value,
            amount=amount,
            currency="TZS",
            transaction_ref=data.payment_ref,
        )

    db.commit()
    db.refresh(sub)
    return get_subscription(db, current_admin)


def list_plans() -> List[dict]:
    descriptions = {
        SubscriptionPlan.TRIAL: "Jaribio siku 14 — bure",
        SubscriptionPlan.BASIC: "Plan ya msingi",
        SubscriptionPlan.STANDARD: "Plan ya kati",
        SubscriptionPlan.PREMIUM: "Plan kamili",
    }
    return [
        {
            "plan": plan,
            "max_employees": lim["max_employees"],
            "max_products": lim["max_products"],
            "days": lim["days"],
            "price": lim["price"],
            "description": descriptions[plan],
        }
        for plan, lim in PLAN_LIMITS.items()
    ]


def require_active_subscription(db: Session, current_user: User):
    sub = (
        db.query(Subscription)
        .filter(Subscription.shop_id == current_user.shop_id)
        .first()
    )
    if not sub:
        raise HTTPException(status_code=404, detail="Subscription not found")

    if not sub.is_valid():
        if sub.status == SubscriptionStatus.ACTIVE:
            sub.status = SubscriptionStatus.EXPIRED
            db.commit()

        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail={
                "message": "Your subscription has expired. Please renew.",
                "status": sub.status.value,
                "expires_at": sub.expires_at.isoformat() if sub.expires_at else None,
            },
        )
    return sub