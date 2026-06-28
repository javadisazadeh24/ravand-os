"""
RAVAND OS – Database Layer
SQLAlchemy engine + session factory.
Currently configured for SQLite; switching to PostgreSQL requires only
changing DATABASE_URL in .env – no code changes needed.
"""

from collections.abc import Generator
from typing import Any

from sqlalchemy import create_engine, event, text
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.core.config import get_settings
from app.core.logging import get_logger

logger = get_logger(__name__)
settings = get_settings()


# ── Engine ─────────────────────────────────────────────────────────────────────

def _build_engine():
    """
    Build the SQLAlchemy engine.
    Applies SQLite-specific pragmas for WAL mode and foreign key enforcement.
    PostgreSQL connections skip these pragmas automatically.
    """
    connect_args: dict[str, Any] = {}

    if settings.DATABASE_URL.startswith("sqlite"):
        # Allow multi-threaded access (required for FastAPI with SQLite)
        connect_args["check_same_thread"] = False

    engine = create_engine(
        settings.DATABASE_URL,
        echo=settings.DATABASE_ECHO,
        connect_args=connect_args,
        pool_pre_ping=True,     # validate connections before use
    )

    # SQLite-only: enable WAL journal and foreign keys at connection level
    if settings.DATABASE_URL.startswith("sqlite"):
        @event.listens_for(engine, "connect")
        def _set_sqlite_pragmas(dbapi_conn, _connection_record):
            cursor = dbapi_conn.cursor()
            cursor.execute("PRAGMA journal_mode=WAL")
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.execute("PRAGMA synchronous=NORMAL")
            cursor.close()

    logger.info("Database engine created | url=%s", settings.DATABASE_URL)
    return engine


engine = _build_engine()

SessionLocal: sessionmaker[Session] = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
)


# ── Declarative Base ───────────────────────────────────────────────────────────

class Base(DeclarativeBase):
    """
    Base class for all SQLAlchemy ORM models in RAVAND OS.
    Extend this to add shared columns (e.g., created_at) in the future.
    """
    pass


# ── Session Dependency ─────────────────────────────────────────────────────────

def get_db() -> Generator[Session, None, None]:
    """
    FastAPI dependency that yields a database session.
    Commits on success; rolls back on any exception.
    Usage:
        @router.get("/")
        def endpoint(db: Session = Depends(get_db)):
            ...
    """
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


# ── Database Initialisation ────────────────────────────────────────────────────

def init_db() -> None:
    """
    Create all tables defined in ORM models.
    Called once at application startup.
    Safe to call multiple times (CREATE TABLE IF NOT EXISTS semantics).
    """
    # Import all models so their metadata is registered before create_all
    import app.database.models  # noqa: F401

    Base.metadata.create_all(bind=engine)
    logger.info("Database tables initialised.")


def verify_db_connection() -> bool:
    """
    Perform a simple SELECT 1 to confirm the database is reachable.
    Returns True on success, False on failure.
    """
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception as exc:
        logger.error("Database connectivity check failed: %s", exc)
        return False
