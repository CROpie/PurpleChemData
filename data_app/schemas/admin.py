from enum import Enum as PyEnum
from pydantic import BaseModel
from typing import Optional


class PatchStatus(BaseModel):
    id: int
    status: str


class PatchUser(BaseModel):
    id: int
    full_name: str


class PatchChemical(BaseModel):
    id: int
    CAS: str
    chemicalName: Optional[str] = None
    MW: Optional[str] = None
    MP: Optional[str] = None
    BP: Optional[str] = None
    density: Optional[str] = None
    smile: Optional[str] = None
    inchi: Optional[str] = None


class PatchSupplier(BaseModel):
    id: int
    supplierName: str


class AmountUnitEnum(str, PyEnum):
    mg = "mg"
    mL = "mL"
    g = "g"
    L = "L"


class PatchOrder(BaseModel):
    id: int
    amount: int
    amountUnit: AmountUnitEnum
    isConsumed: bool
    supplierPN: Optional[str] = None


class DeleteAny(BaseModel):
    id: int
