from fastapi import APIRouter,Depends,Query
from app.core.database import get_db
from app.dependencies.auth import get_current_admin
from sqlalchemy.orm import Session
from app.services.user_service import (
    create_employee,
    destroy,
    get_employee,
    get_employees,
    reset_employee_password,
    set_employee_active,
    update_employee,
)
from app.models.user import User
from app.schemas.user import (
    EmployeePasswordReset,
    EmployeeStatusUpdate,
    UserResponse,
    UserUpdate,
    createuser,
)
from typing import List




router = APIRouter(
    prefix="/api/employees",
    tags=["EMPLOYEE"]
)

@router.post("",response_model=UserResponse, status_code=201)
def employers(data:createuser, db: Session = Depends(get_db), current_admin: User = Depends(get_current_admin)):
    return create_employee(db, data, current_admin)
    
    
    
@router.get("", response_model=List[UserResponse])
def list_employer(active_only: bool = Query(True, description="show only active employee"),
                  db: Session=Depends(get_db),
                  current_admin: User = Depends(get_current_admin)):
    return get_employees(db,current_admin,active_only)


@router.get("/{employee_id}", response_model= UserResponse)
def get_employee_id(employee_id: int,db: Session= Depends(get_db),current_admin: User= Depends(get_current_admin)):
    return get_employee(db, employee_id, current_admin)


@router.put("/{employee_id}", response_model= UserResponse)
def update(
    employee_id:int,
    data:UserUpdate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    return update_employee(db, employee_id, data, current_admin)


@router.patch("/{employee_id}/password", response_model=UserResponse)
def reset_password(
    employee_id: int,
    data: EmployeePasswordReset,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin),
):
    return reset_employee_password(db, employee_id, data.new_password, current_admin)


@router.patch("/{employee_id}/status", response_model=UserResponse)
def set_status(
    employee_id: int,
    data: EmployeeStatusUpdate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin),
):
    return set_employee_active(db, employee_id, data.is_active, current_admin)


@router.delete("/{employee_id}", response_model=UserResponse)
def delete_employee(
    employee_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    return destroy(db, employee_id, current_admin)