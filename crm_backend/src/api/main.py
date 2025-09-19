from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.core.config import get_settings
from src.core.database import engine, Base

# Routers
from src.api.routers.accounts import router as accounts_router  # noqa: E402
from src.api.routers.contacts import router as contacts_router  # noqa: E402
from src.api.routers.deals import router as deals_router  # noqa: E402
from src.api.routers.activities import router as activities_router  # noqa: E402
from src.api.routers.pipeline import router as pipeline_router  # noqa: E402
from src.api.routers.ai import router as ai_router  # noqa: E402

# Initialize FastAPI with metadata and tags
app = FastAPI(
    title="Kavia AI CRM Backend",
    description="Backend APIs for accounts, contacts, deals, activities, pipeline stages, and AI analytics.",
    version="0.2.0",
    openapi_tags=[
        {"name": "health", "description": "Health and status endpoints"},
        {"name": "accounts", "description": "Manage accounts"},
        {"name": "contacts", "description": "Manage contacts"},
        {"name": "deals", "description": "Manage deals and pipeline"},
        {"name": "activities", "description": "Activity logs"},
        {"name": "pipeline", "description": "Pipeline stages"},
        {"name": "ai", "description": "AI analytics and insights"},
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


# Include routers
app.include_router(accounts_router)
app.include_router(contacts_router)
app.include_router(deals_router)
app.include_router(activities_router)
app.include_router(pipeline_router)
app.include_router(ai_router)
