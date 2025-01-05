from enum import Enum

class AccountStatus(str,Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
