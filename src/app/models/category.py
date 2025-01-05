from sqlalchemy import Column, Integer, String
from ..models import Base
from sqlalchemy.orm import relationship


class Category(Base):
    __tablename__ = "category"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    description = Column(String, nullable=True)
    icon_name = Column(String, nullable=True)

    products = relationship("Product", back_populates="category")

