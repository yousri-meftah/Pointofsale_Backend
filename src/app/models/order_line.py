from sqlalchemy import Column, Integer, Float, ForeignKey
from sqlalchemy.orm import relationship
from ..models import Base

class OrderLine(Base):
    __tablename__ = 'order_line'
    id = Column(Integer, primary_key=True)
    order_id = Column(Integer, ForeignKey('order.id'))
    product_id = Column(Integer, ForeignKey('product.id'))
    unit_price = Column(Float)
    quantity = Column(Integer)
    total_price = Column(Float)

    order = relationship("Order", back_populates="order_line")
    product = relationship("Product", back_populates="order_line")
