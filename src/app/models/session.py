from sqlalchemy import Column, Integer, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from ..models import Base
from ..enums import SessionStatusEnum

class Session(Base):
    __tablename__ = 'session'
    id = Column(Integer, primary_key=True)
    employee_id = Column(Integer, ForeignKey('employee.id'))
    opened_at = Column(DateTime)
    closed_at = Column(DateTime)
    session_status = Column(Enum(SessionStatusEnum), nullable=False)

    employee = relationship("Employee", back_populates="sessions")
    order = relationship("Order", back_populates="session")
