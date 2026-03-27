# app/core/config.py
# Manages application-wide settings and configurations.

import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv

# Load environment variables from a .env file
load_dotenv()

class Settings(BaseSettings):
    """
    Pydantic model for loading and validating environment variables.
    """
    # Database configuration
    DATABASE_URL: str

    # JWT Authentication settings
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # Hosted Redis (e.g. Redis Cloud). Full URL with password, e.g.
    # redis://default:YOUR_PASSWORD@HOST:PORT/0
    REDIS_URL: str | None = None

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

# Create a single, reusable instance of the settings
settings = Settings()
