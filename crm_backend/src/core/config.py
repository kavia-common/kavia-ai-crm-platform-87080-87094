import os
from functools import lru_cache
from typing import List
from pydantic import BaseModel, Field
from dotenv import load_dotenv

# Load .env if present (do not write .env; orchestrator handles it)
load_dotenv()


class Settings(BaseModel):
    """
    Centralized application settings loaded from environment variables.
    """
    ENV: str = Field(default=os.getenv("ENV", "development"), description="Environment name")
    DEBUG: bool = Field(default=os.getenv("DEBUG", "false").lower() == "true", description="Debug mode")

    # Database (use env variables provided by db container)
    DB_URL: str = Field(default=os.getenv("CRM_DB_URL", "sqlite:///./crm.db"), description="Database URL (SQLAlchemy style)")
    DB_ECHO: bool = Field(default=os.getenv("DB_ECHO", "false").lower() == "true", description="SQLAlchemy echo")

    # CORS
    CORS_ALLOW_ORIGINS: List[str] = Field(
        default_factory=lambda: os.getenv("CORS_ALLOW_ORIGINS", "*").split(","),
        description="CORS allowed origins (comma-separated)"
    )

    # AI toggles
    AI_LEAD_SCORING_ENABLED: bool = Field(default=os.getenv("AI_LEAD_SCORING_ENABLED", "true").lower() == "true")
    AI_FORECASTING_ENABLED: bool = Field(default=os.getenv("AI_FORECASTING_ENABLED", "true").lower() == "true")
    AI_PROBABILITY_ENABLED: bool = Field(default=os.getenv("AI_PROBABILITY_ENABLED", "true").lower() == "true")


# PUBLIC_INTERFACE
@lru_cache()
def get_settings() -> Settings:
    """Return cached application settings."""
    return Settings()
