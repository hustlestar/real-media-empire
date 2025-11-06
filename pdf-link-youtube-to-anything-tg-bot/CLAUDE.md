# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

### Development Setup
```bash
# Install dependencies using uv
uv sync

# Install dev dependencies
uv add --dev pytest pytest-asyncio pytest-cov black isort mypy

# Setup environment
cp .env.example .env
# Edit .env with required values:
# - TELEGRAM_BOT_TOKEN (from @BotFather)
# - DATABASE_URL (PostgreSQL connection)
# - OPENROUTER_API_KEY (for AI features)
```

### Running the Application
```bash
# Start both bot and API (recommended for production)
PYTHONPATH=src python -m main

# Start only the API server
PYTHONPATH=src python -m main --api-only

# Start only the Telegram bot
PYTHONPATH=src python -m main --bot-only

# With additional options
PYTHONPATH=src python -m main --debug --locale ru

# Legacy: Start API separately (deprecated)
PYTHONPATH=src python -m api.main
```

### Database Management
```bash
# Create database
createdb pdf_link_youtube_to_anything_tg_bot

# Apply migrations (shortcut)
pdf-link-youtube-to-anything-tg-bot migrate

# Database commands
pdf-link-youtube-to-anything-tg-bot db status
pdf-link-youtube-to-anything-tg-bot db upgrade
pdf-link-youtube-to-anything-tg-bot db downgrade
pdf-link-youtube-to-anything-tg-bot db revision -m "Description"
pdf-link-youtube-to-anything-tg-bot db history
```

### Testing
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=pdf_link_youtube_to_anything_tg_bot

# Run specific test categories
pytest -m unit
pytest -m integration
pytest -m "not slow"

# Run single test file
pytest tests/test_bot.py::TestSpecificClass::test_specific_method
```

### Code Quality
```bash
# Format code (line length: 140)
black src/

# Sort imports
isort src/

# Type checking (strict mode enabled)
mypy src/

# Run all quality checks
black src/ && isort src/ && mypy src/
```

## Architecture

### Core Components

**Bot Entry (`src/main.py`, `src/core/bot.py`)**
- Main bot initialization and lifecycle management
- Sets up all components: database, localization, keyboards, AI provider
- Handles graceful shutdown with signal handling
- CLI interface for configuration and management

**Content Processing Pipeline**
1. **Message Reception** (`src/handlers/message.py`): Receives user input (text, files, URLs)
2. **URL Detection** (`src/utils/url_detector.py`): Classifies URLs as YouTube, PDF, or web content
3. **Content Processors** (`src/processors/`):
   - `PDFProcessor`: Extracts text from PDF files and URLs using pypdf
   - `YouTubeProcessor`: Downloads transcripts/captions using yt-dlp
   - `WebScraperProcessor`: Extracts main content from web pages using Crawl4AI
4. **AI Processing** (`src/processors/ai_processor.py`): 
   - Generates summaries, MVP plans, or content ideas
   - Uses PromptManager for structured prompts
5. **Content Storage** (`src/utils/content_storage.py`): Temporary storage with user context
6. **Markdown Saving** (`src/utils/markdown_saver.py`): Saves AI outputs to markdown files

**Database Layer**
- SQLAlchemy models in `src/models/` with async support (asyncpg)
- Migration system using Alembic (`alembic/`)
- Auto-migration on startup via `MigrationManager`
- User tracking and preferences storage

**AI Integration**
- Abstract interface `AIProviderInterface` for provider flexibility
- OpenRouter implementation with model selection
- Prompt management system with templates for different content types
- Support for custom user instructions

**Localization System**
- Multi-language support (EN, RU, ES) via YAML files in `locales/`
- Dynamic language switching per user
- Locale-aware keyboard generation

**Callback Flow**
When user selects processing option:
1. `BasicHandlers.handle_callback_query` receives callback
2. Retrieves stored content from `ContentStorage`
3. Routes to appropriate processor based on action
4. Applies custom instructions if provided
5. Returns formatted AI response to user

## Key Patterns

- **Dependency Injection**: Components receive dependencies through constructors
- **Async/Await**: Entire codebase uses asyncio for concurrent operations
- **Factory Pattern**: BotConfig.from_env() creates configuration from environment
- **Repository Pattern**: DatabaseManager abstracts database operations
- **Strategy Pattern**: Different processors for different content types
- **Template Method**: PromptManager provides structured prompt generation

## Environment Variables

Required:
- `TELEGRAM_BOT_TOKEN`: Bot token from BotFather
- `DATABASE_URL`: PostgreSQL connection string

AI Features:
- `OPENROUTER_API_KEY`: API key for AI processing
- `OPENROUTER_MODEL`: Model selection (default: deepseek/deepseek-chat-v3-0324)

Configuration:
- `DEFAULT_LANGUAGE`: Default bot language (en/ru/es)
- `SUPPORTED_LANGUAGES`: Comma-separated language codes
- `LOG_LEVEL`: Logging verbosity (DEBUG/INFO/WARNING/ERROR)
- `PYTHONPATH`: Should be set to "src" for imports