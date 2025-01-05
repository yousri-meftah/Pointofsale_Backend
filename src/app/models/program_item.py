from sqlalchemy import Column, Integer, String, ForeignKey, Enum
from sqlalchemy.orm import relationship
from ..models import Base
from ..enums import CodeStatusEnum

class ProgramItem(Base):
    __tablename__ = 'program_item'
    id = Column(Integer, primary_key=True)
    code = Column(String(50))
    status = Column(Enum(CodeStatusEnum), nullable=False)
    program_id = Column(Integer, ForeignKey('program.id'))
    order_id = Column(Integer, ForeignKey('order.id'))

    program = relationship("Program", back_populates="program_item")
    order = relationship("Order" ,  back_populates="program_item")
