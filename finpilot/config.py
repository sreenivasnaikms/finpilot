"""Application configuration and settings."""

import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Load local .env if present
load_dotenv()


class Settings(BaseSettings):
    APP_NAME: str = "FinPilot"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # Mesh API Configuration (Mandatory Hackathon Sponsor Gateway)
    # Base URL must point strictly to Mesh API gateway
    MESH_API_KEY: str = os.getenv("MESH_API_KEY", "")
    MESH_BASE_URL: str = os.getenv("MESH_BASE_URL", "https://api.meshapi.ai/v1")
    
    # Model defaults to gpt-4o-mini on Mesh API (fast, robust for structured JSON and reasoning)
    DEFAULT_MODEL: str = os.getenv("MESH_MODEL", "openai/gpt-4o-mini")
    REASONING_MODEL: str = os.getenv("MESH_REASONING_MODEL", "openai/gpt-4o")
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./finpilot.db")
    
    # Proactive Digest Schedule
    DIGEST_INTERVAL_HOURS: int = int(os.getenv("DIGEST_INTERVAL_HOURS", "24"))

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
