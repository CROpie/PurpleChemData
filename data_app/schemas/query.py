from enum import Enum as PyEnum
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class User(BaseModel):
    id: int
    username: str
    full_name: str | None = None


class Chemical(BaseModel):
    # id: int
    CAS: str
    chemicalName: Optional[str] = None
    MW: Optional[str] = None
    MP: Optional[str] = None
    BP: Optional[str] = None
    density: Optional[str] = None
    smile: Optional[str] = None
    inchi: Optional[str] = None


class Supplier(BaseModel):
    id: int
    supplierName: str


class Location(BaseModel):
    id: int
    locationName: str


class StatusEnum(str, PyEnum):
    submitted = "submitted"
    ordered = "ordered"
    received = "received"


class AmountUnitEnum(str, PyEnum):
    mg = "mg"
    mL = "mL"
    g = "g"
    L = "L"


class QueryOrder(BaseModel):
    id: int
    amount: int
    amountUnit: AmountUnitEnum
    isConsumed: bool
    orderDate: datetime
    status: StatusEnum
    supplierPN: Optional[str] = None

    fullname: str

    CAS: str
    chemicalName: Optional[str] = None

    supplierName: str
