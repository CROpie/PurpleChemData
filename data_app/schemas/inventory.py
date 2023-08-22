from pydantic import BaseModel


class PatchAmountLocation(BaseModel):
    id: int
    amount: int
    location_id: int | None
    isConsumed: bool


class Location(BaseModel):
    id: int
    locationName: str


class OutPatchOrder(BaseModel):
    id: int
    amount: int
    location: Location | None
