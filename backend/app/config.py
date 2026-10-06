"""
Application configuration.

This module contains configuration settings for the backend application.
"""

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """
    Application settings.
    
    Environment variables:
    - APP_NAME: Application name (default: Ticket Processing API)
    - APP_VERSION: Application version (default: 1.0.0)
    - DEBUG: Debug mode (default: False)
    """
    app_name: str = "Ticket Processing API"
    app_version: str = "1.0.0"
    debug: bool = False

    class Config:
        env_file = ".env"


# Create settings instance
settings = Settings()
