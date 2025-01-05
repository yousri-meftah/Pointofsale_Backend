from pydantic import BaseModel
from .base import OurBaseModel, OurBaseModelOut
from typing import  Optional

class CategoryCreate(BaseModel):
    name: str
    description: str
    icon_name: str

class CategoryUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    icon_name: Optional[str] = None



class Category(OurBaseModel):
    id:int
    name: str
    description: str
    icon_name: str

class CategoryOut(OurBaseModelOut):
    categories : Optional[list[Category]]=None

