from pydantic import BaseModel
from .base import OurBaseModel, OurBaseModelOut , PagedResponse
from typing import Optional,Dict,List
from .pricelist_line import PricelistLineOut_base


class PricelistCreate(BaseModel):
    name: str
    description: str

class PricelistUpdate(OurBaseModel):
    name: Optional[str] = None
    description: Optional[str] = None

class PricelistOut(OurBaseModelOut):
    name: str| None
    description: str | None

class Pricelist(OurBaseModel):
    id : int
    name: str| None
    description: str| None

class PricelistsPagedResponse(OurBaseModelOut):
    items: Optional[list[Pricelist]] | None

class pricelist_with_lines(OurBaseModelOut):
    data: Dict[int, List[PricelistLineOut_base]]