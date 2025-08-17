# app/core/config.py
# Manages application-wide settings and configurations.

import os
from pydantic_settings import BaseSettings
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

    class Config:
        # This tells Pydantic to read variables from a .env file.
        # It's case-insensitive.
        env_file = ".env"
        env_file_encoding = 'utf-8'
        extra = "ignore"

# Create a single, reusable instance of the settings
settings = Settings()
