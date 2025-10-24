from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
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

    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:5173", "http://localhost:5174"]

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

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
