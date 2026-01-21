import stripe
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID

from app.database.db import get_db
from app.models.order import Order
from app.models.payment import Payment
from app.models.user import User
from app.core.security import get_current_user
from app.core.config import settings

router = APIRouter(prefix="/payments", tags=["Payments"])
stripe.api_key = settings.STRIPE_SECRET_KEY


@router.post("/create/{order_id}")
def create_payment_checkout(
    order_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    order = db.query(Order).filter(Order.id == order_id).first()

    if not order:
        raise HTTPException(404, "Order not found")

    if order.user_id != current_user.id:
        raise HTTPException(403, "Not your order")

    if order.status == "PAID":
        raise HTTPException(400, "Order already paid")

    session = stripe.checkout.Session.create(
        mode="payment",
        payment_method_types=["card"],
        line_items=[
            {
                "price_data": {
                    "currency": "inr",
                    "product_data": {"name": f"Order {order.id}"},
                    "unit_amount": int(order.total_amount * 100),
                },
                "quantity": 1,
            }
        ],
        success_url=f"http://localhost:8000/payments/success/{order.id}",
        cancel_url=f"http://localhost:8000/payments/cancel/{order.id}",
        metadata={
            "order_id": str(order.id),
            "user_id": str(current_user.id),
        },
    )

    payment = Payment(
        order_id=order.id,
        user_id=current_user.id,
        stripe_session_id=session.id,
        amount=order.total_amount,
        currency="INR",
        status="PENDING",
        stripe_response=session.to_dict(),
    )

    db.add(payment)
    db.commit()

    return {"checkout_url": session.url}


@router.get("/success/{order_id}")
def payment_success_page(order_id: UUID):

    return {
        "message": "Payment successful",
        "order_id": str(order_id),
        "note": "Your payment has been confirmed and a confirmation email has been sent.",
    }


@router.get("/cancel/{order_id}")
def payment_cancel_page(order_id: UUID):
    return {
        "message": "Payment cancelled",
        "order_id": str(order_id),
        "note": "You can retry the payment from your orders page.",
    }
