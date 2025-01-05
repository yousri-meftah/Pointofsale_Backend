from pydantic import BaseModel
from .base import OurBaseModel, OurBaseModelOut

class ProgramItemCreate(BaseModel):
    code: str
    status_id: int
    program_id: int
    order_id: int

class ProgramItemUpdate(BaseModel):
    code: str | None
    status_id: int | None
    program_id: int | None
    order_id: int | None

class ProgramItemOut(BaseModel):
    id: int
    code: str
    status_id: int
    program_id: int
    order_id: int


class ProgramItem(OurBaseModel):
    code: str
    status_id: int
    program_id: int
    order_id: int
