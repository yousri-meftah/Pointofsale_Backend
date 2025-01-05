from datetime import datetime
from typing import Optional,Dict
from pydantic import BaseModel
from .base import OurBaseModel, OurBaseModelOut, PagedResponse
from .order_line import OrderLine
from ..models import ProgramItem

class Order(OurBaseModel):
    number: str
    customer_id: Optional[int] = None
    session_id: int
    created_on: datetime
    order_lines: list[OrderLine]

class OrderOut(OurBaseModel):
    id:int
    number: Optional[int] = None
    customer_id: Optional[int] = None
    session_id: int
    created_on: Optional[datetime] = None
    total_price: float
    pricelist_id: Optional[int] = None
    program_item: Optional[list[str]] = []

class OrdersOut(PagedResponse):
    list: list[OrderOut]

class OrderCreate(BaseModel):
    customer_id: Optional[int] = None
    products_ids : list[tuple[int, int]]
    session_id: int
    created_on: datetime
    total_price: float
    pricelist_id: Optional[int] = None
    program_item_id: Optional[list[str]] = None

class OrderUpdate(BaseModel):
    number: Optional[str] = None
    customer_id: Optional[int] = None
    session_id: Optional[int] = None
    created_on: Optional[datetime] = None
    total_price: Optional[float] = None
    pricelist_id: Optional[int] = None
    program_item_id: Optional[int] = None


class OrderLineIn(BaseModel):
    product_id: int
    quantity: int
    price: float  # Assuming price is included for frontend calculations

class OrderIn(BaseModel):
    session_id: int
    order_lines: list[OrderLineIn]
    customer_id: Optional[int] = None
    program_code: Optional[str] = None
    pricelist_id: Optional[int] = None


class Discount(BaseModel):
    type: str
    id: int
    amount: float

class PriceCalculationOut(BaseModel):
    original_total_price: float
    total_price: float
    discounts: list[Discount]

class DiscountDetail(BaseModel):
    component: str
    discount: float
    description: Optional[str] = None

class CalculatedOrder(BaseModel):
    total_price: float
    discounts: list[DiscountDetail]


class OrderLineSchema( OurBaseModel):
    product_id: int
    unit_price: float
    quantity: int
    total_price: float

class order_details(OurBaseModelOut):
    program_item : Optional[list[str]] = []
    session_id: int
    customer_name:Optional[str] = None
    total_price: float
    pricelist_name: Optional[str] = None
    code : Optional[str] = None
    products : Optional[list[OrderLineSchema]] = []
