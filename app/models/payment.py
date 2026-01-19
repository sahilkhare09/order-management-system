from sqlalchemy import Column, String, Float, ForeignKey, JSON, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid

from app.database.db import Base


class Payment(Base):
    __tablename__ = "payments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    order_id = Column(UUID(as_uuid=True), ForeignKey("orders.id"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    stripe_payment_intent_id = Column(String, nullable=False, unique=True)

    amount = Column(Float, nullable=False)
    currency = Column(String(10), default="INR")

    status = Column(String(20), nullable=False)  # PENDING, SUCCEEDED, FAILED
    payment_method = Column(String(50), nullable=True)

    stripe_response = Column(JSON, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )
