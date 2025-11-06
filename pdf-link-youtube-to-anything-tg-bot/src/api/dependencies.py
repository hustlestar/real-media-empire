"""FastAPI dependencies."""

from config.settings import BotConfig
from core.database import DatabaseManager
from core.ai_provider import OpenRouterProvider
from services.file_storage import FileStorageService
from services.content_service import ContentService
from services.processing_service import ProcessingService
from services.tag_service import TagService
from services.bundle_service import BundleService
from processors.ai_processor import AIProcessor

# Load configuration
config = BotConfig.from_env()

# Initialize singletons
_db_manager: DatabaseManager = None
_file_storage: FileStorageService = None
_content_service: ContentService = None
_processing_service: ProcessingService = None
_tag_service: TagService = None
_bundle_service: BundleService = None
_ai_processor: AIProcessor = None


async def get_database() -> DatabaseManager:
    """Get database manager instance."""
    global _db_manager
    if _db_manager is None:
        _db_manager = DatabaseManager(config.database_url, auto_migrate=False)
        await _db_manager.setup()
    return _db_manager


async def get_file_storage() -> FileStorageService:
    """Get file storage service instance."""
    global _file_storage
    if _file_storage is None:
        _file_storage = FileStorageService(config)
    return _file_storage


async def get_ai_processor() -> AIProcessor:
    """Get AI processor instance."""
    global _ai_processor
    if _ai_processor is None:
        ai_provider = OpenRouterProvider(
            api_key=config.openrouter_api_key,
            model=config.openrouter_model
        )
        _ai_processor = AIProcessor(ai_provider)
    return _ai_processor


async def get_content_service() -> ContentService:
    """Get content service instance."""
    global _content_service
    if _content_service is None:
        db = await get_database()
        file_storage = await get_file_storage()
        ai_processor = await get_ai_processor()
        _content_service = ContentService(db, file_storage, ai_processor)
    return _content_service


async def get_tag_service() -> TagService:
    """Get tag service instance."""
    global _tag_service
    if _tag_service is None:
        db = await get_database()
        _tag_service = TagService(db)
    return _tag_service


async def get_processing_service() -> ProcessingService:
    """Get processing service instance."""
    global _processing_service
    if _processing_service is None:
        db = await get_database()
        file_storage = await get_file_storage()

        # Initialize AI provider
        ai_provider = OpenRouterProvider(
            api_key=config.openrouter_api_key,
            model=config.openrouter_model
        )
        ai_processor = AIProcessor(ai_provider)

        _processing_service = ProcessingService(db, file_storage, ai_processor)
    return _processing_service


async def get_bundle_service() -> BundleService:
    """Get bundle service instance."""
    global _bundle_service
    if _bundle_service is None:
        db = await get_database()
        _bundle_service = BundleService(db)
    return _bundle_service


# Placeholder for future API key authentication
async def get_current_user_id() -> int:
    """Get current user ID (placeholder - returns demo user ID).

    In production, this would validate API key and return associated user_id.
    For now, return your actual Telegram user ID.
    """
    # Return your Telegram user ID so UI shows content from bot
    # TODO: Implement proper API key authentication
    return 66395090  # Your Telegram user ID