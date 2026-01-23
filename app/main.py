from uuid import UUID
from fastapi import FastAPI, Request

from app.database.db import Base, engine

from app.routers.user_router import router as user_router
from app.routers.auth_router import router as auth_router
from app.routers.restaurant_router import router as restaurant_router
from app.routers.menu_router import router as menu_router
from app.routers.order_router import router as order_router
from app.routers.payment_router import router as payment_router
from app.routers.webhook_router import router as webhook_router

from app.models.payment import Payment

app = FastAPI()

@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)


app.include_router(user_router)
app.include_router(auth_router)
app.include_router(restaurant_router)
app.include_router(menu_router)
app.include_router(order_router)
app.include_router(payment_router)
app.include_router(webhook_router)


@app.get("/")
def home():
    return {"message": "Database connected!"}
