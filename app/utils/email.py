import smtplib
import logging
from email.message import EmailMessage
from app.core.config import settings

logger = logging.getLogger(__name__)


def send_order_email(to_email: str, order_id: str, amount: float):
    msg = EmailMessage()
    msg["Subject"] = "Payment Successful – Order Confirmed"
    msg["From"] = settings.EMAIL_FROM
    msg["To"] = to_email

    msg.set_content(f"""
Hello,

Your payment has been completed successfully.

Order ID: {order_id}
Amount Paid: ₹{amount:.2f}

Thank you for ordering with us!

Regards,
Food Order System
""")

    try:
        with smtplib.SMTP(
            settings.EMAIL_HOST, settings.EMAIL_PORT, timeout=10
        ) as server:
            server.starttls()
            server.login(settings.EMAIL_USERNAME, settings.EMAIL_PASSWORD)
            server.send_message(msg)

        logger.info(
            "Payment confirmation email sent",
            extra={"order_id": order_id, "to": to_email},
        )

    except Exception as e:
        logger.error(
            "Failed to send payment email",
            exc_info=e,
            extra={"order_id": order_id, "to": to_email},
        )
