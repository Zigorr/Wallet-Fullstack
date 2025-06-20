import re
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Database Configuration
    DATABASE_URL: str

    # Supabase Configuration (optional, for additional features)
    SUPABASE_URL: Optional[str] = None
    SUPABASE_KEY: Optional[str] = None

    # JWT Authentication
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Application Settings
    LOG_LEVEL: str = "INFO"

    # Password Validation
    # Enforces: 8+ chars, 1 uppercase, 1 lowercase, 1 number, 1 special char
    PASSWORD_REGEX: str = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$"
    PASSWORD_MESSAGE: str = "Password must be at least 8 characters long and contain at least one uppercase letter, one lowercase letter, one number, and one special character."

    class Config:
        env_file = ".env"

settings = Settings()
