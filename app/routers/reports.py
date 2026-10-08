from datetime import date, timedelta

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.dependencies.auth import get_current_admin, get_current_user
from app.models.user import User
from app.services import report_service

router = APIRouter(prefix="/api/reports", tags=["Reports"])


@router.get("/summary")
def get_summary(
    from_date: date | None = Query(None),
    to_date: date | None = Query(None),
    reports: bool = Query(False),
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    today = date.today()
    end_date = to_date or today
    start_date = from_date or (end_date - timedelta(days=29) if reports else end_date)
    if start_date > end_date:
        raise HTTPException(
            status_code=422,
            detail="from_date must be on or before to_date",
        )
    return report_service.summary(db, admin, start_date, end_date)


@router.get("/employee-summary")
def get_employee_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return report_service.employee_summary(db, current_user)