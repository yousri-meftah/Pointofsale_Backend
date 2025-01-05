from pydantic import BaseModel
from .base import OurBaseModel, OurBaseModelOut , PagedResponse

class OrderLine(OurBaseModel):
    product_id: int
    unit_price: float
    quantity: int
    total_price: float

class OrderLineOut(OurBaseModelOut):
    product_id: int
    unit_price: float
    quantity: int
    total_price: float

class OrderLinesOut(PagedResponse):
    list: list[OrderLineOut] | None


class OrderLineCreate(BaseModel):
    order_id: int
    product_id: int
    unit_price: float
    quantity: int
    total_price: float

class OrderLineUpdate(BaseModel):
    order_id: int
    product_id: int
    unit_price: float
    quantity: int
    total_price: float
