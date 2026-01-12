from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm

from app.database.db import get_db
from app.models.user import User
from app.schemas.user_schema import UserCreate, UserRead
from app.utils.hash import hash_password, verify_password
from app.core.security import create_access_token

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register", response_model=UserRead)
def register_user(payload: UserCreate, db: Session = Depends(get_db)):
    # Check if first user
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



@router.post("/login")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(401, "Invalid credentials")

    token = create_access_token({"sub": str(user.id)})
    return {"access_token": token, "token_type": "bearer"}
