"""Content hash calculation and normalization service."""

import hashlib
import logging
from typing import BinaryIO
from urllib.parse import urlparse, urlunparse

logger = logging.getLogger(__name__)


class HashService:
    """Service for calculating content hashes for deduplication."""

    @staticmethod
    def hash_url(url: str) -> str:
        """Normalize URL and calculate SHA256 hash.

        Args:
            url: URL to hash

        Returns:
            SHA256 hex digest of normalized URL
        """
        # Parse URL
        parsed = urlparse(url)

        # Normalize:
        # - Convert to lowercase
        # - Remove query parameters and fragments
        # - Remove trailing slashes from path
        # - Sort query parameters if we decide to keep them (currently removed)
        normalized_url = urlunparse((
            parsed.scheme.lower(),
            parsed.netloc.lower(),
            parsed.path.rstrip('/') or '/',
            '',  # Remove params
            '',  # Remove query
            ''   # Remove fragment
        ))

        # Calculate hash
        hash_obj = hashlib.sha256(normalized_url.encode('utf-8'))
        return hash_obj.hexdigest()

    @staticmethod
    async def hash_file_content(file: BinaryIO) -> str:
        """Calculate SHA256 of file content using streaming.

        Args:
            file: Binary file object

        Returns:
            SHA256 hex digest of file content
        """
        hash_obj = hashlib.sha256()
        chunk_size = 8192  # 8KB chunks

        while True:
            chunk = file.read(chunk_size)
            if not chunk:
                break
            hash_obj.update(chunk)

        return hash_obj.hexdigest()

    @staticmethod
    def hash_text(text: str) -> str:
        """Calculate SHA256 of text content.

        Args:
            text: Text to hash

        Returns:
            SHA256 hex digest
        """
        hash_obj = hashlib.sha256(text.encode('utf-8'))
        return hash_obj.hexdigest()

    @staticmethod
    def hash_bytes(data: bytes) -> str:
        """Calculate SHA256 of byte data.

        Args:
            data: Bytes to hash

        Returns:
            SHA256 hex digest
        """
        hash_obj = hashlib.sha256(data)
        return hash_obj.hexdigest()