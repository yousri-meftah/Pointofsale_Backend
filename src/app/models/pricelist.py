from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.orm import relationship
from ..models import Base

class Pricelist(Base):
    __tablename__ = 'pricelist'
    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    description = Column(Text)

    customers = relationship("Customer", back_populates="pricelist")

    order = relationship("Order", back_populates="pricelist")
    pricelist_lines = relationship("PricelistLine", back_populates="pricelist")

