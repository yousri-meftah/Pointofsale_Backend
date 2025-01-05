from enum import Enum
class Role(str,Enum):
    SUPER_USER = 'SUPER_USER'
    ADMIN = 'ADMIN'
    VENDOR = 'VENDOR'
    INVENTORY_MANAGER = 'INVENTORY_MANAGER'
