import stripe
from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.models.order import Order
from app.core.config import settings

stripe.api_key = settings.STRIPE_SECRET_KEY


def create_stripe_payment_intent(
    db: Session,
    order_id: str,
):
    order = db.query(Order).filter(Order.id == order_id).first()

    if not order:
        raise HTTPException(404, "Order not found")

    if not order.total_amount or order.total_amount <= 0:
        raise HTTPException(400, "Invalid order amount")

    amount_in_paise = int(order.total_amount * 100)

    intent = stripe.PaymentIntent.create(
        amount=amount_in_paise,
        currency="inr",
        metadata={
            "order_id": str(order.id),
        },
        automatic_payment_methods={"enabled": True},
    )

    return intent
