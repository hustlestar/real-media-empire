"""Main entry point for the Telegram bot template with click CLI options."""

import asyncio
import logging
import sys
import threading

import click

from config.settings import BotConfig
from core.bot import TelegramBot

logger = logging.getLogger(__name__)

@click.command()
@click.option("--locale", default="en", help="Bot default language (en, ru, es, etc.)", show_default=True)
@click.option("--debug", is_flag=True, help="Enable debug mode with verbose logging")
@click.option("--support", is_flag=True, help="Force enable support bot (overrides env config)")
@click.option("--config-file", type=click.Path(exists=True), help="Path to custom configuration file")
@click.option("--dry-run", is_flag=True, help="Validate configuration without starting the bot")
@click.option("--stats", is_flag=True, help="Show bot statistics and exit")
@click.option("--api-only", is_flag=True, help="Start only the API server")
@click.option("--bot-only", is_flag=True, help="Start only the Telegram bot")
@click.version_option(version="1.0.0", prog_name="Telegram Bot Template")
def main(locale: str, debug: bool, support: bool, config_file: str, dry_run: bool, stats: bool, api_only: bool, bot_only: bool):
    """
    Simplified Telegram Bot Template

    A clean, maintainable Telegram bot with essential features:
    - Locale management
    - Keyboard management
    - OpenRouter AI integration
    - Optional support bot
    - Simple user database

    Examples:
        python -m pdf_link_youtube_to_anything_tg_bot --locale ru --debug
        python -m pdf_link_youtube_to_anything_tg_bot --support --dry-run
    """

    log_level = logging.DEBUG if debug else logging.INFO
    logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=log_level)

    try:
        config = BotConfig.from_env()

        # Override locale if provided
        if locale != "en":
            config.default_language = locale
            if locale not in config.supported_languages:
                config.supported_languages.append(locale)

        # Override debug mode
        if debug:
            config.log_level = "DEBUG"

        # Force enable support bot if requested
        if support and not config.has_support_bot:
            click.echo("WARNING: Support bot requested but not properly configured in environment")
            click.echo("   Please set SUPPORT_BOT_TOKEN and SUPPORT_CHAT_ID")
            sys.exit(1)

        config.validate()

        click.echo(f"{config.bot_name} v{config.bot_version}")
        click.echo(f"Language: {config.default_language}")
        click.echo(f"AI Support: {'enabled' if config.has_ai_support else 'disabled'}")
        click.echo(f"Support Bot: {'enabled' if config.has_support_bot else 'disabled'}")

        if dry_run:
            click.echo("Configuration validation passed")
            click.echo("Dry run mode - bot not started")
            return

        if stats:
            asyncio.run(show_stats(config))
            return

        # Determine what to run
        if api_only:
            click.echo("Starting API server only...")
            start_api(config)
        elif bot_only:
            click.echo("Starting bot only...")
            bot = TelegramBot(config)
            asyncio.run(bot.run())
        else:
            # Start both API and bot
            click.echo("Starting API server and Telegram bot...")
            api_thread = threading.Thread(target=start_api, args=(config,), daemon=True)
            api_thread.start()

            # Give API time to start
            import time
            time.sleep(2)

            bot = TelegramBot(config)
            asyncio.run(bot.run())

    except KeyboardInterrupt:
        click.echo("\nBot stopped by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        raise e

def start_api(config: BotConfig):
    """Start the FastAPI server."""
    import uvicorn

    logger.info(f"Starting Content Processing API")
    logger.info(f"Host: {config.api_host}")
    logger.info(f"Port: {config.api_port}")
    logger.info(f"Documentation: http://{config.api_host}:{config.api_port}/docs")

    uvicorn.run(
        "api.app:app",
        host=config.api_host,
        port=config.api_port,
        log_level=config.log_level.lower(),
        reload=False
    )


async def show_stats(config: BotConfig):
    """Show bot statistics."""
    try:
        bot = TelegramBot(config)
        await bot.setup()

        stats = await bot.get_stats()

        click.echo("\nBot Statistics:")
        click.echo("=" * 40)

        for key, value in stats.items():
            if isinstance(value, dict):
                click.echo(f"{key.replace('_', ' ').title()}:")
                for sub_key, sub_value in value.items():
                    click.echo(f"  - {sub_key}: {sub_value}")
            else:
                click.echo(f"{key.replace('_', ' ').title()}: {value}")

        await bot.stop()

    except Exception as e:
        click.echo(f"ERROR: Error getting stats: {e}", err=True)

@click.group()
def cli():
    """Telegram Bot Template CLI."""
    pass

@cli.command()
def validate():
    """Validate bot configuration."""
    try:
        config = BotConfig.from_env()
        config.validate()

        click.echo("Configuration is valid")
        click.echo(f"Bot: {config.bot_name}")
        click.echo(f"Database: {config.database_url[:20]}...")
        click.echo(f"AI: {'Enabled' if config.has_ai_support else 'Disabled'}")
        click.echo(f"Support: {'Enabled' if config.has_support_bot else 'Disabled'}")

    except Exception as e:
        click.echo(f"ERROR: Configuration error: {e}", err=True)
        sys.exit(1)

@cli.command()
def test_db():
    """Test database connection."""

    async def _test():
        try:
            config = BotConfig.from_env()

            from core.database import DatabaseManager

            db = DatabaseManager(config.database_url)

            click.echo("Testing database connection...")
            await db.setup()

            # Test basic operations
            stats = await db.get_stats()
            click.echo("Database connection successful")
            click.echo(f"Total users: {stats.get('total_users', 0)}")

            await db.close()

        except Exception as e:
            click.echo(f"ERROR: Database test error: {e}", err=True)

    asyncio.run(_test())

cli.add_command(validate)
cli.add_command(test_db)

if __name__ == "__main__":
    main()
