"""Environment-driven application configuration."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime configuration loaded from the repository root .env file."""

    model_config = SettingsConfigDict(env_file="../.env", extra="ignore")

    backend_host: str = "127.0.0.1"
    backend_port: int = 8010
    frontend_port: int = 5173
    cors_origin: str = "http://localhost:5173"
    demo_user_id: str = "agent-1"


settings = Settings()
