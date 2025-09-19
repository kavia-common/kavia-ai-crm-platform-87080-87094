# Expose routers for import in main app
from .accounts import router as accounts_router  # noqa: F401
from .contacts import router as contacts_router  # noqa: F401
from .deals import router as deals_router  # noqa: F401
from .activities import router as activities_router  # noqa: F401
from .pipeline import router as pipeline_router  # noqa: F401
from .ai import router as ai_router  # noqa: F401
