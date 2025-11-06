# PDF & YouTube Content Processing Bot

Telegram bot that processes PDFs, YouTube videos, and web content with AI-powered insights.

## Quick Start

```bash
# Clone and setup
git clone https://github.com/hustlestar/pdf-link-youtube-to-anything-tg-bot.git
cd pdf-link-youtube-to-anything-tg-bot
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
uv sync

# Configure
cp .env.example .env
# Edit .env with your TELEGRAM_BOT_TOKEN and DATABASE_URL

# Database
createdb pdf_link_youtube_to_anything_tg_bot
pdf-link-youtube-to-anything-tg-bot migrate

# Run
pdf-link-youtube-to-anything-tg-bot
```

## Features

- **Process**: PDFs, YouTube videos, web pages
- **Generate**: Summaries, MVP plans, content ideas
- **Support**: Multi-language (EN/RU/ES), custom instructions
- **Tech**: PostgreSQL, OpenRouter AI, auto-migrations

## Usage

1. Send `/start` to begin
2. Send PDF file/URL, YouTube URL, or webpage URL
3. Choose: Summary, MVP Plan, or Content Ideas
4. Add custom instructions (optional)
5. Get AI-generated insights

## Development

```bash
# Tests
pytest --cov=pdf_link_youtube_to_anything_tg_bot

# Code quality
black pdf_link_youtube_to_anything_tg_bot/
mypy pdf_link_youtube_to_anything_tg_bot/

# Migrations
pdf-link-youtube-to-anything-tg-bot db revision -m "Description"
pdf-link-youtube-to-anything-tg-bot db upgrade
```

## Deploy

Set GitHub Secrets: `TELEGRAM_BOT_TOKEN`, `DATABASE_URL`, `OPENROUTER_API_KEY`
Push to main branch for auto-deployment.

## License

MIT

## Author

Jack Ma - hustlequeen@mail.ru