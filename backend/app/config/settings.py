import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Load the appropriate .env file based on environment
env = os.getenv("APP_ENV", "dev")
load_dotenv(f".env.{env}")

class Settings(BaseSettings):
    """Application settings."""
    APP_NAME: str = "EasyTalk"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = env == "dev"
    
    # API Configuration
    API_PREFIX: str = "/api/v1"
    
    # JWT Configuration
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "your-secret-key-for-development-only")
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 1 day
    
    # Database Configuration
    MONGO_URI: str = os.getenv("MONGO_URI", "mongodb://localhost:27017")
    MONGO_DB_NAME: str = os.getenv("MONGO_DB_NAME", "easytalk_db")
    
    # Firebase Configuration (optional)
    FIREBASE_CREDENTIALS_PATH: str = os.getenv("FIREBASE_CREDENTIALS_PATH", "")
    
    class Config:
        case_sensitive = True


settings = Settings()
