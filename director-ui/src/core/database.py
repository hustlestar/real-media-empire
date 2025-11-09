"""Database management with async SQLAlchemy support."""

import logging
from datetime import datetime
from typing import Optional, Dict, Any

from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine, AsyncSession, async_sessionmaker
from sqlalchemy import text

from .migration_manager import MigrationManager

logger = logging.getLogger(__name__)


class SQLAlchemyPoolWrapper:
    """Wrapper to provide asyncpg-like pool interface for backward compatibility."""

    def __init__(self, session_factory: async_sessionmaker):
        self._session_factory = session_factory

    def acquire(self):
        """Return a context manager that provides a connection-like interface."""
        return SQLAlchemyConnectionWrapper(self._session_factory())


class SQLAlchemyConnectionWrapper:
    """Wrapper to provide asyncpg-like connection interface using AsyncSession."""

    def __init__(self, session: AsyncSession):
        self._session = session

    async def __aenter__(self):
        await self._session.__aenter__()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            await self._session.rollback()
        else:
            await self._session.commit()
        await self._session.close()

    def transaction(self):
        """Begin a transaction (asyncpg compatibility)."""
        return self._session.begin()

    async def fetchrow(self, query: str, *args):
        """Execute query and fetch one row (asyncpg compatibility)."""
        # Convert positional args ($1, $2) to named params
        named_query, params = self._convert_positional_to_named(query, args)
        result = await self._session.execute(text(named_query), params)
        return result.mappings().first()

    async def fetch(self, query: str, *args):
        """Execute query and fetch all rows (asyncpg compatibility)."""
        named_query, params = self._convert_positional_to_named(query, args)
        result = await self._session.execute(text(named_query), params)
        return result.mappings().all()

    async def fetchval(self, query: str, *args):
        """Execute query and fetch single value (asyncpg compatibility)."""
        named_query, params = self._convert_positional_to_named(query, args)
        result = await self._session.execute(text(named_query), params)
        return result.scalar()

    async def execute(self, query: str, *args):
        """Execute query (asyncpg compatibility)."""
        named_query, params = self._convert_positional_to_named(query, args)
        result = await self._session.execute(text(named_query), params)
        return f"UPDATE {result.rowcount}"

    def _convert_positional_to_named(self, query: str, args: tuple) -> tuple:
        """Convert $1, $2 positional parameters to :p1, :p2 named parameters."""
        import re
        named_query = query
        params = {}
        for i, arg in enumerate(args, 1):
            named_query = re.sub(rf'\${i}(?!\d)', f':p{i}', named_query)
            params[f'p{i}'] = arg
        return named_query, params


