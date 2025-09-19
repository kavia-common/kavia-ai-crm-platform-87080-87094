from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.core.config import get_settings
from src.core.database import engine, Base

# Initialize FastAPI with metadata and tags
app = FastAPI(
    title="Kavia AI CRM Backend",
    description="Backend APIs for accounts, contacts, deals, activities, and pipeline. Prepared for AI endpoints.",
    version="0.1.0",
    openapi_tags=[
        {"name": "health", "description": "Health and status endpoints"},
        {"name": "accounts", "description": "Manage accounts"},
        {"name": "contacts", "description": "Manage contacts"},
        {"name": "deals", "description": "Manage deals and pipeline"},
        {"name": "activities", "description": "Activity logs"},
        {"name": "pipeline", "description": "Pipeline stages"},
    ],
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Create tables automatically in development mode
settings = get_settings()
if settings.app_env == "development":
    from src.models import crm_models  # noqa: F401 ensure models are imported
    Base.metadata.create_all(bind=engine)


# PUBLIC_INTERFACE
@app.get("/", tags=["health"], summary="Health Check", description="Simple health check endpoint.")
def health_check():
    """Returns a simple health status message for availability checks."""
    return {"message": "Healthy"}
