from pydantic import BaseModel
from datetime import date
from .base import OurBaseModel, OurBaseModelOut
from app.enums.program_type import ProgramTypeEnum
from app.enums.code_status import CodeStatusEnum
from pydantic import BaseModel, Field, root_validator, ValidationError,model_validator
from typing import Optional
from typing import List, Dict
from app.models import ProgramItem

class ProgramCreate(BaseModel):
    name: str
    description: str
    program_type: ProgramTypeEnum
    start_date: date
    end_date: date
    discount: Optional[float] = None
    product_buy_id: Optional[int] = None
    product_get_id: Optional[int] = None
    program_status: int
    count : int

    @model_validator(mode="after")
    def check_discount_and_products(cls, values):
        discount = values.discount
        product_buy_id = values.product_buy_id
        product_get_id = values.product_get_id

        if discount is not None and (product_buy_id is not None or product_get_id is not None):
            raise ValueError('If there is a discount, product_buy_id and product_get_id should be null.')
        if discount is None and (product_buy_id is None or product_get_id is None):
            raise ValueError('If product_buy_id and product_get_id are provided, discount should be null.')

        return values

class ProgramUpdate(BaseModel):
    name: str | None
    description: str | None
    start_date: date | None
    end_date: date | None
    discount: float | None
    product_buy_id: int | None
    product_get_id: int | None
    program_status_id: int | None
    count: int | None




class ProgramOut(BaseModel):
    id: int
    name: str
    description: str
    program_type: ProgramTypeEnum
    start_date: date
    end_date: date
    discount: float | None
    product_buy_id: int | None
    product_get_id: int | None
    program_status: int

class ProgramItem_out(OurBaseModel):
    id: int
    code: str
    status: CodeStatusEnum
    order_id: int | None


class programItem_out(BaseModel):
    id: int
    code: Optional[str] = None
    status: CodeStatusEnum
    order_id: Optional[int] = None
    discount: float | None
    product_buy_id: int | None
    product_get_id: int | None



class ProgramItemsMap(OurBaseModelOut):
    programs: List[programItem_out]

class ProgramDetails(BaseModel):
    status: Optional[str] = None
    program_type:str
    discount: Optional[float] = None

class calculate_program(OurBaseModelOut):
    results: Dict[str, ProgramDetails]


class CalculateProgramRequest(OurBaseModel):
    code: List[str]
    total: float
    products: List[int] = []