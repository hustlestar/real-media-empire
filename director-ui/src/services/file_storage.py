"""File storage service for managing content files."""

import aiofiles
import logging
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Tuple, Optional
from uuid import UUID

logger = logging.getLogger(__name__)


class FileStorageService:
    """Manages file-based content storage."""

    def __init__(self, config):
        """Initialize file storage service.

        Args:
            config: BotConfig instance with storage paths
        """
        self.config = config
        self.extracted_path = Path(config.extracted_text_path)
        self.results_path = Path(config.processing_results_path)
        self.uploads_path = Path(config.uploads_path)

        # Ensure directories exist
        self._ensure_directories()

    def _ensure_directories(self) -> None:
        """Create storage directories if they don't exist."""
        for path in [self.extracted_path, self.results_path, self.uploads_path]:
            path.mkdir(parents=True, exist_ok=True)
            logger.info(f"Ensured directory exists: {path}")

    def _get_date_subpath(self) -> str:
        """Get current date-based subpath (YYYY/MM format)."""
        now = datetime.now()
        return f"{now.year}/{now.month:02d}"

    async def save_extracted_text(self, content_hash: str, text: str, language: str = 'en') -> str:
        """Save extracted text to file with language suffix.

        Args:
            content_hash: Content hash for filename
            text: Extracted text content
            language: Language code (en, ru, es)

        Returns:
            Relative file path
        """
        date_subpath = self._get_date_subpath()
        full_path = self.extracted_path / date_subpath
        full_path.mkdir(parents=True, exist_ok=True)

        # Include language in filename
        filename = f"{content_hash}_{language}.txt"
        file_path = full_path / filename
        relative_path = f"extracted/{date_subpath}/{filename}"

        async with aiofiles.open(file_path, 'w', encoding='utf-8') as f:
            await f.write(text)

        logger.info(f"Saved extracted text ({language}): {relative_path} ({len(text)} chars)")
        return relative_path

    async def save_processing_result(self, job_id: UUID, result: str) -> str:
        """Save AI processing result to file.

        Args:
            job_id: Processing job ID
            result: AI-generated result

        Returns:
            Relative file path
        """
        date_subpath = self._get_date_subpath()
        full_path = self.results_path / date_subpath
        full_path.mkdir(parents=True, exist_ok=True)

        filename = f"{job_id}.md"
        file_path = full_path / filename
        relative_path = f"results/{date_subpath}/{filename}"

        async with aiofiles.open(file_path, 'w', encoding='utf-8') as f:
            await f.write(result)

        logger.info(f"Saved processing result: {relative_path} ({len(result)} chars)")
        return relative_path

    async def save_uploaded_file(self, file_data: bytes, original_filename: str, file_hash: str) -> Tuple[str, str]:
        """Save uploaded file.

        Args:
            file_data: File content bytes
            original_filename: Original filename
            file_hash: Calculated file hash

        Returns:
            Tuple of (relative_path, extension)
        """
        date_subpath = self._get_date_subpath()
        full_path = self.uploads_path / date_subpath
        full_path.mkdir(parents=True, exist_ok=True)

        # Get file extension
        extension = Path(original_filename).suffix or '.pdf'
        filename = f"{file_hash}{extension}"
        file_path = full_path / filename
        relative_path = f"uploads/{date_subpath}/{filename}"

        async with aiofiles.open(file_path, 'wb') as f:
            await f.write(file_data)

        logger.info(f"Saved uploaded file: {relative_path} ({len(file_data)} bytes)")
        return relative_path, extension

    async def read_extracted_text(self, path: str) -> Optional[str]:
        """Read extracted text from file.

        Args:
            path: Relative file path

        Returns:
            File content or None if not found
        """
        from pathlib import Path
        file_path = Path(self.config.storage_base_path) / path

        if not file_path.exists():
            logger.warning(f"File not found: {file_path}")
            return None

        try:
            async with aiofiles.open(file_path, 'r', encoding='utf-8') as f:
                content = await f.read()
            return content
        except Exception as e:
            logger.error(f"Error reading file {file_path}: {e}")
            return None

    async def read_processing_result(self, path: str) -> Optional[str]:
        """Read processing result from file.

        Args:
            path: Relative file path

        Returns:
            File content or None if not found
        """
        file_path = Path(self.config.storage_base_path) / path

        if not file_path.exists():
            logger.warning(f"File not found: {file_path}")
            return None

        try:
            async with aiofiles.open(file_path, 'r', encoding='utf-8') as f:
                content = await f.read()
            return content
        except Exception as e:
            logger.error(f"Error reading file {file_path}: {e}")
            return None

    async def read_uploaded_file(self, path: str) -> Optional[bytes]:
        """Read uploaded file content.

        Args:
            path: Relative file path

        Returns:
            File content bytes or None if not found
        """
        file_path = Path(self.config.storage_base_path) / path

        if not file_path.exists():
            logger.warning(f"File not found: {file_path}")
            return None

        try:
            async with aiofiles.open(file_path, 'rb') as f:
                content = await f.read()
            return content
        except Exception as e:
            logger.error(f"Error reading file {file_path}: {e}")
            return None

    async def delete_file(self, path: str) -> bool:
        """Delete a file.

        Args:
            path: Relative file path

        Returns:
            True if deleted, False otherwise
        """
        file_path = Path(self.config.storage_base_path) / path

        if not file_path.exists():
            logger.warning(f"File not found for deletion: {file_path}")
            return False

        try:
            os.remove(file_path)
            logger.info(f"Deleted file: {file_path}")
            return True
        except Exception as e:
            logger.error(f"Error deleting file {file_path}: {e}")
            return False

    async def cleanup_old_files(self, days: Optional[int] = None) -> int:
        """Delete files older than specified days.

        Args:
            days: Number of days (uses config default if not specified)

        Returns:
            Number of files deleted
        """
        days = days or self.config.file_retention_days
        cutoff_date = datetime.now() - timedelta(days=days)
        deleted_count = 0

        for base_path in [self.extracted_path, self.results_path, self.uploads_path]:
            for file_path in base_path.rglob('*'):
                if file_path.is_file():
                    file_mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
                    if file_mtime < cutoff_date:
                        try:
                            os.remove(file_path)
                            deleted_count += 1
                            logger.debug(f"Deleted old file: {file_path}")
                        except Exception as e:
                            logger.error(f"Error deleting {file_path}: {e}")

        logger.info(f"Cleanup complete: deleted {deleted_count} files older than {days} days")
        return deleted_count