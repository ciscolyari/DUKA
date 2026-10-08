from fastapi import APIRouter,Depends,Query
from app.core.database import get_db
from app.dependencies.auth import get_current_admin, get_current_employee
from sqlalchemy.orm import Session
from app .services.user_service import createuser, create_employee, get_employee, destroy,update_employee, get_employees
from app.models.user import User
from app.schemas.user import UserResponse,createuser,UserUpdate
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

@router.delete("/{employee_id}", response_model=UserResponse)
def delete_employee(
    employee_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    return destroy(db, employee_id, current_admin)