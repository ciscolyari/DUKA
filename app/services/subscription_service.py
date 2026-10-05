
from datetime import datetime, timezone, timedelta
from typing import List

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.shop import Shop, SubscriptionPlan, SubscriptionStatus, PLAN_LIMITS
from app.models.user import User
from app.schemas.subscription import ActivateSubscriptionRequest


def start_trial(shop: Shop) -> None:
    
    now = datetime.now(timezone.utc)
    shop.subscription_plan = SubscriptionPlan.TRIAL
    shop.subscription_status = SubscriptionStatus.ACTIVE
    shop.subscription_starts_at = now
    shop.subscription_expires_at = now + timedelta(days=14)


def get_subscription(db: Session, current_admin: User) -> dict:
   
    shop = db.query(Shop).filter(Shop.id == current_admin.shop_id).first()
    if not shop:
        raise HTTPException(status_code=404, detail="Shop not found")

    # Kama muda umeisha → weka EXPIRED
    if shop.subscription_status == SubscriptionStatus.ACTIVE and not shop.is_subscription_active():
        shop.subscription_status = SubscriptionStatus.EXPIRED
        db.commit()
        db.refresh(shop)

    limits = PLAN_LIMITS.get(shop.subscription_plan, PLAN_LIMITS[SubscriptionPlan.BASIC])

    return {
        "shop_id": shop.id,
        "shop_name": shop.name,
        "plan": shop.subscription_plan,
        "status": shop.subscription_status,
        "starts_at": shop.subscription_starts_at,
        "expires_at": shop.subscription_expires_at,
        "days_remaining": shop.days_remaining(),
        "is_active": shop.is_subscription_active(),
        "max_employees": limits["max_employees"],
        "max_products": limits["max_products"],
        "last_payment_ref": shop.last_payment_ref,
    }


def activate_subscription(
    db: Session,
    current_admin: User,
    data: ActivateSubscriptionRequest,
):
    
    shop = db.query(Shop).filter(Shop.id == current_admin.shop_id).first()
    if not shop:
        raise HTTPException(status_code=404, detail="Shop not found")

    limits = PLAN_LIMITS.get(data.plan, PLAN_LIMITS[SubscriptionPlan.BASIC])
    days = data.days if data.days else limits["days"]
    now = datetime.now(timezone.utc)

    
    if shop.is_subscription_active() and shop.subscription_expires_at:
        base = shop.subscription_expires_at
        if base.tzinfo is None:
            base = base.replace(tzinfo=timezone.utc)
        if base < now:
            base = now
    else:
        base = now

    shop.subscription_plan = data.plan
    shop.subscription_status = SubscriptionStatus.ACTIVE
    shop.subscription_starts_at = now
    shop.subscription_expires_at = base + timedelta(days=days)
    if data.payment_ref:
        shop.last_payment_ref = data.payment_ref

    db.commit()
    db.refresh(shop)
    return get_subscription(db, current_admin)


def list_plans() -> List[dict]:
    """Orodha ya plans."""
    descriptions = {
        SubscriptionPlan.TRIAL: "Jaribio siku 14 — bure",
        SubscriptionPlan.BASIC: "Plan ya msingi",
        SubscriptionPlan.STANDARD: "Plan ya kati",
        SubscriptionPlan.PREMIUM: "Plan kamili",
    }
    result = []
    for plan, limits in PLAN_LIMITS.items():
        result.append({
            "plan": plan,
            "max_employees": limits["max_employees"],
            "max_products": limits["max_products"],
            "days": limits["days"],
            "description": descriptions[plan],
        })
    return result


def require_active_subscription(db: Session, current_user: User) -> Shop:
   
    shop = db.query(Shop).filter(Shop.id == current_user.shop_id).first()
    if not shop:
        raise HTTPException(status_code=404, detail="Shop not found")

    if not shop.is_subscription_active():
        if shop.subscription_status == SubscriptionStatus.ACTIVE:
            shop.subscription_status = SubscriptionStatus.EXPIRED
            db.commit()

        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail={
                "message": "your subscription has expired please renew",
                "status": shop.subscription_status.value,
                "expires_at": (
                    shop.subscription_expires_at.isoformat()
                    if shop.subscription_expires_at else None
                ),
            },
        )
    return shop