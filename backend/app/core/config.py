from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    """
    Production-safe settings configuration.
    All secrets MUST be provided via environment variables.
    No defaults for sensitive values.
    """
    # Application Info
    APP_NAME: str = "Sevai Hub API"
    VERSION: str = "4.0.0"
    ENVIRONMENT: str = "development"  # development, staging, production
    
    # Database (REQUIRED - no default)
    DATABASE_URL: str  # postgresql://user:password@host:5432/dbname
    
    # JWT / Security (REQUIRED - no default)
    SECRET_KEY: str    # Min 32 characters - used to sign JWT tokens
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 1 day
    
    # Admin credentials (REQUIRED - from environment only)
    ADMIN_SECRET_KEY: str              # High-security admin secret
    ADMIN_MOBILE: str                  # Admin mobile number
    ADMIN_AADHAAR: str                 # Admin Aadhaar ID
    ADMIN_PASSWORD_HASH: str           # HASHED password using bcrypt (NOT plaintext!)
    
    # CORS Configuration (REQUIRED - use env for production)
    CORS_ORIGINS: Optional[str] = "http://localhost:3000,http://localhost:5173"  # Comma-separated
    
    # Redis Cache
    REDIS_URL: str = "redis://localhost:6379"
    
    # MinIO Object Storage
    MINIO_URL: str = "http://localhost:9000"
    MINIO_ACCESS_KEY: str = "minioadmin"
    MINIO_SECRET_KEY: str = "minioadmin123"
    MINIO_BUCKET: str = "sevaihub"
    
    # Email/SMTP Settings
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    EMAILS_FROM_EMAIL: str = "noreply@sevaihub.com"
    EMAILS_FROM_NAME: str = "Sevai Hub"
    
    # SMS/Twilio Settings
    TWILIO_ACCOUNT_SID: Optional[str] = None
    TWILIO_AUTH_TOKEN: Optional[str] = None
    TWILIO_PHONE_NUMBER: Optional[str] = None
    
    # Optional Features
    DEBUG: bool = False
    TESTING: bool = False
    ALLOW_ORIGINS_ALL: bool = False  # DANGER: Only for testing

    class Config:
        env_file = ".env"
        extra = "forbid"  # Reject unknown environment variables
        case_sensitive = True

    @property
    def cors_origins_list(self) -> list[str]:
        """Parse CORS origins from comma-separated string."""
        if not self.CORS_ORIGINS:
            return ["http://localhost:3000"]
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]

    def validate_production_settings(self) -> None:
        """Validate critical settings for production deployment."""
        if self.ENVIRONMENT == "production":
            if not self.SECRET_KEY or len(self.SECRET_KEY) < 32:
                raise ValueError("SECRET_KEY must be 32+ characters for production")
            if not self.DATABASE_URL:
                raise ValueError("DATABASE_URL is required for production")
            if not self.ADMIN_PASSWORD_HASH or "$2b$" not in self.ADMIN_PASSWORD_HASH:
                raise ValueError("ADMIN_PASSWORD_HASH must be bcrypt hash for production (starts with $2b$)")
            if self.DEBUG:
                raise ValueError("DEBUG must be False in production")
            if self.ALLOW_ORIGINS_ALL:
                raise ValueError("ALLOW_ORIGINS_ALL must be False in production (CORS security risk)")

settings = Settings()

# Validate production settings on startup
if settings.ENVIRONMENT == "production":
    settings.validate_production_settings()

