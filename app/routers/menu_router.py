from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID

from app.database.db import get_db
from app.models.menu import Menu
from app.models.restaurant import Restaurant
from app.models.user import User
from app.schemas.menu_schema import MenuCreate, MenuUpdate, MenuRead
from app.core.security import get_current_user

router = APIRouter(prefix="/menus", tags=["Menus"])

def admin_only(user: User):
    if user.role.lower() != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")


@router.post("", response_model=MenuRead)
def create_menu(
    payload: MenuCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    admin_only(current_user)

    restaurant = (
        db.query(Restaurant)
        .filter(Restaurant.id == payload.restaurant_id)
        .first()
    )
    if not restaurant:
        raise HTTPException(404, "Restaurant not found")

    menu = Menu(**payload.dict())
    db.add(menu)
    db.commit()
    db.refresh(menu)
    return menu


@router.get("/{restaurant_id}", response_model=list[MenuRead])
def get_menu_by_restaurant(
    restaurant_id: UUID,
    db: Session = Depends(get_db),
):
    return (
        db.query(Menu)
        .filter(Menu.restaurant_id == restaurant_id)
        .all()
    )


@router.put("/{menu_id}", response_model=MenuRead)
def update_menu(
    menu_id: UUID,
    payload: MenuUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    admin_only(current_user)

    menu = db.query(Menu).filter(Menu.id == menu_id).first()
    if not menu:
        raise HTTPException(404, "Menu item not found")

    for key, value in payload.dict(exclude_unset=True).items():
        setattr(menu, key, value)

    db.commit()
    db.refresh(menu)
    return menu


@router.delete("/{menu_id}")
def delete_menu(menu_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    admin_only(current_user)

    menu = db.query(Menu).filter(Menu.id == menu_id).first()
    if not menu:
        raise HTTPException(404, "Menu item not found")

    db.delete(menu)
    db.commit()
    return {"message": "Menu item deleted successfully"}


