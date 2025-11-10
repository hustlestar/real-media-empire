"""Configuration settings for the Telegram bot template."""

import os
import logging
from dataclasses import dataclass, field
from typing import Optional, List
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

@dataclass
class BotConfig:
    """Configuration class for the Director UI application.

    All Telegram features are optional. The API can run standalone without Telegram.
    """

    # Required settings
    database_url: str

    # Optional Telegram bot
    bot_token: Optional[str] = None

    # Optional AI settings
    openrouter_api_key: Optional[str] = None
    openrouter_model: str = "openai/gpt-3.5-turbo"

    # Optional support bot settings
    support_bot_token: Optional[str] = None
    support_chat_id: Optional[int] = None
    MAINTAINER_CHAT_ID: Optional[int] = None  # For critical alerts

    # Database migration settings
    auto_migrate: bool = True
    migration_timeout: int = 300  # 5 minutes

    # Localization settings
    default_language: str = "en"
    supported_languages: List[str] = field(default_factory=lambda: ["en", "ru", "es"])

    # Bot metadata
    bot_name: str = "Telegram Bot"
    bot_description: str = "A simple Telegram bot"
    bot_version: str = "1.0.0"

    # Logging settings
    log_level: str = "INFO"

    # API settings
    api_enabled: bool = True
    api_host: str = "0.0.0.0"
    api_port: int = 10000
    api_cors_origins: List[str] = field(default_factory=lambda: ["*"])

    # Storage settings
    storage_base_path: str = "./storage"
    extracted_text_path: str = "./storage/extracted"
    processing_results_path: str = "./storage/results"
    uploads_path: str = "./storage/uploads"
    max_file_size_mb: int = 50
    file_retention_days: int = 90

    @classmethod
    def from_env(cls) -> "BotConfig":
        """Create configuration from environment variables."""

        # Database URL - fallback to aiosqlite if not set
        database_url = os.getenv("DATABASE_URL")
        if not database_url:
            database_url = "sqlite+aiosqlite:///./director_ui.db"
            logger.warning("⚠️  DATABASE_URL not set - using SQLite: director_ui.db")
            logger.info("    Set DATABASE_URL for PostgreSQL: postgresql+asyncpg://user:pass@host/db")

        # Optional Telegram bot token
        bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
        if not bot_token:
            logger.warning("⚠️  TELEGRAM_BOT_TOKEN not set - Telegram bot features will be disabled")
            logger.info("    API will run standalone without Telegram integration")

        # Optional environment variables
        openrouter_api_key = os.getenv("OPENROUTER_API_KEY")
        openrouter_model = os.getenv("OPENROUTER_MODEL", "openai/gpt-3.5-turbo")

        support_bot_token = os.getenv("SUPPORT_BOT_TOKEN")
        support_chat_id_str = os.getenv("SUPPORT_CHAT_ID")
        support_chat_id = int(support_chat_id_str) if support_chat_id_str else None

        maintainer_chat_id_str = os.getenv("MAINTAINER_CHAT_ID")
        maintainer_chat_id = int(maintainer_chat_id_str) if maintainer_chat_id_str else None

        # Bot metadata
        bot_name = os.getenv("BOT_NAME", "Telegram Bot")
        bot_description = os.getenv("BOT_DESCRIPTION", "A simple Telegram bot")
        bot_version = os.getenv("BOT_VERSION", "1.0.0")

        # Database migration settings
        auto_migrate_str = os.getenv("AUTO_MIGRATE", "true").lower()
        auto_migrate = auto_migrate_str in ("true", "1", "yes", "on")
        migration_timeout = int(os.getenv("MIGRATION_TIMEOUT", "300"))

        # Localization
        default_language = os.getenv("DEFAULT_LANGUAGE", "en")
        supported_languages_str = os.getenv("SUPPORTED_LANGUAGES", "en,ru,es")
        supported_languages = [lang.strip() for lang in supported_languages_str.split(",")]

        # Logging
        log_level = os.getenv("LOG_LEVEL", "INFO")

        # API settings
        api_enabled_str = os.getenv("API_ENABLED", "true").lower()
        api_enabled = api_enabled_str in ("true", "1", "yes", "on")
        api_host = os.getenv("API_HOST", "0.0.0.0")
        api_port = int(os.getenv("API_PORT", "10000"))
        api_cors_origins_str = os.getenv("API_CORS_ORIGINS", "*")
        api_cors_origins = [origin.strip() for origin in api_cors_origins_str.split(",")]

        # Storage settings
        storage_base_path = os.getenv("STORAGE_BASE_PATH", "./storage")
        extracted_text_path = os.getenv("EXTRACTED_TEXT_PATH", f"{storage_base_path}/extracted")
        processing_results_path = os.getenv("PROCESSING_RESULTS_PATH", f"{storage_base_path}/results")
        uploads_path = os.getenv("UPLOADS_PATH", f"{storage_base_path}/uploads")
        max_file_size_mb = int(os.getenv("MAX_FILE_SIZE_MB", "50"))
        file_retention_days = int(os.getenv("FILE_RETENTION_DAYS", "90"))

        return cls(
            bot_token=bot_token,
            database_url=database_url,
            openrouter_api_key=openrouter_api_key,
            openrouter_model=openrouter_model,
            support_bot_token=support_bot_token,
            support_chat_id=support_chat_id,
            auto_migrate=auto_migrate,
            migration_timeout=migration_timeout,
            default_language=default_language,
            supported_languages=supported_languages,
            bot_name=bot_name,
            bot_description=bot_description,
            bot_version=bot_version,
            log_level=log_level,
            MAINTAINER_CHAT_ID=maintainer_chat_id,
            api_enabled=api_enabled,
            api_host=api_host,
            api_port=api_port,
            api_cors_origins=api_cors_origins,
            storage_base_path=storage_base_path,
            extracted_text_path=extracted_text_path,
            processing_results_path=processing_results_path,
            uploads_path=uploads_path,
            max_file_size_mb=max_file_size_mb,
            file_retention_days=file_retention_days,
        )

    @property
    def has_telegram_bot(self) -> bool:
        """Check if Telegram bot is configured."""
        return self.bot_token is not None

    @property
    def has_ai_support(self) -> bool:
        """Check if AI support is available."""
        return self.openrouter_api_key is not None

    @property
    def has_support_bot(self) -> bool:
        """Check if support bot is configured."""
        return self.support_bot_token is not None and self.support_chat_id is not None

    def setup_logging(self) -> None:
        """Setup logging configuration."""
        logging.basicConfig(
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=getattr(logging, self.log_level.upper(), logging.INFO)
        )
        logger.info(f"Logging configured with level: {self.log_level}")

    def validate(self) -> None:
        """Validate configuration settings."""
        if not self.database_url:
            raise ValueError("Database URL is required")

        if not self.bot_token:
            logger.info("ℹ️  Telegram bot not configured - running in API-only mode")

        if self.default_language not in self.supported_languages:
            raise ValueError(f"Default language '{self.default_language}' not in supported languages")

        if self.support_bot_token and not self.support_chat_id:
            logger.warning("Support bot token provided but no support chat ID configured")

        if self.support_chat_id and not self.support_bot_token:
            logger.warning("Support chat ID provided but no support bot token configured")

        logger.info("Configuration validation passed")
