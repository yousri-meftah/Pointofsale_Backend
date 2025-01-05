from datetime import date
from pydantic import BaseModel
from .base import OurBaseModel, OurBaseModelOut, PagedResponse

class PricelistLineCreate(OurBaseModel):
    pricelist_id: int
    product_id: int
    new_price: float
    start_date: date
    end_date: date

class PricelistLineUpdate(OurBaseModel):
    product_id: int| None
    new_price: float| None

class PricelistLineOut(OurBaseModelOut):
    id: int
    pricelist_id: int
    product_id: int
    new_price: float
    start_date: date
    end_date: date

class PricelistLineOut_base(OurBaseModel):
    id: int| None
    pricelist_id: int| None
    product_name : str| None
    product_id: int| None
    new_price: float| None
    start_date: date| None
    end_date: date| None
