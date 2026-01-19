from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import ConfigDict


class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str = "HS256"

    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 2880

    STRIPE_SECRET_KEY: str
    STRIPE_WEBHOOK_SECRET: str


    class Config:
        env_file = ".env"
        extra = "forbid"


settings = Settings()
