"""
Pytest configuration and fixtures for DAO tests.

Provides SQLite test database setup and teardown, along with service fixtures.
"""

import pytest
import asyncio
import tempfile
import shutil
from pathlib import Path
from uuid import uuid4
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from core.database import DatabaseManager
from services.content_service import ContentService
from services.processing_service import ProcessingService
from services.bundle_service import BundleService
from services.file_storage import FileStorageService
from processors.ai_processor import AIProcessor


@pytest.fixture(scope="session")
def event_loop():
    """Create an event loop for async tests."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
async def test_db_url(tmp_path_factory):
    """Create a temporary SQLite database URL for testing."""
    # Create a unique temp directory for this test session
    temp_dir = tmp_path_factory.mktemp("test_db")
    db_file = temp_dir / "test.db"

    # Return SQLite URL
    yield f"sqlite:///{db_file}"

    # Cleanup handled by pytest's tmp_path_factory


@pytest.fixture
async def db_manager(test_db_url):
    """Create and initialize a test database manager with schema."""
    # Create database manager without auto-migrate
    db = DatabaseManager(database_url=test_db_url, auto_migrate=False)
    await db.setup()

    # Create schema manually for SQLite testing
    await _create_test_schema(db)

    yield db

    # Cleanup
    await db.close()


@pytest.fixture
async def storage_dir(tmp_path):
    """Create temporary storage directory for file operations."""
    storage_path = tmp_path / "storage"
    storage_path.mkdir()

    # Create subdirectories
    (storage_path / "extracted").mkdir()
    (storage_path / "uploads").mkdir()
    (storage_path / "results").mkdir()

    yield str(storage_path)

    # Cleanup handled by pytest's tmp_path


@pytest.fixture
async def file_storage(storage_dir):
    """Create file storage service for testing."""
    # Create a mock config object for FileStorageService
    class MockConfig:
        def __init__(self, storage_dir):
            self.storage_base_path = storage_dir
            self.extracted_text_path = f"{storage_dir}/extracted"
            self.processing_results_path = f"{storage_dir}/results"
            self.uploads_path = f"{storage_dir}/uploads"
            self.file_retention_days = 90

    return FileStorageService(MockConfig(storage_dir))


@pytest.fixture
async def ai_processor():
    """Create mock AI processor for testing (without real API calls)."""
    return MockAIProcessor()


@pytest.fixture
async def content_service(db_manager, file_storage, ai_processor):
    """Create content service for testing."""
    return ContentService(db_manager, file_storage, ai_processor)


@pytest.fixture
async def processing_service(db_manager, file_storage, ai_processor):
    """Create processing service for testing."""
    return ProcessingService(db_manager, file_storage, ai_processor)


@pytest.fixture
async def bundle_service(db_manager):
    """Create bundle service for testing."""
    return BundleService(db_manager)


@pytest.fixture
async def test_user(db_manager):
    """Create a test user in the database."""
    async with db_manager.session() as session:
        from sqlalchemy import text
        result = await session.execute(
            text("""
                INSERT INTO users (id, email, hashed_password, is_active, created_at, updated_at)
                VALUES (1, 'test@example.com', 'hashed_password', TRUE, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                RETURNING id
            """)
        )
        await session.commit()
        user_id = result.scalar()

    yield user_id

    # Cleanup handled by database teardown


@pytest.fixture
async def test_content(db_manager, test_user):
    """Create test content item in the database."""
    async with db_manager.session() as session:
        from sqlalchemy import text
        import json

        content_id = str(uuid4())
        content_hash = "test_hash_" + str(uuid4())[:8]

        result = await session.execute(
            text("""
                INSERT INTO content_items (
                    id, content_hash, source_type, source_url, file_reference,
                    extracted_text_path, extracted_text_paths, content_metadata,
                    user_id, processing_status, detected_language, created_at, updated_at
                )
                VALUES (
                    :id, :hash, 'pdf_url', 'https://example.com/test.pdf', NULL,
                    '/test/path.txt', :paths, :metadata,
                    :user_id, 'completed', 'en', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
                )
                RETURNING id
            """),
            {
                "id": content_id,
                "hash": content_hash,
                "paths": json.dumps({"en": "/test/path.txt"}),
                "metadata": json.dumps({"title": "Test Content"}),
                "user_id": test_user
            }
        )
        await session.commit()

    yield content_id


async def _create_test_schema(db: DatabaseManager):
    """Create test database schema for SQLite."""
    async with db.session() as session:
        from sqlalchemy import text

        # Create users table
        await session.execute(text("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                email VARCHAR(255) UNIQUE NOT NULL,
                hashed_password VARCHAR(255) NOT NULL,
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """))

        # Create content_items table
        await session.execute(text("""
            CREATE TABLE IF NOT EXISTS content_items (
                id VARCHAR(36) PRIMARY KEY,
                content_hash VARCHAR(64) NOT NULL UNIQUE,
                source_type VARCHAR(50) NOT NULL,
                source_url TEXT,
                file_reference TEXT,
                extracted_text_path TEXT NOT NULL,
                extracted_text_paths TEXT,
                content_metadata TEXT DEFAULT '{}',
                user_id INTEGER NOT NULL,
                processing_status VARCHAR(50) DEFAULT 'pending',
                detected_language VARCHAR(10),
                error_message TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """))

        # Create tags table
        await session.execute(text("""
            CREATE TABLE IF NOT EXISTS tags (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name VARCHAR(100) UNIQUE NOT NULL,
                user_id INTEGER,
                usage_count INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """))

        # Create content_tags junction table
        await session.execute(text("""
            CREATE TABLE IF NOT EXISTS content_tags (
                content_id VARCHAR(36) NOT NULL,
                tag_id INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (content_id, tag_id),
                FOREIGN KEY (content_id) REFERENCES content_items(id) ON DELETE CASCADE,
                FOREIGN KEY (tag_id) REFERENCES tags(id) ON DELETE CASCADE
            )
        """))

        # Create processing_jobs table
        await session.execute(text("""
            CREATE TABLE IF NOT EXISTS processing_jobs (
                id VARCHAR(36) PRIMARY KEY,
                content_id VARCHAR(36),
                bundle_id VARCHAR(36),
                content_ids TEXT,
                processing_type VARCHAR(50) NOT NULL,
                status VARCHAR(50) DEFAULT 'pending',
                result_path TEXT,
                user_prompt TEXT,
                output_language VARCHAR(10) DEFAULT 'en',
                error_message TEXT,
                user_id INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (content_id) REFERENCES content_items(id) ON DELETE CASCADE,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """))

        # Create bundles table
        await session.execute(text("""
            CREATE TABLE IF NOT EXISTS bundles (
                id VARCHAR(36) PRIMARY KEY,
                user_id INTEGER NOT NULL,
                name VARCHAR(255),
                content_ids TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """))

        # Create bundle_attempts table
        await session.execute(text("""
            CREATE TABLE IF NOT EXISTS bundle_attempts (
                id VARCHAR(36) PRIMARY KEY,
                bundle_id VARCHAR(36) NOT NULL,
                attempt_number INTEGER NOT NULL,
                processing_type VARCHAR(50) NOT NULL,
                output_language VARCHAR(10) NOT NULL,
                system_prompt TEXT NOT NULL,
                user_prompt TEXT,
                combined_content_preview TEXT,
                custom_instructions TEXT,
                result_path TEXT,
                job_id VARCHAR(36),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE (bundle_id, attempt_number),
                FOREIGN KEY (bundle_id) REFERENCES bundles(id) ON DELETE CASCADE,
                FOREIGN KEY (job_id) REFERENCES processing_jobs(id) ON DELETE SET NULL
            )
        """))

        # Create indexes
        await session.execute(text("CREATE INDEX IF NOT EXISTS idx_content_items_user_id ON content_items(user_id)"))
        await session.execute(text("CREATE INDEX IF NOT EXISTS idx_content_items_hash ON content_items(content_hash)"))
        await session.execute(text("CREATE INDEX IF NOT EXISTS idx_processing_jobs_user_id ON processing_jobs(user_id)"))
        await session.execute(text("CREATE INDEX IF NOT EXISTS idx_processing_jobs_content_id ON processing_jobs(content_id)"))
        await session.execute(text("CREATE INDEX IF NOT EXISTS idx_processing_jobs_bundle_id ON processing_jobs(bundle_id)"))
        await session.execute(text("CREATE INDEX IF NOT EXISTS idx_bundles_user_id ON bundles(user_id)"))
        await session.execute(text("CREATE INDEX IF NOT EXISTS idx_bundle_attempts_bundle_id ON bundle_attempts(bundle_id)"))

        await session.commit()


class MockAIProcessor:
    """Mock AI processor for testing without real API calls."""

    async def detect_language_and_generate_tags(self, text: str, existing_tags: list, user_id: int) -> dict:
        """Mock language and tag detection."""
        return {
            "language": "en",
            "tags": ["test", "content"]
        }

    async def process_content(
        self,
        content: str,
        processing_type: str,
        source_type: str,
        user_id: int,
        language: str
    ) -> str:
        """Mock content processing."""
        return f"Processed {processing_type} for {source_type} in {language}"

    async def process_content_with_user_prompt(
        self,
        content: str,
        processing_type: str,
        source_type: str,
        user_id: int,
        user_prompt: str,
        language: str
    ) -> str:
        """Mock content processing with user prompt."""
        return f"Processed {processing_type} with prompt: {user_prompt} in {language}"
