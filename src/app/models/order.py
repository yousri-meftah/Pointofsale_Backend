from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..models import Base

class Order(Base):
    __tablename__ = 'order'
    id = Column(Integer, primary_key=True)
    number = Column(String(10))
    customer_id = Column(Integer, ForeignKey('customer.id'), nullable=True)
    session_id = Column(Integer, ForeignKey('session.id'))
    created_on = Column(DateTime, default=func.now())
    total_price = Column(Float)
    pricelist_id = Column(Integer, ForeignKey('pricelist.id'))



    order_line = relationship("OrderLine", back_populates="order")
    customer = relationship("Customer",back_populates="order")
    session = relationship("Session", back_populates="order")
    pricelist = relationship("Pricelist" , back_populates="order")

    program_item = relationship("ProgramItem", back_populates="order")
