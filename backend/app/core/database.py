"""
Database connection and session lifecycle management.
"""
import os
from pathlib import Path
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base
from app.core.config import settings

if settings.USE_SQLITE:
    if "sqlite+aiosqlite:///" in settings.DATABASE_URL:
        raw_path = settings.DATABASE_URL.replace("sqlite+aiosqlite:///", "")
        p = Path(raw_path)
        if not p.is_absolute():
            # Check workspace root first, then backend dir
            workspace_root_db = Path(__file__).resolve().parent.parent.parent.parent / p.name
            backend_dir_db = Path(__file__).resolve().parent.parent.parent / p.name
            if workspace_root_db.exists():
                db_url = f"sqlite+aiosqlite:///{workspace_root_db.as_posix()}"
            elif backend_dir_db.exists():
                db_url = f"sqlite+aiosqlite:///{backend_dir_db.as_posix()}"
            else:
                db_url = f"sqlite+aiosqlite:///{workspace_root_db.as_posix()}"
        else:
            db_url = settings.DATABASE_URL
    else:
        db_url = settings.DATABASE_URL
else:
    db_url = settings.POSTGRES_URL

engine = create_async_engine(
    db_url,
    echo=False,
    future=True,
    connect_args={"check_same_thread": False} if "sqlite" in db_url else {}
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

Base = declarative_base()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency for obtaining async DB session per request."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db() -> None:
    """Create tables on startup if not existing."""
    import app.models  # Ensure all SQLAlchemy models are registered on Base.metadata
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
