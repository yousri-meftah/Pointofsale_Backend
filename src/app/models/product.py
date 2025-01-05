from sqlalchemy import Column, Integer, String, Float, Text, ForeignKey
from sqlalchemy.orm import relationship
from ..models import Base

class Product(Base):
    __tablename__ = 'product'
    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    description = Column(Text)
    unit_price = Column(Float)
    quantity = Column(Integer)
    image_link = Column(String(255))
    category_id = Column(Integer, ForeignKey('category.id'))

    category = relationship("Category", back_populates="products")
    order_line = relationship("OrderLine", back_populates="product")
    pricelist_lines = relationship("PricelistLine", back_populates="product")
    programs_buy = relationship("Program", foreign_keys='Program.product_buy_id', overlaps="product_buy")
    programs_get = relationship("Program", foreign_keys='Program.product_get_id', overlaps="product_get")
