from sqlalchemy import Column, Integer

from ..models import Base


class Blacklist(Base):
    __tablename__ = "blacklist"
    id:int = Column(Integer, primary_key=True, index=True, autoincrement=True)
    token = Column(Integer)



