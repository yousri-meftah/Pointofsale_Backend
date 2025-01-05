from datetime import datetime
from typing import List
from uuid import UUID
from sqlalchemy import Integer
from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.models import Employee,Activation_account
from app.schemas.employee import User as Create_employee
from app.models import Employee_role,Change_password
from app.services.email import send_activation_email,send_reset_password_email
from app.enums import Role, Token_status,AccountStatus
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime, timedelta
from core.config import settings
from app.exceptions.employee import employee_not_found,user_already_exist,token_expired
from app.enums import Role, Token_status,AccountStatus,Gender,ContractType
from pydantic import parse_obj_as
import csv
import io
from fastapi import APIRouter, Depends, HTTPException,status,UploadFile,File,status
from datetime import datetime
from sqlalchemy.exc import IntegrityError
from app.schemas.employee import OurBaseModelOut
from app import utils



#====== get  employee ======
def get_employee(db: Session, employee_id):
    employee =  db.query(Employee).get(employee_id)
    if employee is None:
       raise OurBaseModelOut
    return employee


#====== get all employee ======
def get_employees(db: Session):
    return db.query(Employee).all()


#====== create roles for an employee  ======
def create_employee_roles(db: Session, employee: Employee, roles: List[Role]):
    employee_roles = []
    for rolee in roles:
        employee_role = Employee_role(Employee_id=employee.id, role=rolee.name)
        db.add(employee_role)
        employee_roles.append(employee_role)
    #return employee_roles


#====== create an employee and send an email  ======
async def create_employee(db: Session, employee: Create_employee):
    existing_employee = db.query(Employee).filter(Employee.email == employee.email).first()
    if existing_employee:
        return OurBaseModelOut(
            status=status.HTTP_400_BAD_REQUEST,
            message="Employee already exists.",
        )
    db_employee = Employee(**employee.dict(exclude={"roles"}))
    db.add(db_employee)
    db.flush()
    create_employee_roles(db, db_employee, employee.roles)
    try:
        await send_activation_email(db_employee, db)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Error sending activation email.") from e
    db.commit()
    return OurBaseModelOut(
        status=status.HTTP_201_CREATED,
        message="Employee created successfully.",
    )


async def update_employee(db: Session, employee_id: int, employee_data: dict):
    employee = get_employee(db, employee_id)
    if not employee:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Employee not found.")

    for key, value in employee_data.items():
        setattr(employee, key, value)

    db.commit()
    return employee


async def activate_account(db: Session, password: str, token: int):
    token = db.query(Activation_account).filter(Activation_account.token == token).first()
    if not token:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Token not found.")

    expiration_time = token.created_at + timedelta(minutes=settings.CODE_EXPIRATION_MINUTES)
    if datetime.now() > expiration_time:
        raise HTTPException(status_code=status.HTTP_410_GONE, detail="Token has expired.")

    if token.status == Token_status.USED:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Token has already been")

    token.status = Token_status.USED
    db.flush()

    try:
        employee = get_employee(db, token.Employee_id)
        if not employee:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Employee not found.")

        employee.password =utils.hash_password(password)
        employee.status = AccountStatus.ACTIVE
        db.commit()
        return True
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database error occurred.") from e


def discactivate_employee(db : Session , employee_id:int):
    try:
        employee =get_employee(db,employee_id)
        employee.status = AccountStatus.DEACTIVATE_account
        db.commit()
        return True
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Database error occurred.") from e






def reset_password(db: Session, token: int, password: str):
    token = db.query(Change_password).filter(Change_password.token == token).first()
    if not token:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Token not found.")

    expiration_time = token.created_at + timedelta(minutes=settings.CODE_EXPIRATION_MINUTES)
    if datetime.now() > expiration_time:
        raise HTTPException(status_code=status.HTTP_410_GONE, detail="Token has expired.")

    if token.status == Token_status.USED:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Token has already been used.")

    token.status = Token_status.USED
    db.flush()

    try:
        employee = get_employee(db, token.Employee_id)
        if not employee:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Employee not found.")

        employee.password = utils.hash_password(password)
        db.commit()
        return employee
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database error occurred.") from e



async def create_employees_from_csv(file: UploadFile, db: Session):
    if file.content_type != 'text/csv':
        raise HTTPException(status_code=400, detail="Invalid file format")

    # Read and decode the file
    stream = io.StringIO(file.file.read().decode("utf-8"))
    csv_reader = csv.DictReader(stream)

    successful = []
    errors = []

    for employee_data in csv_reader:
        try:
            employee_data['birthdate'] = datetime.strptime(employee_data['birthdate'], '%Y-%m-%d') if employee_data['birthdate'] else None
            employee_data['gender'] = Gender(employee_data['gender'])
            employee_data['status'] = AccountStatus(employee_data['status'])
            employee_data['contract_type'] = ContractType(employee_data['contract_type'])
            employee_data['roles'] = employee_data['roles'].split(";") if employee_data['roles'] else []

            # Parsing the dictionary to the Pydantic model
            employee = parse_obj_as(Create_employee, employee_data)

            # Creating the employee in the database
            if await create_employee(db, employee):
                successful.append(employee.email)
        except IntegrityError as e:
            # Rollback the transaction on error
            db.rollback()
            # Add the error message and the problematic email to the error list
            errors.append({'email': employee_data['email'], 'error': str(e.orig)})
        except Exception as e:
            db.rollback()
            errors.append({'email': employee_data['email'], 'error': str(e)})

    # Return a response with successful inserts and any errors encountered
    if errors:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={"errors": errors})

    return {"successful": successful}


