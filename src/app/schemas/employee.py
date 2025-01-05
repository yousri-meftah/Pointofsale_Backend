import re
from typing import List, Optional
from pydantic import BaseModel,EmailStr, validator
from sqlalchemy import DateTime
from app.enums import AccountStatus, ContractType,Gender
from datetime import date
from .base import OurBaseModel , OurBaseModelOut , PagedResponse




class Role(OurBaseModel):
    name: str

class RoleOut(OurBaseModel):
    name: str | None

class RolesOut(PagedResponse):
    roles: List[RoleOut] | None




class User(OurBaseModel):
    firstname: str
    lastname: str
    number: int
    gender: Gender
    phone_number: Optional[str] = None
    email: str
    status : AccountStatus
    birthdate: date
    contract_type: ContractType
    cnss_number: str
    roles: List[Role]

    @validator("cnss_number")
    def validates_cnss_number(cls, cnss_number, values):
        contract_type = values.get('contract_type')
        if contract_type in [ContractType.CDI, ContractType.CDD]:
            if not cnss_number:
                raise ValueError("CNSS number is mandatory for CDD and CDI contracts.")
            # Validate CNSS number format with regex
            if not re.match(r'^\d{8}-\d{2}$', cnss_number):
                raise ValueError("Invalid CNSS number format. It should be 8 digits followed by a hyphen and 2 digits.")
        elif cnss_number and not re.match(r'^\d{8}-\d{2}$', cnss_number):
            raise ValueError("Invalid CNSS number format. It should be 8 digits followed by a hyphen and 2 digits.")
        return cnss_number



class UserOut(OurBaseModelOut):
    id:int
    firstname: str
    lastname: str
    number: int
    gender: Gender
    phone_number: Optional[str] = None
    email: str
    account_status : str
    birthdate: Optional[date] = None
    contract_type: ContractType
    cnss_number: Optional[str] = None
    roles:Optional[List[str]] = None

class UsersOut(PagedResponse):
    list: List[UserOut] | None

class EmployeeUpdate(OurBaseModel):
    firstname: Optional[str] = None
    lastname: Optional[str] = None
    phone_number: Optional[str] = None
    birth_date: Optional[date] = None
    cnss_number: Optional[str] = None
    gender: Optional[Gender] = None
    roles: Optional[List[Role]] = None
    status: Optional[AccountStatus] = None
    contract_type: Optional[ContractType] = None



class csvReturn(BaseModel):
    status: str
    errors: Optional[List] = []
    can_force: Optional[List] = []
    data: Optional[List] = []
    message: str

"""{
            "status": "error",
            "errors": critical_errors,
            "can_force": can_force_errors,
            "data": data_rows,
        }"""
