from sqlalchemy import Column, Integer, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from ..models import Base
from ..enums import Token_status


class Change_password(Base):
    __tablename__ = "change_password"

    id:int = Column(Integer, primary_key=True, index=True, autoincrement=True)

    Employee_id = Column(Integer, ForeignKey('employee.id'))
    employee = relationship("Employee", back_populates="change_poasswords")

    token = Column(Integer)
    created_at = Column(DateTime)
    status = Column(Enum(Token_status), nullable=False)