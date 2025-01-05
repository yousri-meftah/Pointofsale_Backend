
import re
from typing import List, Optional
from pydantic import BaseModel,EmailStr, validator
from sqlalchemy import DateTime
from app.enums import AccountStatus, ContractType,Gender
from datetime import date
from .base import OurBaseModel


class TokenResponse(OurBaseModel):
    access_token: str
    refresh_token: str
    expires_in: int

class ActivateAccount(OurBaseModel):
    password: str
    confirmPass: str
    code: int


class resetPassword(OurBaseModel):
    password: str
    confirmPass: str
    code : int


class forgetPassword(OurBaseModel):
    email: str