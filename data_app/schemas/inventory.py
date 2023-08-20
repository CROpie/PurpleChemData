from pydantic import BaseModel


class PatchOrder(BaseModel):
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
