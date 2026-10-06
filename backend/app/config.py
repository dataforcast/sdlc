"""
Application configuration.

This module contains configuration settings for the backend application.
"""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Application settings.
    
    Environment variables (loaded from .env file at project root):
    - APP_NAME: Application name (default: Ticket Processing API)
    - APP_VERSION: Application version (default: 1.0.0)
    - DEBUG: Debug mode (default: False)
    - BACKEND_PORT: Backend server port
    - FRONTEND_PORT: Frontend server port
    """
    app_name: str = "Ticket Processing API"
    app_version: str = "1.0.0"
    debug: bool = False
    backend_port: int
    frontend_port: int

    class Config:
        env_file = "../.env"
        extra = "ignore"


# Create settings instance
settings = Settings()
