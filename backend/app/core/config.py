"""
Application Configuration
"""
from pydantic_settings import BaseSettings
from typing import List
import os
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    # Application
    APP_NAME: str = "Demo Bank API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    ENVIRONMENT: str = "development"

    # Database
    DATABASE_URL: str = "postgresql://localhost:5432/demo_bank"
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    DB_NAME: str = "demo_bank"
    DB_USER: str = "postgres"
    DB_PASSWORD: str = ""

    # Security
    SECRET_KEY: str = "your-secret-key-change-this-in-production-min-32-chars"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 hours

    # Paystack
    PAYSTACK_SECRET_KEY: str = "sk_test_"
    PAYSTACK_PUBLIC_KEY: str = "pk_test_"
    PAYSTACK_BASE_URL: str = "https://api.paystack.co"

    # CORS
    ALLOWED_ORIGINS: str = "http://localhost:3000,http://localhost:8081"

    # API
    API_V1_PREFIX: str = "/api"
    PORT: int = 8000

    # EchoBank
    ECHOBANK_API_URL: str = "http://localhost:8001"

    @property
    def allowed_origins_list(self) -> List[str]:
        """Parse ALLOWED_ORIGINS into a list"""
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",")]

    @property
    def database_url_sync(self) -> str:
        """Get synchronous database URL"""
        if self.DB_PASSWORD:
            return f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        return f"postgresql://{self.DB_USER}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
