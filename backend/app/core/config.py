from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List
import os
from pathlib import Path
from pydantic import field_validator

# Get the project root directory (2 levels up from this file)
BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
ENV_FILE = BASE_DIR / ".env"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(ENV_FILE),
        case_sensitive=True,
        env_parse_none_str='none',
        extra='ignore'  # Ignore extra fields from .env
    )

    # API Keys
    TOGETHER_API_KEY: str
    WHISPERAPI: str

    # Database
    DATABASE_URL: str

    # JWT Configuration
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Encryption
    ENCRYPTION_KEY: str

    # File Storage
    CHROMA_PATH: str = "./chroma_db"
    UPLOAD_DIR: str = "./uploads"
    MAX_FILE_SIZE_MB: int = 50

    # CORS (comma-separated string)
    CORS_ORIGINS: str = "http://localhost:5173,http://localhost:5174"

    @property
    def cors_origins_list(self) -> List[str]:
        """Parse CORS_ORIGINS string into a list"""
        return [origin.strip() for origin in self.CORS_ORIGINS.split(',')]

    # Environment
    ENVIRONMENT: str = "development"

    # Email Configuration
    EMAIL_SENDER: str
    EMAIL_PASSWORD: str

    # Paystack Configuration
    PAYSTACK_SECRET_KEY: str
    PAYSTACK_PUBLIC_KEY: str
    PAYSTACK_CALLBACK_URL: str

    # Cloudinary Configuration
    CLOUDINARY_CLOUD_NAME: str
    CLOUDINARY_API_KEY: str
    CLOUDINARY_API_SECRET: str

    # AWS Bedrock (Optional - multiple keys available)
    BEDROCK_API_KEY_1: str | None = None
    BEDROCK_ACCESS_KEY_1: str | None = None
    BEDROCK_SECRET_KEY_1: str | None = None


settings = Settings()
