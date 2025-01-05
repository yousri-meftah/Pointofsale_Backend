from sqlalchemy import Column, Integer, Float, Date, ForeignKey
from sqlalchemy.orm import relationship
from ..models import Base

class PricelistLine(Base):
    __tablename__ = 'pricelist_line'
    id = Column(Integer, primary_key=True)
    pricelist_id = Column(Integer, ForeignKey('pricelist.id'))
    product_id = Column(Integer, ForeignKey('product.id'))
    new_price = Column(Float)
    min_quantity = Column(Integer)
    start_date = Column(Date)
    end_date = Column(Date)

    pricelist = relationship("Pricelist", back_populates="pricelist_lines")
    product = relationship("Product", back_populates="pricelist_lines")
