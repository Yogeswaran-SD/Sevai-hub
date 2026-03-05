from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "Sevai Hub API"
    VERSION: str = "1.0.0"
    DATABASE_URL: str = "postgresql://postgres:password@localhost:5432/sevaihub"
    SECRET_KEY: str = "sevai-hub-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 1 day

    class Config:
        env_file = ".env"

settings = Settings()
