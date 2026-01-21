from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID


from app.database.db import get_db
from app.models.restaurant import Restaurant
from app.models.user import User
from app.schemas.restaurant_schema import (
    RestaurantCreate,
    RestaurantUpdate,
    RestaurantRead,
)
from app.core.security import get_current_user

router = APIRouter(prefix="/restaurants", tags=["Restaurants"])


def admin_only(user: User):
    if user.role.lower() != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")


@router.post("", response_model=RestaurantRead)
def create_restaurant(
    payload: RestaurantCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    admin_only(current_user)

    restaurant = Restaurant(**payload.dict())
    db.add(restaurant)
    db.commit()
    db.refresh(restaurant)
    return restaurant


@router.get("", response_model=list[RestaurantRead])
def list_restaurants(db: Session = Depends(get_db)):
    return db.query(Restaurant).all()


@router.get("/{restaurant_id}", response_model=RestaurantRead)
def get_restaurant(
    restaurant_id: UUID,
    db: Session = Depends(get_db),
):
    restaurant = db.query(Restaurant).filter(Restaurant.id == restaurant_id).first()
    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurant not found")

    return restaurant


@router.put("/{restaurant_id}", response_model=RestaurantRead)
def update_restaurant(
    restaurant_id: UUID,
    payload: RestaurantUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    admin_only(current_user)

    restaurant = db.query(Restaurant).filter(Restaurant.id == restaurant_id).first()
    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurant not found")

    for key, value in payload.dict(exclude_unset=True).items():
        setattr(restaurant, key, value)

    db.commit()
    db.refresh(restaurant)
    return restaurant


@router.delete("/{restaurant_id}")
def delete_restaurant(
    restaurant_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    admin_only(current_user)

    restaurant = db.query(Restaurant).filter(Restaurant.id == restaurant_id).first()
    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurant not found")

    db.delete(restaurant)
    db.commit()
    return {"message": "Restaurant deleted successfully"}
