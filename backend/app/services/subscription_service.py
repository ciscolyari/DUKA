from datetime import datetime, timezone, timedelta
from decimal import Decimal
from typing import List

from fastapi import HTTPException, status
from sqlalchemy.orm import Session, joinedload

from app.models.subscription import (
    SubscriptionPlan, Subscription, SubscriptionStatus, STATUS_TRANSITIONS,
)
from app.models.user import User, UserRole
from app.schemas.subscription import (
    PlanCreate, PlanUpdate, SubscribeRequest, ChangePlanRequest, SubscriptionStatusUpdate,
)
from app.services.billing_service import create_billing_and_invoice


def _to_sub_dict(sub: Subscription) -> dict:
    return {
        "id": sub.id,
        "shop_id": sub.shop_id,
        "plan_id": sub.plan_id,
        "plan_name": sub.plan.name if sub.plan else None,
        "status": sub.status,
        "starts_at": sub.starts_at,
        "expires_at": sub.expires_at,
        "days_remaining": sub.days_remaining(),
        "is_valid": sub.is_valid(),
        "is_current": sub.is_current,
        "amount_paid": sub.amount_paid,
        "payment_ref": sub.payment_ref,
        "notes": sub.notes,
        "created_at": sub.created_at,
    }


# ----- PLANS -----

def create_plan(db, data: PlanCreate, current_admin: User):
    if current_admin.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Admin only")
    if db.query(SubscriptionPlan).filter(SubscriptionPlan.name == data.name).first():
        raise HTTPException(status_code=400, detail="Plan name already exists")

    plan = SubscriptionPlan(
        name=data.name,
        description=data.description,
        price=data.price,
        currency=data.currency,
        duration_days=data.duration_days,
        billing_interval=data.billing_interval,
        features=data.features,
        is_active=data.is_active,
    )
    db.add(plan)
    db.commit()
    db.refresh(plan)
    return plan


def list_plans(db, active_only: bool = False):
    q = db.query(SubscriptionPlan)
    if active_only:
        q = q.filter(SubscriptionPlan.is_active == True)
    return q.order_by(SubscriptionPlan.price.asc()).all()


def get_plan(db, plan_id: int):
    plan = db.query(SubscriptionPlan).filter(SubscriptionPlan.id == plan_id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    return plan


def update_plan(db, plan_id: int, data: PlanUpdate, current_admin: User):
    if current_admin.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Admin only")
    plan = get_plan(db, plan_id)
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(plan, field, value)
    db.commit()
    db.refresh(plan)
    return plan


def set_plan_status(db, plan_id: int, is_active: bool, current_admin: User):
    if current_admin.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Admin only")
    plan = get_plan(db, plan_id)
    plan.is_active = is_active
    db.commit()
    db.refresh(plan)
    return plan


# ----- SUBSCRIPTIONS -----

def create_trial_for_shop(db, shop_id: int):
    trial = db.query(SubscriptionPlan).filter(SubscriptionPlan.name.ilike("trial")).first()
    if not trial:
        trial = SubscriptionPlan(
            name="Trial",
            description="Jaribio la siku 14 — bure",
            price=0,
            currency="TZS",
            duration_days=14,
            features={"max_employees": 2, "max_products": 50},
            is_active=True,
        )
        db.add(trial)
        db.flush()

    now = datetime.now(timezone.utc)
    sub = Subscription(
        shop_id=shop_id,
        plan_id=trial.id,
        status=SubscriptionStatus.ACTIVE,
        starts_at=now,
        expires_at=now + timedelta(days=trial.duration_days),
        is_current=True,
        amount_paid=0,
    )
    db.add(sub)
    return sub


def subscribe(db, data: SubscribeRequest, current_user: User):
    plan = get_plan(db, data.plan_id)
    if not plan.is_active:
        raise HTTPException(status_code=400, detail="Plan is not active")

    db.query(Subscription).filter(
        Subscription.shop_id == current_user.shop_id,
        Subscription.is_current == True,
    ).update({"is_current": False})

    now = datetime.now(timezone.utc)
    amount = data.amount_paid if data.amount_paid is not None else plan.price

    sub = Subscription(
        shop_id=current_user.shop_id,
        plan_id=plan.id,
        status=SubscriptionStatus.ACTIVE if amount == 0 else SubscriptionStatus.PENDING,
        starts_at=now if amount == 0 else None,
        expires_at=(now + timedelta(days=plan.duration_days)) if amount == 0 else None,
        is_current=True,
        amount_paid=amount,
        payment_ref=data.payment_ref,
        notes=data.notes,
    )

    if amount and Decimal(str(amount)) > 0 and data.payment_ref:
        sub.status = SubscriptionStatus.ACTIVE
        sub.starts_at = now
        sub.expires_at = now + timedelta(days=plan.duration_days)

    db.add(sub)
    db.flush()

    if sub.status == SubscriptionStatus.ACTIVE and Decimal(str(amount or 0)) > 0:
        create_billing_and_invoice(
            db,
            shop_id=sub.shop_id,
            subscription_id=sub.id,
            paid_by_id=current_user.id,
            plan=plan.name,
            amount=Decimal(str(amount)),
            currency=plan.currency,
            transaction_ref=data.payment_ref,
        )

    db.commit()
    db.refresh(sub)
    sub = db.query(Subscription).options(joinedload(Subscription.plan)).filter(Subscription.id == sub.id).first()
    return _to_sub_dict(sub)


def get_current_subscription(db, current_user: User):
    sub = (
        db.query(Subscription)
        .options(joinedload(Subscription.plan))
        .filter(
            Subscription.shop_id == current_user.shop_id,
            Subscription.is_current == True,
            Subscription.is_active == True,
        )
        .first()
    )
    if not sub:
        raise HTTPException(status_code=404, detail="No current subscription")

    if sub.status == SubscriptionStatus.ACTIVE and not sub.is_valid():
        sub.status = SubscriptionStatus.EXPIRED
        db.commit()
        db.refresh(sub)

    return _to_sub_dict(sub)


def list_subscriptions(db, current_user: User):
    rows = (
        db.query(Subscription)
        .options(joinedload(Subscription.plan))
        .filter(Subscription.shop_id == current_user.shop_id, Subscription.is_active == True)
        .order_by(Subscription.created_at.desc())
        .all()
    )
    return [_to_sub_dict(s) for s in rows]


def get_subscription(db, subscription_id: int, current_user: User):
    sub = (
        db.query(Subscription)
        .options(joinedload(Subscription.plan))
        .filter(
            Subscription.id == subscription_id,
            Subscription.shop_id == current_user.shop_id,
            Subscription.is_active == True,
        )
        .first()
    )
    if not sub:
        raise HTTPException(status_code=404, detail="Subscription not found")
    return _to_sub_dict(sub)


def update_subscription_status(db, subscription_id: int, data: SubscriptionStatusUpdate, current_user: User):
    sub = (
        db.query(Subscription)
        .options(joinedload(Subscription.plan))
        .filter(
            Subscription.id == subscription_id,
            Subscription.shop_id == current_user.shop_id,
            Subscription.is_active == True,
        )
        .first()
    )
    if not sub:
        raise HTTPException(status_code=404, detail="Subscription not found")

    allowed = STATUS_TRANSITIONS.get(sub.status, set())
    if data.status not in allowed:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot change status from {sub.status.value} to {data.status.value}",
        )

    sub.status = data.status
    if data.notes:
        sub.notes = data.notes

    if data.status == SubscriptionStatus.ACTIVE and not sub.starts_at:
        now = datetime.now(timezone.utc)
        sub.starts_at = now
        days = sub.plan.duration_days if sub.plan else 30
        sub.expires_at = now + timedelta(days=days)

    db.commit()
    db.refresh(sub)
    return _to_sub_dict(sub)


def change_plan(db, subscription_id: int, data: ChangePlanRequest, current_user: User):
    current = (
        db.query(Subscription)
        .options(joinedload(Subscription.plan))
        .filter(
            Subscription.id == subscription_id,
            Subscription.shop_id == current_user.shop_id,
            Subscription.is_active == True,
        )
        .first()
    )
    if not current:
        raise HTTPException(status_code=404, detail="Subscription not found")

    new_plan = get_plan(db, data.new_plan_id)
    if not new_plan.is_active:
        raise HTTPException(status_code=400, detail="New plan is not active")
    if current.plan_id == new_plan.id:
        raise HTTPException(status_code=400, detail="Already on this plan")

    current.is_current = False
    if current.status == SubscriptionStatus.ACTIVE:
        current.status = SubscriptionStatus.CANCELLED

    now = datetime.now(timezone.utc)
    amount = data.amount_paid if data.amount_paid is not None else new_plan.price

    new_sub = Subscription(
        shop_id=current_user.shop_id,
        plan_id=new_plan.id,
        status=SubscriptionStatus.ACTIVE,
        starts_at=now,
        expires_at=now + timedelta(days=new_plan.duration_days),
        is_current=True,
        amount_paid=amount,
        payment_ref=data.payment_ref,
        notes=data.notes or f"Changed from plan_id={current.plan_id}",
    )
    db.add(new_sub)
    db.flush()

    if Decimal(str(amount or 0)) > 0:
        create_billing_and_invoice(
            db,
            shop_id=new_sub.shop_id,
            subscription_id=new_sub.id,
            paid_by_id=current_user.id,
            plan=new_plan.name,
            amount=Decimal(str(amount)),
            currency=new_plan.currency,
            transaction_ref=data.payment_ref,
        )

    db.commit()
    db.refresh(new_sub)
    new_sub = db.query(Subscription).options(joinedload(Subscription.plan)).filter(Subscription.id == new_sub.id).first()
    return _to_sub_dict(new_sub)


def available_plans_for_change(db, subscription_id: int, current_user: User):
    sub = (
        db.query(Subscription)
        .filter(Subscription.id == subscription_id, Subscription.shop_id == current_user.shop_id)
        .first()
    )
    if not sub:
        raise HTTPException(status_code=404, detail="Subscription not found")

    return (
        db.query(SubscriptionPlan)
        .filter(SubscriptionPlan.is_active == True, SubscriptionPlan.id != sub.plan_id)
        .order_by(SubscriptionPlan.price.asc())
        .all()
    )


def require_active_subscription(db, current_user: User):
    sub = (
        db.query(Subscription)
        .options(joinedload(Subscription.plan))
        .filter(
            Subscription.shop_id == current_user.shop_id,
            Subscription.is_current == True,
            Subscription.is_active == True,
        )
        .first()
    )
    if not sub:
        raise HTTPException(status_code=404, detail="No subscription found")

    if not sub.is_valid():
        if sub.status == SubscriptionStatus.ACTIVE:
            sub.status = SubscriptionStatus.EXPIRED
            db.commit()
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail={
                "message": "Subscription has expired. Please renew.",
                "status": sub.status.value,
                "expires_at": sub.expires_at.isoformat() if sub.expires_at else None,
            },
        )
    return sub