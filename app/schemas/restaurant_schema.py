from pydantic import BaseModel
from uuid import UUID
from typing import Optional

class RestaurantCreate(BaseModel):
    name: str
    description: Optional[str] = None
    address: str
    is_open: bool = True


class RestaurantUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    address: Optional[str] = None
    is_open: Optional[bool] = None


class RestaurantRead(BaseModel):
    id: UUID
    name: str
    description: Optional[str]
    address: str
    is_open: bool

    class Config:
        from_attributes = True
