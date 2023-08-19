from enum import Enum as PyEnum
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

## ORDER CHEMICAL ##


# Locations List
class LoadLocation(BaseModel):
    id: int
    locationName: str
    # user_id: int
    # user: User


# Orders List
class Chemical(BaseModel):
    id: int
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


class LoadOrder(BaseModel):
    id: int
    # user_id: int
    # user: User
    chemical_id: int
    chemical: Chemical
    supplier_id: int
    supplier: Supplier
    location_id: Optional[int] = None
    location: Optional[Location] = None
    status: StatusEnum
    amount: int
    amountUnit: AmountUnitEnum
    isConsumed: bool
    orderDate: datetime
    supplierPN: Optional[str] = None


# Locations And Orders Dictionary
class LoadLocationsAndOrdersLists(BaseModel):
    locationsList: list[LoadLocation]
    ordersList: list[LoadOrder]


## INVENTORY ##
class LoadSupplier(BaseModel):
    id: int
    supplierName: str
