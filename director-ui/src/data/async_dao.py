"""Unified async database access layer using SQLAlchemy AsyncSession."""
import os
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import Session

# Lazy imports to avoid circular dependencies
_async_engine = None
_AsyncSessionLocal = None


def get_async_engine():
    """Get or create async database engine."""
    global _async_engine
    if _async_engine is None:
        from data.models import Base
        DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./mediaempire.db")

        # Convert DATABASE_URL to async driver format
        async_url = DATABASE_URL

        # Handle SQLite
        if DATABASE_URL.startswith("sqlite:///"):
            async_url = DATABASE_URL.replace("sqlite:///", "sqlite+aiosqlite:///")

        # Handle PostgreSQL - use asyncpg driver
        elif DATABASE_URL.startswith("postgresql://") or DATABASE_URL.startswith("postgres://"):
            # Replace postgresql:// with postgresql+asyncpg://
            async_url = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)
            async_url = async_url.replace("postgres://", "postgresql+asyncpg://", 1)

        # Already has async driver specified
        elif "postgresql+asyncpg://" in DATABASE_URL or "sqlite+aiosqlite://" in DATABASE_URL:
            async_url = DATABASE_URL

        # Strip sync drivers and replace with async
        elif "postgresql+psycopg2://" in DATABASE_URL:
            async_url = DATABASE_URL.replace("postgresql+psycopg2://", "postgresql+asyncpg://")

        # Create async engine
        connect_args = {}
        if "sqlite" in async_url:
            connect_args = {"check_same_thread": False}

        _async_engine = create_async_engine(
            async_url,
            pool_size=20,
            max_overflow=100,
            echo=False,  # Set to True for SQL debug logging
            connect_args=connect_args,
        )

    return _async_engine


def get_async_session_local():
    """Get or create async session factory."""
    global _AsyncSessionLocal
    if _AsyncSessionLocal is None:
        _AsyncSessionLocal = async_sessionmaker(
            bind=get_async_engine(),
            class_=AsyncSession,
            expire_on_commit=False,
            autocommit=False,
            autoflush=False,
        )
    return _AsyncSessionLocal


async def get_async_db() -> AsyncGenerator[AsyncSession, None]:
    """Get async database session (FastAPI dependency)."""
    AsyncSessionLocal = get_async_session_local()
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def create_tables():
    """Create all tables (for testing/development)."""
    from data.models import Base
    engine = get_async_engine()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_or_create(session: AsyncSession, model, **kwargs):
    """Get or create a model instance (async version)."""
    from sqlalchemy import select

    stmt = select(model).filter_by(**kwargs)
    result = await session.execute(stmt)
    instance = result.scalar_one_or_none()

    if instance:
        return instance
    else:
        instance = model(**kwargs)
        session.add(instance)
        await session.flush()
        await session.refresh(instance)
        return instance
