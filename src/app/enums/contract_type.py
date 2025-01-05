from enum import Enum
class ContractType(str,Enum):
    CDI = 'CDI'
    CDD = 'CDD'
    CIVP = 'CIVP'
    APPRENTI = 'APPRENTI'
