from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite+aiosqlite:///./task_service.db"
    AUTH_SERVICE_URL: str = "http://localhost:8001"

    class Config:
        env_file = ".env"

settings = Settings()
