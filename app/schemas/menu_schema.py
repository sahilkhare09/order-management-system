from pydantic import BaseModel
from uuid import UUID
from typing import Optional

class MenuCreate(BaseModel):
    restaurant_id: UUID
    name: str
    price: float
    is_available: bool = True


class MenuUpdate(BaseModel):
    name: Optional[str] = None
    price: Optional[float] = None
    is_available: Optional[bool] = None


class MenuRead(BaseModel):
    id: UUID
    restaurant_id: UUID
    name: str
    price: float
    is_available: bool

    class Config:
        from_attributes = True
