from uuid import UUID
from pydantic import BaseModel, EmailStr
from typing import Optional


class UserCreate(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    phone: str
    password: str
    address: Optional[str] = None


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None


class UserRead(BaseModel):
    id: UUID
    first_name: str
    last_name: str
    email: EmailStr
    phone: str
    role: str
    address: Optional[str]

    class Config:
        from_attributes = True


class UserProfile(BaseModel):
    id: UUID
    first_name: str
    last_name: str
    email: EmailStr
    phone: str
    role: str
    address: Optional[str]

    class Config:
        from_attributes = True

