from pydantic import BaseModel
from uuid import UUID
from typing import List
from datetime import datetime



class OrderItemCreate(BaseModel):
    menu_id: UUID
    quantity: int


class OrderItemRead(BaseModel):
    id: UUID
    menu_id: UUID
    quantity: int
    price_at_order: float

    class Config:
        from_attributes = True



class OrderCreate(BaseModel):
    restaurant_id: UUID
    items: List[OrderItemCreate]


class OrderStatusUpdate(BaseModel):
    status: str


class OrderRead(BaseModel):
    id: UUID
    user_id: UUID
    restaurant_id: UUID
    status: str
    total_amount: float
    created_at: datetime
    items: List[OrderItemRead]

    class Config:
        from_attributes = True
