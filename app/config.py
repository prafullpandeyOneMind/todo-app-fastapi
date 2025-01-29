from pydantic_settings import BaseSettings
from jose import jwt



class Settings(BaseSettings):
    DATABASE_URL: str
    JWT_SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: str
    class Config:
        env_file = ".env"

settings = Settings()