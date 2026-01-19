import uuid
from sqlalchemy import Column, String, DateTime
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime

from app.database.db import Base


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False, index=True)
    phone = Column(String, nullable=False)
    password = Column(String, nullable=False)
    role = Column(String, default="user")
    address = Column(String, nullable=True)
    reset_token = Column(String, nullable=True)
    reset_token_expiry = Column(DateTime, nullable=True)
   
