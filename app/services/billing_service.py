from datetime import datetime, timezone
from decimal import Decimal
from typing import List, Optional

from fastapi import HTTPException
from sqlalchemy.orm import Session, joinedload

from app.models.billing import Billing, Invoice, BillingStatus
from app.models.user import User, UserRole


def _generate_invoice_number(db: Session, shop_id: int):
    today = datetime.now(timezone.utc).strftime("%Y%m%d")
    prefix = f"DUKA-{shop_id}-{today}-"

    last = (
        db.query(Invoice)
        .filter(Invoice.invoice_number.like(f"{prefix}%"))
        .order_by(Invoice.id.desc())
        .first()
    )
    if last and last.invoice_number:
        try:
            seq = int(last.invoice_number.split("-")[-1]) + 1
        except ValueError:
            seq = 1
    else:
        seq = 1
    return f"{prefix}{seq:03d}"


def create_billing_and_invoice(
    db: Session,
    *,
    shop_id: int,
    subscription_id: int,
    paid_by_id: int,
    plan: str,
    amount: Decimal,
    currency: str = "TZS",
    transaction_ref: Optional[str] = None,
    notes: Optional[str] = None):
    billing = Billing(
        shop_id=shop_id,
        subscription_id=subscription_id,
        paid_by_id=paid_by_id,
        plan=plan,
        amount=amount,
        currency=currency,
        transaction_ref=transaction_ref,
        payment_date=datetime.now(timezone.utc),
        status=BillingStatus.SUCCESS,
        notes=notes,
        is_active=True,
    )
    db.add(billing)
    db.flush()

    existing = (
        db.query(Invoice)
        .filter(Invoice.billing_id == billing.id, Invoice.is_active == True)
        .first()
    )
    if existing:
        return billing

    invoice_number = _generate_invoice_number(db, shop_id)
    while db.query(Invoice).filter(Invoice.invoice_number == invoice_number).first():
        invoice_number = _generate_invoice_number(db, shop_id)

    db.add(Invoice(
        billing_id=billing.id,
        shop_id=shop_id,
        subscription_id=subscription_id,
        invoice_number=invoice_number,
        amount=amount,
        currency=currency,
        issued_at=datetime.now(timezone.utc),
        is_active=True,
    ))
    db.flush()
    return billing


def get_billings(db, current_user, subscription_id=None):
    q = ( db.query(Billing) .options(joinedload(Billing.paid_by), joinedload(Billing.invoice)) .filter(Billing.shop_id == current_user.shop_id, Billing.is_active == True) )
    if subscription_id is not None:
        q = q.filter(Billing.subscription_id == subscription_id)
    return q.order_by(Billing.payment_date.desc()).all()


def get_billing(db, billing_id, current_user):
    b = ( db.query(Billing) .options(joinedload(Billing.paid_by), joinedload(Billing.invoice)) .filter(Billing.id == billing_id,
            Billing.shop_id == current_user.shop_id,
            Billing.is_active == True, ) .first() )
    if not b:
        raise HTTPException(status_code=404, detail="Billing record not found")
    return b


def get_invoices(db, current_user):
    return (
        db.query(Invoice)
        .options(joinedload(Invoice.billing))
        .filter(Invoice.shop_id == current_user.shop_id, Invoice.is_active == True)
        .order_by(Invoice.issued_at.desc())
        .all()
    )


def get_invoice(db, invoice_id, current_user):
    inv = (
        db.query(Invoice)
        .options(joinedload(Invoice.billing))
        .filter(
            Invoice.id == invoice_id,
            Invoice.shop_id == current_user.shop_id,
            Invoice.is_active == True,
        )
        .first()
    )
    if not inv:
        raise HTTPException(status_code=404, detail="Invoice not found")
    return inv


def get_invoice_by_number(db, invoice_number, current_user):
    inv = (
        db.query(Invoice).options(joinedload(Invoice.billing)).filter(
            Invoice.invoice_number == invoice_number,
            Invoice.shop_id == current_user.shop_id,
            Invoice.is_active == True,
        )
        .first()
    )
    if not inv:
        raise HTTPException(status_code=404, detail="Invoice not found")
    return inv


def get_invoice_by_billing(db, billing_id, current_user):
    billing = get_billing(db, billing_id, current_user)
    if not billing.invoice or not billing.invoice.is_active:
        raise HTTPException(status_code=404, detail="Invoice not found for this payment")
    return billing.invoice