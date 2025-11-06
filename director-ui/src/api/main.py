"""FastAPI application entry point."""

import logging
import uvicorn
from config.settings import BotConfig

# Setup logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)


def main():
    """Start the FastAPI server."""
    config = BotConfig.from_env()

    logger.info(f"Starting Content Processing API")
    logger.info(f"Host: {config.api_host}")
    logger.info(f"Port: {config.api_port}")
    logger.info(f"Documentation: http://{config.api_host}:{config.api_port}/docs")

    uvicorn.run(
        "api.app:app",
        host=config.api_host,
        port=config.api_port,
        log_level=config.log_level.lower(),
        reload=False  # Set to True for development
    )


if __name__ == "__main__":
    main()