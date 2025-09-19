from contextlib import contextmanager
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase, Session
from src.core.config import get_settings


class Base(DeclarativeBase):
    """Declarative base for ORM models."""
    pass


def _make_engine():
    settings = get_settings()
    # SQLite needs check_same_thread=False for single-file development DB.
    connect_args = {}
    if settings.database_url.startswith("sqlite"):
        connect_args = {"check_same_thread": False}
    engine = create_engine(
        settings.database_url,
        pool_size=settings.db_pool_size if not settings.database_url.startswith("sqlite") else None,
        max_overflow=settings.db_max_overflow if not settings.database_url.startswith("sqlite") else None,
        pool_timeout=settings.db_pool_timeout if not settings.database_url.startswith("sqlite") else None,
        echo=(settings.app_env == "development"),
        connect_args=connect_args,
        future=True,
    )
    return engine


engine = _make_engine()
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False, class_=Session, future=True)


# PUBLIC_INTERFACE
def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency that yields a database session and ensures proper cleanup."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@contextmanager
def db_session() -> Generator[Session, None, None]:
    """Context manager for DB session in internal modules and scripts."""
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
