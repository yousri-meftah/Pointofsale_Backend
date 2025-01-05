from sqlalchemy import Column, Integer, String, DateTime, Enum,Boolean
from sqlalchemy.orm import relationship
from ..models import Base
from ..enums import Gender, AccountStatus,ContractType
from .employee_role import Employee_role
from .change_password import Change_password
from .account_activation import Activation_account




class Employee(Base):
    __tablename__ = "employee"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    firstname = Column(String(120), nullable=False)
    lastname = Column(String(120), nullable=False)
    password = Column(String(255))
    number = Column(Integer, nullable=False)
    gender = Column(Enum(Gender), nullable=False)
    phone_number = Column(String(20))
    status = Column(Enum(AccountStatus), nullable=False, default=AccountStatus.INACTIVE)
    email = Column(String(50), nullable=False, unique=True)
    birthdate = Column(DateTime)
    contract_type = Column(Enum(ContractType), nullable=False)
    cnss_number = Column(String(15))
    created_at = Column(DateTime)

    Employee_roles = relationship("Employee_role",back_populates="employee")
    change_poasswords = relationship("Change_password",back_populates="employee")
    activation_accounts = relationship("Activation_account",back_populates="employee")
    sessions = relationship("Session", back_populates="employee")

