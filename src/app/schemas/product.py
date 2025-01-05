from typing import Optional
from pydantic import BaseModel
from .base import OurBaseModel, OurBaseModelOut, PagedResponse

class Product(OurBaseModel):
    name: str
    description: Optional[str] = None
    unit_price: float
    quantity: int
    image_link: Optional[str] = None
    category_id: int

class ProductOut(OurBaseModel):
    id : Optional[int] = None
    name: Optional[str] = None
    description: Optional[str] = None
    unit_price: Optional[float] = None
    quantity: Optional[int] = None
    image_link: Optional[str] = None
    category_id: Optional[int] = None

class Product_with_Pricelist_Out(OurBaseModel):
    id : Optional[int] = None
    name: Optional[str] = None
    description: Optional[str] = None
    unit_price: Optional[float] = None
    new_price: Optional[float] = None
    quantity: Optional[int] = None
    image_link: Optional[str] = None
    category_id: Optional[int] = None

class return_products(OurBaseModelOut):
    products: Optional[list[ProductOut] ]= None

class ProductsOut(PagedResponse):
    products: list[ProductOut] | None

class Products_with_pricelist_Out(PagedResponse):
    products: list[Product_with_Pricelist_Out] | None

class ProductCreate(BaseModel):
    name: str
    description: str
    unit_price: float
    quantity: int
    image_link: Optional[str] = None
    category_id: int

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    unit_price: Optional[float] = None
    quantity: Optional[int] = None
    image_link: Optional[str] = None
    category_id: Optional[int] = None


