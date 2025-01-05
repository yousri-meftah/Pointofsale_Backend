from typing import Optional
from pydantic import BaseModel
from .base import OurBaseModel, OurBaseModelOut, PagedResponse
from typing import List, Dict

class Customer(OurBaseModel):
    name: str
    email: str
    pricelist_id: Optional[int]

class CustomerOut_withstatus(OurBaseModelOut):
    name: Optional[str]=None
    email: Optional[str]=None
    pricelist_id: Optional[int]=None

class CustomerOut(OurBaseModel):
    id : int
    name: Optional[str]=None
    email: str
    pricelist_id: int| None

class CustomersOut(PagedResponse):
    list: list[CustomerOut] | None


class CustomerCreate(BaseModel):
    name: str
    email: str
    pricelist_id: Optional[int]=None

class CustomerUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    pricelist_id: Optional[int] = None


class BulkAddResponse(OurBaseModel):
    status: int
    message: str
    errors: Optional[List[Dict[str, str]]] = None
    added_customers: Optional[List[CustomerOut]] = None