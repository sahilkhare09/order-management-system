from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
from jose import jwt, JWTError
from datetime import datetime, timedelta

from app.database.db import get_db
from app.models.user import User
from app.schemas.user_schema import UserCreate, UserRead
from app.schemas.auth_schema import Token, ForgotPasswordRequest, ResetPasswordRequest
from app.utils.token import generate_reset_token
from app.utils.hash import hash_password, verify_password
from app.core.config import settings
from app.core.security import (create_access_token, create_refresh_token,)

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register", response_model=UserRead)
def register_user(payload: UserCreate, db: Session = Depends(get_db)):
    is_first_user = db.query(User).count() == 0

    user = User(
        first_name=payload.first_name,
        last_name=payload.last_name,
        email=payload.email,
        phone=payload.phone,
        password=hash_password(payload.password),
        role="admin" if is_first_user else "user",
        address=payload.address,
    )

    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.post("/login", response_model=Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access_token = create_access_token(
        data={"sub": str(user.id)}
    )
    refresh_token = create_refresh_token(
        data={"sub": str(user.id)}
    )

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
}



@router.post("/refresh")
def refresh_access_token(refresh_token: str):
    try:
        payload = jwt.decode(
            refresh_token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )

        if payload.get("type") != "refresh":
            raise HTTPException(status_code=401, detail="Invalid refresh token")

        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid refresh token")

        new_access_token = create_access_token(
            data={"sub": user_id}
        )

        return {
            "access_token": new_access_token,
            "token_type": "bearer",
        }

    except JWTError:
        raise HTTPException(status_code=401, detail="Refresh token expired or invalid")

@router.post("/forgot-password")
def forgot_password(
    payload: ForgotPasswordRequest,
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.email == payload.email).first()

    if not user:
        return {"message": "If account exists, reset link sent"}

    token = generate_reset_token()
    user.reset_token = token
    user.reset_token_expiry = datetime.utcnow() + timedelta(minutes=30)

    db.commit()

    print(f"RESET TOKEN for {user.email}: {token}")

    return {"message": "Password reset link sent"}


@router.post("/reset-password")
def reset_password(
    payload: ResetPasswordRequest,
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(
        User.reset_token == payload.token
    ).first()

    if not user:
        raise HTTPException(400, "Invalid or expired token")

    if user.reset_token_expiry < datetime.utcnow():
        raise HTTPException(400, "Token expired")

    user.password = hash_password(payload.new_password)
    user.reset_token = None
    user.reset_token_expiry = None

    db.commit()

    return {"message": "Password reset successful"}
