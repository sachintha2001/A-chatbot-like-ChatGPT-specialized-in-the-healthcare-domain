import os
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from app.config import settings

# Enforce secure directory boundaries for SQLite or vector artifacts when running locally
if "sqlite" in settings.DATABASE_URL:
    db_file_path = settings.DATABASE_URL.replace("sqlite+aiosqlite:///", "")
    db_dir = os.path.dirname(db_file_path)
    if db_dir:
        os.makedirs(db_dir, exist_ok=True)

audit_dir = os.path.dirname(settings.AUDIT_LOG_STORAGE_PATH)
if audit_dir:
    os.makedirs(audit_dir, exist_ok=True)

vector_dir = settings.VECTOR_STORE_PATH
if vector_dir:
    os.makedirs(vector_dir, exist_ok=True)

# Isolation level for concurrent audit log transactions and RLHF feedback updates
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,
    future=True,
    pool_pre_ping=True
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False
)

Base = declarative_base()


def utc_now():
    """Returns naive UTC datetime for strict asyncpg PostgreSQL compatibility."""
    from datetime import datetime, timezone
    return datetime.now(timezone.utc).replace(tzinfo=None)


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
