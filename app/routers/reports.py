from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.dependencies.auth import get_current_admin, get_current_user
from app.models.user import User
from app.services import report_service

router = APIRouter(prefix="/api/reports", tags=["Reports"])


@router.get("/summary")
def summary(
    from_date: Optional[date] = Query(None),
    to_date: Optional[date] = Query(None),
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin),
):
    return report_service.get_admin_summary(db, current_admin, from_date, to_date)


@router.get("/employee-summary")
def employee_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return report_service.get_employee_summary(db, current_user)