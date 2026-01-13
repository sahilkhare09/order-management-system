from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID

from app.database.db import get_db
from app.models.order import Order
from app.models.order_item import OrderItem
from app.models.restaurant import Restaurant
from app.models.menu import Menu
from app.models.user import User
from app.schemas.order_schema import (OrderCreate, OrderRead, OrderStatusUpdate,    )

from app.core.security import get_current_user

router = APIRouter(prefix="/orders", tags=["Orders"])


def admin_only(user: User):
    if user.role.lower() != "admin":
        raise HTTPException(403, "Admin access required")



@router.post("/with-items", response_model=OrderRead)
def place_order_with_items(
    payload: OrderCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        restaurant = db.query(Restaurant).filter(
            Restaurant.id == payload.restaurant_id
        ).first()
        if not restaurant:
            raise HTTPException(404, "Restaurant not found")

        menu_ids = [item.menu_id for item in payload.items]

        menu_items = db.query(Menu).filter(
            Menu.id.in_(menu_ids),
            Menu.restaurant_id == payload.restaurant_id,
            Menu.is_available.is_(True)
        ).all()

        if len(menu_items) != len(set(menu_ids)):
            raise HTTPException(400, "Invalid or unavailable menu items")

        order = Order(
            user_id=current_user.id,
            restaurant_id=payload.restaurant_id,
            status="Placed",
            total_amount=0
        )
        db.add(order)
        db.flush()

        menu_map = {m.id: m for m in menu_items}
        total_amount = 0

        order_items = []
        for item in payload.items:
            menu = menu_map[item.menu_id]
            item_total = menu.price * item.quantity
            total_amount += item_total

            order_items.append(
                OrderItem(
                    order_id=order.id,
                    menu_id=menu.id,
                    quantity=item.quantity,
                    price_at_order=menu.price
                )
            )

        db.add_all(order_items)


        order.total_amount = total_amount

        db.commit()
        db.refresh(order)
        return order

    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(500, f"Order failed: {str(e)}")

    
@router.get("", response_model=list[OrderRead])
def get_my_orders(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return db.query(Order).filter(
        Order.user_id == current_user.id
    ).all()




@router.get("/{order_id}", response_model=OrderRead
)
def get_order_detail(
    order_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    order = db.query(Order).filter(Order.id == order_id).first()

    if not order:
        raise HTTPException(404, "Order not found")

    if order.user_id != current_user.id and current_user.role.lower() != "admin":
        raise HTTPException(403, "Access denied")

    return order



@router.put("/{order_id}/status", response_model=OrderRead)
def update_order_status(
    order_id: UUID,
    payload: OrderStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    admin_only(current_user)

    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(404, "Order not found")

    order.status = payload.status
    db.commit()
    db.refresh(order)

    return order


