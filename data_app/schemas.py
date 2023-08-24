from enum import Enum as PyEnum
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


from pydantic import BaseModel
from typing import Optional


class TokenData(BaseModel):
    id: Optional[int] = None


class User(BaseModel):
    id: int  # id comes from Auth database
    username: str
    full_name: str


class ChemicalIn(BaseModel):
    CAS: str
    chemicalName: Optional[str] = None
    MW: Optional[str] = None
    MP: Optional[str] = None
    BP: Optional[str] = None
    density: Optional[str] = None
    smile: Optional[str] = None
    inchi: Optional[str] = None


class Chemical(ChemicalIn):
    id: int


class LocationIn(BaseModel):
    locationName: str


class Location(LocationIn):
    id: int


class SupplierIn(BaseModel):
    supplierName: str


class Supplier(SupplierIn):
    id: int


class StatusEnum(str, PyEnum):
    submitted = "submitted"
    ordered = "ordered"
    received = "received"


class AmountUnitEnum(str, PyEnum):
    mg = "mg"
    mL = "mL"
    g = "g"
    L = "L"


class OrderIn(BaseModel):
    chemical_id: Optional[int] = None  # get straight after chem added
    supplier_id: int
    amount: int
    amountUnit: AmountUnitEnum
    supplierPN: Optional[str] = None


class Order(OrderIn):
    id: Optional[int] = None
    user_id: int
    user: User
    chemical: Chemical
    supplier: Supplier
    location_id: Optional[int] = None
    location: Optional[Location] = None
    status: StatusEnum
    isConsumed: bool
    orderDate: datetime


class QueryOrder(BaseModel):
    id: int
    amount: int
    amountUnit: AmountUnitEnum
    isConsumed: bool
    status: StatusEnum
    supplierPN: Optional[str] = None
    orderDate: datetime
    CAS: str
    chemicalName: Optional[str] = None
    full_name: str
    supplierName: str


class ChemOrderIn(BaseModel):
    chemicalData: ChemicalIn
    orderData: OrderIn


class Inventory(BaseModel):
    locationsList: list[Location]
    ordersList: list[Order]


class InventoryPatchIn(BaseModel):
    id: int  ## order id
    amount: int
    isConsumed: bool
    location_id: int | None


class InventoryPatch(BaseModel):
    id: int  ## order id
    amount: int
    isConsumed: bool
    location: Location | None


class CSV(BaseModel):
    userDataList: list[User]
    chemicalList: list[Chemical]
    supplierList: list[Supplier]
    orderList: list[Order]
