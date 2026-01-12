from fastapi import FastAPI, Request

from app.database.db import Base, engine

from app.routers.user_router import router as user_router
from app.routers.auth_router import router as auth_router
from app.routers.restaurant_router import router as restaurant_router


app = FastAPI()

Base.metadata.create_all(bind=engine)


app.include_router(user_router)
app.include_router(auth_router)
app.include_router(restaurant_router)



@app.get("/")
def home():
    return {"message": "Database connected!"}
