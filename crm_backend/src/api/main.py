from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi

from src.core.config import get_settings
from src.db.session import init_db
from src.routes import contacts, accounts, deals, activities, pipelines, ai

# Initialize settings (environment driven)
settings = get_settings()

# PUBLIC_INTERFACE
def create_app() -> FastAPI:
    """
    Create and configure the FastAPI application with routers, middleware, and OpenAPI metadata.
    """
    app = FastAPI(
        title="Kavia AI CRM Backend",
        description=(
            "RESTful API for Kavia AI CRM with contact, account, deal, activity logging, "
            "pipeline management, and AI endpoints for lead scoring, forecasting, and probability analysis. "
            "All settings are environment-driven."
        ),
        version="0.1.0",
        contact={"name": "Kavia AI", "url": "https://kavia.ai"},
        license_info={"name": "Proprietary"},
        openapi_tags=[
            {"name": "health", "description": "Health and meta endpoints"},
            {"name": "contacts", "description": "Manage contacts"},
            {"name": "accounts", "description": "Manage accounts"},
            {"name": "deals", "description": "Manage deals and pipeline stages"},
            {"name": "activities", "description": "Manage activity logs (calls, emails, meetings)"},
            {"name": "pipelines", "description": "Manage pipelines and stages"},
            {"name": "ai", "description": "AI analytics: lead scoring, forecasting, probability"},
        ],
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ALLOW_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include routers
    app.include_router(contacts.router, prefix="/api/contacts", tags=["contacts"])
    app.include_router(accounts.router, prefix="/api/accounts", tags=["accounts"])
    app.include_router(deals.router, prefix="/api/deals", tags=["deals"])
    app.include_router(activities.router, prefix="/api/activities", tags=["activities"])
    app.include_router(pipelines.router, prefix="/api/pipelines", tags=["pipelines"])
    app.include_router(ai.router, prefix="/api/ai", tags=["ai"])

    @app.get("/", tags=["health"], summary="Health Check")
    # PUBLIC_INTERFACE
    def health_check():
        """
        Health check endpoint to verify the service is running.

        Returns:
            dict: A status object.
        """
        return {"message": "Healthy", "service": "kavia-ai-crm-backend", "version": app.version}

    # Initialize DB on startup
    @app.on_event("startup")
    async def on_startup():
        init_db()

    return app


app = create_app()


def custom_openapi():
    """
    Override FastAPI generated openapi to include metadata and WebSocket help if needed later.
    """
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi
