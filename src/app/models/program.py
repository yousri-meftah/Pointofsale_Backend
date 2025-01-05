from sqlalchemy import Column, Integer, String, Float, Date, Text, ForeignKey, Enum ,case , func , CheckConstraint
from sqlalchemy.orm import relationship
from ..models import Base
from ..enums import ProgramTypeEnum



class Program(Base):
    __tablename__ = 'program'
    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    description = Column(Text)
    program_type = Column(Enum(ProgramTypeEnum), nullable=False)
    start_date = Column(Date)
    end_date = Column(Date)
    discount = Column(Float)
    product_buy_id = Column(Integer, ForeignKey('product.id'), nullable=True)
    product_get_id = Column(Integer, ForeignKey('product.id'), nullable=True)
    program_status= Column(Integer)

    product_buy = relationship("Product", foreign_keys=[product_buy_id], overlaps="programs_buy")
    product_get = relationship("Product", foreign_keys=[product_get_id], overlaps="programs_get")
    program_item = relationship("ProgramItem", back_populates="program")


