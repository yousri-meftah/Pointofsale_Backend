from datetime import datetime
from .base import OurBaseModel, OurBaseModelOut,PagedResponse
from app.enums import SessionStatusEnum
from typing import Optional


class SessionCreate(OurBaseModel):
    employee_id: int
    opened_at: datetime
    session_status_id: int

class SessionCreateOut(OurBaseModelOut):
    Session_id: Optional[int]  = None

class check_status(OurBaseModelOut):
    session_status :str

class SessionUpdate(OurBaseModel):
    employee_id: int
    closed_at: datetime
    session_status_id: int

class Session(OurBaseModel):
    employee_id: int
    opened_at: datetime
    closed_at: datetime
    session_status: SessionStatusEnum

class SessionOut(OurBaseModelOut):
    employee_id: int
    opened_at: datetime
    closed_at: datetime
    session_status: SessionStatusEnum

class basic_SessionOut(OurBaseModel):
    employee_id: int
    opened_at: datetime
    closed_at: datetime
    session_status: SessionStatusEnum


class SessionsOut(PagedResponse):
    list: list[basic_SessionOut] | None
