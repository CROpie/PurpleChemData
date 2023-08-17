from enum import Enum as PyEnum
from pydantic import BaseModel
from typing import Optional

## class X = incoming values
## class sendX = return values


class TokenData(BaseModel):
    id: Optional[int] = None


class User(BaseModel):
    id: int
    username: str
    full_name: str | None = None

    class Config:
        orm_mode = True


class Location(BaseModel):
    locationName: str
    # user_id: int is retrieved from the token


class ReturnLocation(Location):
    id: int


class LocationResponse(BaseModel):
    data: Optional[ReturnLocation] = None
    error: Optional[str] = None


class Chemical(BaseModel):
    CAS: str
    chemicalName: Optional[str] = None
    MW: Optional[str] = None
    MP: Optional[str] = None
    BP: Optional[str] = None
    density: Optional[str] = None
    smile: Optional[str] = None
    inchi: Optional[str] = None


class ReturnChemical(Chemical):
    id: int


class ChemicalResponse(BaseModel):
    data: Optional[int] = None
    error: Optional[str] = None


class ReturnChemicalId(BaseModel):
    id: int


class Supplier(BaseModel):
    supplierName: str


class FullSupplier(Supplier):
    id: int


class SupplierResponse(BaseModel):
    data: Optional[int] = None
    error: Optional[str] = None


class GetSuppliersResponse(BaseModel):
    data: list[FullSupplier]
    error: Optional[str] = None


class AmountUnitEnum(str, PyEnum):
    mg = "mg"
    mL = "mL"
    g = "g"
    L = "L"


class Order(BaseModel):
    # user_id: int is retrieved from the token
    chemical_id: int
    supplier_id: int
    amount: int
    amountUnit: AmountUnitEnum
    supplerPN: Optional[str] = None


# class ReturnOrder(BaseModel):
#     id: int


# class OrderResponse(BaseModel):
#     data: Optional[int] = None
#     error: Optional[str] = None


class ReturnOrder(BaseModel):
    id: int
    user_id: int


class OrderResponse(BaseModel):
    data: Optional[ReturnOrder] = None
    error: Optional[str] = None


class OrderWithChemical(BaseModel):
    order: Order
    chemical: Chemical


class UserOrders(User):
    orders: list[OrderWithChemical] = []
