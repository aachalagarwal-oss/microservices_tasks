from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite+aiosqlite:///./user_service.db"
    AUTH_SERVICE_URL: str = "http://localhost:8000"

    class Config:
        env_file = ".env"

settings = Settings()
