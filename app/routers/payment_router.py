from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID

from app.database.db import get_db
from app.models.payment import Payment
from app.models.order import Order
from app.models.user import User
from app.core.security import get_current_user
from app.services.payment_service import create_stripe_payment_intent

router = APIRouter(prefix="/payments", tags=["Payments"])


@router.post("/create/{order_id}")
def create_payment(
    order_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    order = db.query(Order).filter(Order.id == order_id).first()

    if not order:
        raise HTTPException(404, "Order not found")

    if order.user_id != current_user.id:
        raise HTTPException(403, "Not allowed")

    if order.status == "PAID":
        raise HTTPException(400, "Order already paid")

    intent = create_stripe_payment_intent(db, str(order.id))

    payment = Payment(
        order_id=order.id,
        user_id=current_user.id,
        stripe_payment_intent_id=intent.id,
        amount=order.total_amount,
        currency="INR",
        status="PENDING",
        stripe_response=intent.to_dict(),
    )

    db.add(payment)
    db.commit()
    db.refresh(payment)

    return {
        "payment_intent_id": intent.id,
        "client_secret": intent.client_secret,
        "amount": order.total_amount,
        "currency": "INR",
        "status": "payment_pending",
    }
