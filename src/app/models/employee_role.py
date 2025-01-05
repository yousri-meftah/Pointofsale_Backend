from sqlalchemy import Column, Integer, ForeignKey, Enum
from sqlalchemy.orm import relationship
from ..models import Base
from ..enums import Role



class Employee_role(Base):
    __tablename__ = "employee_role"
    id:int = Column(Integer, primary_key=True, index=True, autoincrement=True)
    role = Column(Enum(Role), default=Role.VENDOR)
    Employee_id = Column(Integer, ForeignKey('employee.id'))
    employee = relationship("Employee", back_populates="Employee_roles")



