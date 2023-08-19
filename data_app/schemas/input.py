from enum import Enum as PyEnum
from pydantic import BaseModel
from typing import Optional

## USER LOCATION CHEMICAL SUPPLIER ORDER


class NewUser(BaseModel):
    id: int
    username: str
    full_name: str | None = None


class NewLocation(BaseModel):
    locationName: str


class OutLocation(BaseModel):
    id: int
    locationName: str


class NewChemical(BaseModel):
    CAS: str
    chemicalName: Optional[str] = None
    MW: Optional[str] = None
    MP: Optional[str] = None
    BP: Optional[str] = None
    density: Optional[str] = None
    smile: Optional[str] = None
    inchi: Optional[str] = None


class OutChemical(BaseModel):
    id: int


class NewSupplier(BaseModel):
    supplierName: str


class AmountUnitEnum(str, PyEnum):
    mg = "mg"
    mL = "mL"
    g = "g"
    L = "L"


class NewOrder(BaseModel):
    # user_id: int is retrieved from the token
    chemical_id: int
    supplier_id: int
    amount: int
    amountUnit: AmountUnitEnum
    supplierPN: Optional[str] = None
