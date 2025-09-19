import os
from functools import lru_cache
from pydantic import BaseModel, Field
from dotenv import load_dotenv

# Load .env variables if present
load_dotenv()


class Settings(BaseModel):
    """Application settings loaded from environment variables."""
    app_name: str = Field(default=os.getenv("APP_NAME", "Kavia AI CRM Backend"))
    app_env: str = Field(default=os.getenv("APP_ENV", "development"))

    database_url: str = Field(default=os.getenv("DATABASE_URL", "sqlite:///./crm_dev.db"))
    db_pool_size: int = Field(default=int(os.getenv("DB_POOL_SIZE", "5")))
    db_max_overflow: int = Field(default=int(os.getenv("DB_MAX_OVERFLOW", "10")))
    db_pool_timeout: int = Field(default=int(os.getenv("DB_POOL_TIMEOUT", "30")))


# PUBLIC_INTERFACE
@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return a cached Settings instance constructed from environment variables."""
    return Settings()
