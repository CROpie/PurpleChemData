from pydantic import BaseModel
from typing import Optional, Union
from enum import Enum as PyEnum


class CSVUserData(BaseModel):
    id: int
    username: str
    full_name: str


class CSVChemical(BaseModel):
    id: Optional[int] = None
    CAS: str
    chemicalName: str
    MW: Optional[str] = None
    MP: Optional[str] = None
    BP: Optional[str] = None
    density: Optional[str] = None
    smile: Optional[str] = None
    inchi: Optional[str] = None


class CSVSupplier(BaseModel):
    id: Optional[int] = None
    supplierName: str


class AmountUnitEnum(str, PyEnum):
    mg = "mg"
    mL = "mL"
    g = "g"
    L = "L"


class StatusEnum(str, PyEnum):
    submitted = "submitted"
    ordered = "ordered"
    received = "received"


class CSVOrder(BaseModel):
    user: int
    chemical: Optional[Union[int, str]] = None
    supplier: Optional[Union[int, str]] = None
    status: StatusEnum
    amount: int
    amountUnit: AmountUnitEnum
    supplierPN: Optional[str] = None


class CSVGlobal(BaseModel):
    userDataList: list[CSVUserData]
    chemicalList: list[CSVChemical]
    supplierList: list[CSVSupplier]
    orderList: list[CSVOrder]
