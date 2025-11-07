"""Configuration module for the Telegram bot template."""

from .settings import BotConfig
from dotenv import dotenv_values

# For compatibility with media-empire shared library
CONFIG = dotenv_values()

__all__ = ["BotConfig", "CONFIG"]
