from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID

from app.database.db import get_db
from app.models.user import User
from app.schemas.user_schema import UserRead, UserUpdate, UserProfile
from app.core.security import get_current_user
from app.utils.hash import hash_password

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/profile", response_model=UserProfile)
def get_profile(current_user: User = Depends(get_current_user)):
    return current_user


@router.put("/profile", response_model=UserProfile)
def update_profile(
    payload: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if payload.first_name is not None:
        current_user.first_name = payload.first_name

    if payload.last_name is not None:
        current_user.last_name = payload.last_name

    if payload.phone is not None:
        current_user.phone = payload.phone

    if payload.address is not None:
        current_user.address = payload.address

    db.commit()
    db.refresh(current_user)

    return current_user



@router.get("", response_model=list[UserRead])
def get_all_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role != "admin":
        raise HTTPException(403, "Admin access required")

    return db.query(User).all()


@router.get("/{user_id}", response_model=UserRead)
def get_user_by_id(
    user_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role != "admin":
        raise HTTPException(403, "Admin access required")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(404, "User not found")

    return user


@router.delete("/{user_id}")
def delete_user(
    user_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role != "admin":
        raise HTTPException(403, "Admin access required")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(404, "User not found")

    db.delete(user)
    db.commit()
    return {"message": "User deleted successfully"}
