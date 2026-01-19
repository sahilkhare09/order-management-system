from pydantic import BaseModel, EmailStr
from typing import Optional



class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    refresh_token: Optional[str] = None
    expires_in: Optional[int] = None 


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenData(BaseModel):
    sub: Optional[str] = None
    exp: Optional[int] = None
    type: Optional[str] = None



class RefreshRequest(BaseModel):
    refresh_token: str


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str