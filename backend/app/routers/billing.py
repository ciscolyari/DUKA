from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.dependencies.auth import get_current_admin
from app.models.user import User
from app.schemas.billing import BillingResponse, InvoiceResponse
from app.services import billing_service

router = APIRouter(tags=["Billing & Invoices"])


def _billing_response(b) -> BillingResponse:
    return BillingResponse(
        id=b.id,
        shop_id=b.shop_id,
        subscription_id=b.subscription_id,
        paid_by_id=b.paid_by_id,
        paid_by_name=b.paid_by.full_name if b.paid_by else None,
        plan=b.plan,
        amount=b.amount,
        currency=b.currency,
        transaction_ref=b.transaction_ref,
        payment_date=b.payment_date,
        status=b.status,
        notes=b.notes,
        invoice_number=b.invoice.invoice_number if b.invoice else None,
        created_at=b.created_at,
    )


def _invoice_response(inv) -> InvoiceResponse:
    return InvoiceResponse(
        id=inv.id,
        billing_id=inv.billing_id,
        shop_id=inv.shop_id,
        subscription_id=inv.subscription_id,
        invoice_number=inv.invoice_number,
        amount=inv.amount,
        currency=inv.currency,
        issued_at=inv.issued_at,
        plan=inv.billing.plan if inv.billing else None,
        transaction_ref=inv.billing.transaction_ref if inv.billing else None,
    )


@router.get("/api/billing", response_model=List[BillingResponse])
def list_billing(db: Session = Depends(get_db), current_admin: User = Depends(get_current_admin)):
    return [_billing_response(b) for b in billing_service.get_billings(db, current_admin)]


@router.get("/api/billing/{billing_id}", response_model=BillingResponse)
def get_billing(billing_id: int, db: Session = Depends(get_db), current_admin: User = Depends(get_current_admin)):
    return _billing_response(billing_service.get_billing(db, billing_id, current_admin))


@router.get("/api/subscriptions/{subscription_id}/billing", response_model=List[BillingResponse])
def billing_by_subscription(
    subscription_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin),
):
    rows = billing_service.get_billings(db, current_admin, subscription_id=subscription_id)
    return [_billing_response(b) for b in rows]


@router.get("/api/invoices", response_model=List[InvoiceResponse])
def list_invoices(db: Session = Depends(get_db), current_admin: User = Depends(get_current_admin)):
    return [_invoice_response(i) for i in billing_service.get_invoices(db, current_admin)]


@router.get("/api/invoices/{invoice_id}", response_model=InvoiceResponse)
def get_invoice(invoice_id: int, db: Session = Depends(get_db), current_admin: User = Depends(get_current_admin)):
    return _invoice_response(billing_service.get_invoice(db, invoice_id, current_admin))


@router.get("/api/invoices/number/{invoice_number}", response_model=InvoiceResponse)
def get_invoice_by_number(
    invoice_number: str,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin),
):
    return _invoice_response(billing_service.get_invoice_by_number(db, invoice_number, current_admin))


@router.get("/api/payments/{billing_id}/invoice", response_model=InvoiceResponse)
def get_invoice_for_payment(
    billing_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin),
):
    return _invoice_response(billing_service.get_invoice_by_billing(db, billing_id, current_admin))