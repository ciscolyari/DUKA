from sqlalchemy.orm import Session
from fastapi import Depends,HTTPException, status
from app.models.user import User, UserRole
from app.core.security import hash_password
from app.schemas.user import createuser,UserUpdate




def create_employee(db: Session, data: createuser, current_admin:User):
    if data.role != UserRole.EMPLOYEE:
        raise HTTPException(status_code = status.HTTP_400_BAD_REQUEST,
                            detail="create employee account")
    existing = db.query(User).filter(User.email==data.email).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="email already existing")
    
    employee=User(
        shop_id= current_admin.shop_id,
        email=data.email,
        full_name=data.full_name,
        hashed_password=hash_password(data.password),
        role= UserRole.EMPLOYEE
    )    
    db.add(employee)
    db.commit()
    db.refresh(employee)
    return employee    
        
        
def get_employees(db: Session, current_admin: User, active_only: bool=True):
    query = db.query(User).filter(
    User.shop_id == current_admin.shop_id,
    User.role == UserRole.EMPLOYEE
)
    if active_only:
        query=query.filter(User.active == True)
    return query.order_by(User.full_name).all()    


def get_employee(db: Session, employee_id: int,current_admin: User):
    employee = db.query(User).filter(User.id== employee_id,User.shop_id == current_admin.shop_id,
                                     User.role == UserRole.EMPLOYEE).first()
    if not employee:
       raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="employee not found")
    return employee 
        

def update_employee(db: Session, employee_id: int, data:UserUpdate, current_admin: User):
    employee = get_employee(db, employee_id, current_admin)
    update_data = data.model_dump(exclude_unset= True)
    if "password" in update_data:
        plain_password = update_data.pop("password")
        update_data["hashed_password"] = hash_password(plain_password)
    
    for field, value in update_data.items():
        setattr(employee, field, value)
        
    db.commit()
    db.refresh(employee)
    return employee



def destroy(db:Session, employee_id: int, current_admin: User):
    employee = get_employee(db, employee_id, current_admin)
    employee.active = False
    db.commit()
    db.refresh(employee)
    return employee        