class DatabaseManager:
    """Database manager with automatic migration support using async SQLAlchemy."""

    def __init__(self, database_url: str, auto_migrate: bool = True):
        """Initialize the database manager.

        Args:
            database_url: PostgreSQL database connection URL
            auto_migrate: Whether to automatically apply pending migrations on setup
        """
        self.database_url = database_url
        self.auto_migrate = auto_migrate
        self._engine: Optional[AsyncEngine] = None
        self._session_factory: Optional[async_sessionmaker] = None
        self._migration_manager = MigrationManager(database_url)

    @classmethod
    def from_config(cls, config):
        """Create DatabaseManager from BotConfig.

        Args:
            config: BotConfig instance

        Returns:
            DatabaseManager instance
        """
        return cls(database_url=config.database_url, auto_migrate=config.auto_migrate)

    async def setup(self) -> None:
        """Initialize database connection and ensure schema is up to date."""
        try:
            # Run migrations first if auto_migrate is enabled
            if self.auto_migrate:
                logger.info("Checking for pending database migrations...")
                migration_success = await self._migration_manager.ensure_database_ready(auto_migrate=True)
                if not migration_success:
                    raise RuntimeError("Database migration failed")

            # Convert database URL to async format
            async_url = self._convert_to_async_url(self.database_url)

            # Create async engine
            connect_args = {}
            if "sqlite" in async_url:
                connect_args = {"check_same_thread": False}

            self._engine = create_async_engine(
                async_url,
                pool_size=20,
                max_overflow=100,
                echo=False,
                connect_args=connect_args,
            )

            # Create session factory
            self._session_factory = async_sessionmaker(
                bind=self._engine,
                class_=AsyncSession,
                expire_on_commit=False,
                autocommit=False,
                autoflush=False,
            )

            logger.info("Database setup completed successfully with async SQLAlchemy")
        except Exception as e:
            logger.error(f"Database setup failed: {e}")
            raise

    def _convert_to_async_url(self, database_url: str) -> str:
        """Convert database URL to async driver format."""
        # Handle SQLite
        if database_url.startswith("sqlite:///"):
            return database_url.replace("sqlite:///", "sqlite+aiosqlite:///")

        # Handle PostgreSQL
        if database_url.startswith("postgresql://") or database_url.startswith("postgres://"):
            return database_url.replace("postgresql://", "postgresql+asyncpg://", 1).replace("postgres://", "postgresql+asyncpg://", 1)

        # Already has async driver
        if "postgresql+asyncpg://" in database_url or "sqlite+aiosqlite://" in database_url:
            return database_url

        # Strip sync drivers and replace with async
        if "postgresql+psycopg2://" in database_url or "postgresql+psycopg://" in database_url:
            import re
            return re.sub(r'postgresql\+\w+://', 'postgresql+asyncpg://', database_url)

        return database_url

    async def close(self) -> None:
        """Close database connection pool."""
        if self._engine:
            await self._engine.dispose()
            logger.info("Database connection closed")

    def session(self) -> AsyncSession:
        """Get a new async database session.

        Usage:
            async with db_manager.session() as session:
                # Use session
        """
        if not self._session_factory:
            raise RuntimeError("Database not initialized. Call setup() first.")
        return self._session_factory()

    @property
    def _pool(self):
        """
        Backward compatibility property that mimics asyncpg pool interface.

        DEPRECATED: Services should migrate to using db.session() instead.
        This property provides a compatibility layer for legacy code.
        """
        if not self._session_factory:
            raise RuntimeError("Database not initialized. Call setup() first.")
        return SQLAlchemyPoolWrapper(self._session_factory)

    @property
    def migration_manager(self) -> MigrationManager:
        """Get the migration manager instance."""
        return self._migration_manager

    def create_migration(self, message: str, autogenerate: bool = True) -> str:
        """Create a new migration.

        Args:
            message: Migration description
            autogenerate: Whether to auto-generate migration from model changes

        Returns:
            Generated revision ID
        """
        return self._migration_manager.create_migration(message, autogenerate)

    def apply_migrations(self, target_revision: str = "head") -> bool:
        """Apply migrations to the database.

        Args:
            target_revision: Target revision to migrate to (default: "head")

        Returns:
            True if migrations were applied successfully, False otherwise
        """
        return self._migration_manager.apply_migrations(target_revision)

    def get_migration_status(self) -> Dict[str, Any]:
        """Get current migration status.

        Returns:
            Dictionary with migration status information
        """
        current = self._migration_manager.get_current_revision()
        head = self._migration_manager.get_head_revision()
        has_pending = self._migration_manager.has_pending_migrations()

        return {
            "current_revision": current,
            "head_revision": head,
            "has_pending_migrations": has_pending,
            "migration_history": self._migration_manager.get_migration_history(),
        }

    async def ensure_user(self, user_id: int, username: Optional[str] = None, language: str = "en") -> Dict[str, Any]:
        """Ensure user exists in database, create if not exists."""
        async with self.session() as session:
            # Try to get existing user
            result = await session.execute(
                text("SELECT * FROM users WHERE user_id = :user_id"),
                {"user_id": user_id}
            )
            user = result.mappings().first()

            if user:
                user_dict = dict(user)
                if username and user_dict["username"] != username:
                    await session.execute(
                        text("UPDATE users SET username = :username, updated_at = :updated_at WHERE user_id = :user_id"),
                        {"username": username, "updated_at": datetime.utcnow(), "user_id": user_id}
                    )
                    await session.commit()
                    logger.debug(f"Updated username for user {user_id}")

                return user_dict
            else:
                now = datetime.utcnow()
                await session.execute(
                    text("""
                        INSERT INTO users (user_id, username, language, created_at, updated_at)
                        VALUES (:user_id, :username, :language, :created_at, :updated_at)
                    """),
                    {
                        "user_id": user_id,
                        "username": username,
                        "language": language,
                        "created_at": now,
                        "updated_at": now
                    }
                )
                await session.commit()

                result = await session.execute(
                    text("SELECT * FROM users WHERE user_id = :user_id"),
                    {"user_id": user_id}
                )
                user = result.mappings().first()

                logger.info(f"Created new user: {user_id} (@{username})")
                return dict(user)

    async def get_user(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get user by ID."""
        async with self.session() as session:
            result = await session.execute(
                text("SELECT * FROM users WHERE user_id = :user_id"),
                {"user_id": user_id}
            )
            user = result.mappings().first()
            return dict(user) if user else None

    async def update_user_language(self, user_id: int, language: str) -> bool:
        """Update user's language preference."""
        async with self.session() as session:
            result = await session.execute(
                text("UPDATE users SET language = :language, updated_at = :updated_at WHERE user_id = :user_id"),
                {"language": language, "updated_at": datetime.utcnow(), "user_id": user_id}
            )
            await session.commit()

            success = result.rowcount == 1
            if success:
                logger.info(f"Updated language for user {user_id} to {language}")

            return success

    async def get_user_language(self, user_id: int) -> str:
        """Get user's language preference."""
        async with self.session() as session:
            result = await session.execute(
                text("SELECT language FROM users WHERE user_id = :user_id"),
                {"user_id": user_id}
            )
            language = result.scalar_one_or_none()
            return language or "en"

    async def get_user_count(self) -> int:
        """Get total number of users."""
        async with self.session() as session:
            result = await session.execute(text("SELECT COUNT(*) FROM users"))
            count = result.scalar()
            return count or 0

    async def get_users_by_language(self, language: str) -> int:
        """Get number of users by language."""
        async with self.session() as session:
            result = await session.execute(
                text("SELECT COUNT(*) FROM users WHERE language = :language"),
                {"language": language}
            )
            count = result.scalar()
            return count or 0

    async def get_recent_users(self, limit: int = 10) -> list:
        """Get recently registered users."""
        async with self.session() as session:
            result = await session.execute(
                text("SELECT * FROM users ORDER BY created_at DESC LIMIT :limit"),
                {"limit": limit}
            )
            users = result.mappings().all()
            return [dict(user) for user in users]

    async def delete_user(self, user_id: int) -> bool:
        """Delete user from database."""
        async with self.session() as session:
            result = await session.execute(
                text("DELETE FROM users WHERE user_id = :user_id"),
                {"user_id": user_id}
            )
            await session.commit()

            success = result.rowcount == 1
            if success:
                logger.info(f"Deleted user {user_id}")

            return success

    async def get_stats(self) -> Dict[str, Any]:
        """Get basic database statistics."""
        async with self.session() as session:
            result = await session.execute(text("SELECT COUNT(*) FROM users"))
            total_users = result.scalar()

            result = await session.execute(text("SELECT language, COUNT(*) as count FROM users GROUP BY language"))
            language_stats = result.mappings().all()

            result = await session.execute(text("SELECT COUNT(*) FROM users WHERE created_at > NOW() - INTERVAL '24 hours'"))
            recent_users = result.scalar()

            return {
                "total_users": total_users or 0,
                "recent_users_24h": recent_users or 0,
                "language_distribution": {row["language"]: row["count"] for row in language_stats},
            }
