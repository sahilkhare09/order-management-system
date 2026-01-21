import stripe
from fastapi import APIRouter, Request, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session

from app.core.config import settings
from app.database.db import get_db
from app.models.payment import Payment
from app.models.order import Order
from app.utils.email import send_order_email

router = APIRouter(prefix="/webhook", tags=["Webhook"])
stripe.api_key = settings.STRIPE_SECRET_KEY


@router.post("/stripe")
async def stripe_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):

    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")

    try:
        event = stripe.Webhook.construct_event(
            payload,
            sig_header,
            settings.STRIPE_WEBHOOK_SECRET,
        )
    except Exception:
        raise HTTPException(400, "Webhook error")

    if event["type"] != "checkout.session.completed":
        return {"status": "ignored"}

    session = event["data"]["object"]

    if session.get("payment_status") != "paid":
        return {"status": "not_paid"}

    payment = (
        db.query(Payment).filter(Payment.stripe_session_id == session["id"]).first()
    )

    if not payment or payment.status == "SUCCESS":
        return {"status": "already_processed"}

    order = db.query(Order).filter(Order.id == session["metadata"]["order_id"]).first()

    if not order or not order.user.email:
        return {"status": "missing_email"}

    email = order.user.email
    order_id = str(order.id)
    amount = payment.amount

    payment.status = "SUCCESS"
    order.status = "PAID"
    db.commit()

    background_tasks.add_task(
        send_order_email, to_email=email, order_id=order_id, amount=amount
    )

    return {"status": "ok"}
