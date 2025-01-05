from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from ..models import Base

class Customer(Base):
    __tablename__ = 'customer'
    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    email = Column(String(50))
    pricelist_id = Column(Integer, ForeignKey('pricelist.id'))

    pricelist = relationship("Pricelist", back_populates="customers")
    order = relationship("Order", back_populates="customer")
