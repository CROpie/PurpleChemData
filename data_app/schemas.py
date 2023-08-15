from pydantic import BaseModel


class UserCreate(BaseModel):
    username: str


class User(BaseModel):
    id: int
    full_name: str | None = None

    class Config:
        orm_mode = True


class TokenData(BaseModel):
    username: str | None = None
