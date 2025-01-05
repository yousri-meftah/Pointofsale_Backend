
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from datetime import datetime
from app.controllers.employee import (
    create_employee,
    update_employee,
    discactivate_employee,
    create_employees_from_csv,
    get_employee,
    get_employees,
)
import io
import re
import csv
from typing import Union
from app import utils
from sqlalchemy import func
from core.database import get_db
from app.exceptions.employee import user_already_exist, employee_not_found
from app.services.token import oauth2_scheme, RoleChecker
from app.enums import Role,AccountStatus,ContractType
from app.schemas.employee import UserOut,OurBaseModelOut,UsersOut,RoleOut,User,EmployeeUpdate,RolesOut
from app import models
from app.models import Employee,Employee_role
from sqlalchemy.exc import IntegrityError


allow_action_by_roles = RoleChecker([ Role.SUPER_USER,Role.ADMIN])

router = APIRouter(
    dependencies=[Depends(oauth2_scheme) , Depends(allow_action_by_roles)]
)

@router.get('/get_all_employee', response_model=Union[UsersOut,OurBaseModelOut])
def get_all(
    db: Session = Depends(get_db),
    page_size: int = 10,
    page_number: int = 1,
    name_substr: str = None
):
    query = db.query(models.Employee)

    if name_substr:
        query = query.filter(func.lower(func.CONCAT(models.User.first_name, " ", models.User.last_name)).contains(func.lower(name_substr)))

    total_records = query.count()
    total_pages = utils.div_ceil(total_records, page_size)
    users = query.limit(page_size).offset((page_number-1)*page_size).all()

    user_out_list = []
    for user in users:
        roles_out = []
        for role in user.Employee_roles:
            roles_out.append(role.role.name)
        user_out = UserOut(
            id=user.id,
            firstname=user.firstname,
            lastname=user.lastname,
            number=user.number,
            gender=user.gender,
            account_status=user.status.name,
            phone_number=user.phone_number,
            email=user.email,
            birthdate=user.birthdate,
            contract_type=user.contract_type,
            cnss_number=user.cnss_number,
            roles=roles_out,
            message=None,
            status=None,
        )
        user_out_list.append(user_out)

    return UsersOut(
        total_pages=total_pages,
        total_records=total_records,
        page_number=page_number,
        page_size=page_size,
        list=user_out_list,
        message="All users",
        status=status.HTTP_200_OK
    )


@router.get("/{employee_id}" , response_model=Union[UserOut,OurBaseModelOut])
def get_employee_by_id(
    employee_id: int,
    db: Session = Depends(get_db),
):
    try:
        employee  = get_employee(db, employee_id)
        employee_roles = employee.Employee_roles
        employee_fields = employee.__dict__
        employee_fields.pop('status')
        employee_fields.pop('password')


    except employee_not_found:
        return OurBaseModelOut(
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            messege="something went wrong."
        )
    roles_out = []
    for role in employee_roles:
        roles_out.append(role.role.name)

    return UserOut(
        **employee_fields,
        roles=roles_out,
        message="Employee found",
        status=status.HTTP_200_OK
    )


@router.post("/", response_model=OurBaseModelOut)
async def create_employe(
    employee: User,
    db: Session = Depends(get_db),
    ):
    try:
        result = await create_employee(db, employee)
        return result
    except Exception as e:
        db.rollback()
        return OurBaseModelOut(
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="Error creating user. "
        )



@router.post("/csv", response_model=dict)
async def upload_employees(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    return await create_employees_from_csv(file, db)




@router.patch("/disactivate/{employee_id}", response_model=bool)
def disactivate_employe(
    employee_id: int,
    db: Session = Depends(get_db),
):
    #[TODO] modify the function to return a response model
    return discactivate_employee(db, employee_id=employee_id)




@router.put("/{employee_id}", response_model=OurBaseModelOut)
async def update_employe(
    employee: EmployeeUpdate,
    employee_id: int,
    db: Session = Depends(get_db),
):
    try:
        result = await update_employee(db, employee_id=employee_id, employee_data=employee.dict(exclude_unset=True))

    except HTTPException as e:
        return OurBaseModelOut(
            status=e.status_code,
            message=e.detail
        )
    except Exception as e:
        return OurBaseModelOut(
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="An error occurred during employee update."
        )

    return OurBaseModelOut(
            status=status.HTTP_200_OK,
            message="Employee updated successfully.",
        )



REQUIRED_FIELDS = ["email", "number", "contract_type"]

@router.post("/bulk_add_employees")
async def bulk_add_employees(
    file: UploadFile = File(...),
    force: bool = False,
    db: Session = Depends(get_db)
):
    if file.content_type != "text/csv":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file type. Please upload a CSV file.",
        )
    missing_fields = [field for field in REQUIRED_FIELDS if field not in headers]
    if missing_fields:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Missing required fields in the CSV: {', '.join(missing_fields)}",
        )

    content = await file.read()
    csv_reader = csv.DictReader(io.StringIO(content.decode("utf-8")))
    data_rows = []
    critical_errors = []
    can_force_errors = []
    valid_employees = []

    for line_number, row in enumerate(csv_reader, start=1):
        try:
            email = row.get("email", "").strip()
            firstname = row.get("firstname", "").strip()
            lastname = row.get("lastname", "").strip()
            number = int(row.get("number", 0))
            gender = row.get("gender", "").strip()
            phone_number = row.get("phone_number", None)
            status = row.get("status", "INACTIVE").strip()
            birthdate = row.get("birthdate", None)
            contract_type = row.get("contract_type", "").strip()
            cnss_number = row.get("cnss_number", "").strip()
            roles = row.get("roles", "").split(",")

            #i will return it to front to render it to the user , to know where are the the wrong rows if there is any .
            data_rows.append(row)

            if not email or not firstname or not lastname or not gender or not contract_type:
                critical_errors.append(
                    {"line": line_number, "error": "missing mandatory fields."}
                )
                continue


            if db.query(Employee).filter(Employee.email == email).first():
                critical_errors.append(
                    {"line": line_number, "error": f"Email {email} already exists."}
                )
                continue

            
            if gender==''or gender ==None :
                critical_errors.append(
                    {"line": line_number, "error": f"Invalid gender: {gender}."}
                )
                continue

            if status not in [s.value for s in AccountStatus]:
                can_force_errors.append(f"Line {line_number}: nvalid status {status}. if you force ,it will be INACTIVE.")
                status = AccountStatus.INACTIVE

            if contract_type in [ContractType.CDI, ContractType.CDD,ContractType.APPRENTI,ContractType.CIVP]:
                if not cnss_number:
                    critical_errors.append(
                        {"line": line_number, "error": "CNSS number is mandatory"}
                    )
                    continue
                if contract_type==ContractType.CDI and not re.match(r"^\d{8}-\d{2}$", cnss_number):
                    critical_errors.append(
                        {"line": line_number, "error": "Invalid CNSS number"}
                    )
                    continue
            try:
                birthdate = datetime.strptime(birthdate, "%Y-%m-%d").date()
            except ValueError:
                can_force_errors.append(f"Line {line_number}: Invalid birthdate format {birthdate}. Ignoring.")

            my_roles = []
            for role in roles:
                role = role.strip()
                if role not in [r.value for r in Role]:  
                    can_force_errors.append(
                        f"Line {line_number}: Invalid role {role}. Defaulting to VENDOR."
                    )
                    my_roles.append(Role.VENDOR)
                else:
                    my_roles.append(Role(role))


            valid_employees.append(
                User(
                    firstname=firstname,
                    lastname=lastname,
                    number=number,
                    gender=gender,
                    phone_number=phone_number,
                    status=status,
                    email=email,
                    birthdate=birthdate,
                    contract_type=contract_type,
                    cnss_number=cnss_number,
                    roles=my_roles,
                )
            )
        except Exception as e:
            critical_errors.append({"line": line_number, "error": str(e)})

    if critical_errors:
        return {
            "status": "error",
            "errors": critical_errors,
            "can_force": can_force_errors,
            "data": data_rows,
        }

    if can_force_errors and not force:
        return {
            "status": "can_force",
            "errors": [],
            "can_force": can_force_errors,
            "data": data_rows,
        }

    if force or not can_force_errors:
        try:
            db_employees = [
                Employee(**employee.dict(exclude={"roles"}))
                for employee in valid_employees
            ]
            db.bulk_save_objects(db_employees)
            db.flush()  
            db_roles = []
            for db_employee, employee in zip(db_employees, valid_employees):
                for role in employee.roles:
                    db_roles.append(
                        Employee_role(role=role.name, Employee_id=db_employee.id)
                    )
            db.bulk_save_objects(db_roles)
            db.commit()
            # i guess i need to send the emails here but whatever lets force him to do the forget password , 
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=200,
                detail="something went wrong!!!!",
            )

    return {
        "status": "imported",
        "message": f"Successfully imported {len(valid_employees)} employees.",
    }

