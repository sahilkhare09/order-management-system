import stripe
from fastapi import APIRouter, Request, HTTPException, Depends
from sqlalchemy.orm import Session

from app.core.config import settings
from app.database.db import get_db
from app.models.order import Order

router = APIRouter(prefix="/stripe", tags=["Stripe Webhook"])

stripe.api_key = settings.STRIPE_SECRET_KEY
endpoint_secret = settings.STRIPE_WEBHOOK_SECRET


@router.post("/stripe")
async def stripe_webhook(request: Request):
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")

    try:
        event = stripe.Webhook.construct_event(
            payload=payload,
            sig_header=sig_header,
            secret=endpoint_secret,
        )
    except stripe.error.SignatureVerificationError:
        raise HTTPException(status_code=400, detail="Invalid signature")
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid payload")

    db: Session = SessionLocal()

    try:
        if event["type"] == "payment_intent.succeeded":
            intent = event["data"]["object"]

            payment = db.query(Payment).filter(
                Payment.stripe_payment_intent_id == intent["id"]
            ).first()

            if payment:
                payment.status = "SUCCESS"

                order = db.query(Order).filter(
                    Order.id == payment.order_id
                ).first()

                if order:
                    order.status = "PAID"

                db.commit()

        elif event["type"] == "payment_intent.payment_failed":
            intent = event["data"]["object"]

            payment = db.query(Payment).filter(
                Payment.stripe_payment_intent_id == intent["id"]
            ).first()

            if payment:
                payment.status = "FAILED"
                db.commit()

    finally:
        db.close()

    return {"status": "ok"}
