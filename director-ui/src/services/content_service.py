"""Content service for managing content items with deduplication."""

import logging
from typing import Optional, Dict, Any, Tuple, Union
from uuid import UUID
from datetime import datetime

from models.content import SourceType, ProcessingStatus
from services.hash_service import HashService
from services.file_storage import FileStorageService
from services.tag_service import TagService
from processors.pdf_processor import PDFProcessor
from processors.youtube_processor import YouTubeProcessor
from processors.web_scraper import WebScraperProcessor
from processors.ai_processor import AIProcessor

logger = logging.getLogger(__name__)


class ContentService:
    """Service for content management with deduplication."""

    def __init__(self, database, file_storage: FileStorageService, ai_processor: Optional[AIProcessor] = None):
        """Initialize content service.

        Args:
            database: DatabaseManager instance
            file_storage: FileStorageService instance
            ai_processor: Optional AIProcessor for language/tag detection
        """
        self.db = database
        self.file_storage = file_storage
        self.hash_service = HashService()
        self.tag_service = TagService(database)
        self.ai_processor = ai_processor

    async def get_or_create_from_url(
        self,
        url: str,
        source_type: str,
        user_id: int,
        force_reprocess: bool = False,
        target_language: Optional[str] = None
    ) -> Tuple[Dict[str, Any], bool]:
        """Get existing content by URL or create new.

        Args:
            url: Source URL
            source_type: Type of content (pdf_url, youtube, web)
            user_id: User ID
            force_reprocess: Force reprocessing even if exists

        Returns:
            Tuple of (content_dict, is_new)
        """
        # Calculate hash
        content_hash = self.hash_service.hash_url(url)

        # Check if exists
        existing = await self._get_by_hash(content_hash)
        if existing and not force_reprocess:
            logger.info(f"Content already exists for hash {content_hash}")
            return existing, False

        # Extract content
        extracted_text, metadata = await self._extract_from_url(url, source_type)

        if not extracted_text:
            raise ValueError(f"Failed to extract content from {url}")

        # Detect language and generate tags using AI
        detected_language = target_language  # Use target if provided
        tag_names = []
        if self.ai_processor:
            try:
                # Get all existing tags
                all_tags = await self.tag_service.get_all_tags()
                existing_tag_names = [tag['name'] for tag in all_tags]

                # Call AI for language and tag detection
                detection_result = await self.ai_processor.detect_language_and_generate_tags(
                    text=extracted_text,
                    existing_tags=existing_tag_names,
                    user_id=user_id
                )
                # Only override if target_language not provided
                if not detected_language:
                    detected_language = detection_result.get('language', 'en')
                tag_names = detection_result.get('tags', [])
                logger.info(f"Language: {detected_language} (target: {target_language}), tags: {tag_names}")
            except Exception as e:
                logger.error(f"Error in AI language/tag detection: {e}")
                detected_language = detected_language or 'en'
                tag_names = ['content', 'uncategorized']

        # Ensure we have a detected language
        if not detected_language:
            detected_language = 'en'

        # Save extracted text (with language suffix)
        text_path = await self.file_storage.save_extracted_text(
            content_hash,
            extracted_text,
            language=detected_language
        )

        # If reprocessing existing content, update it
        if existing and force_reprocess:
            content_id = existing['id']

            # Update extracted_text_paths JSONB
            extracted_text_paths = existing.get('extracted_text_paths') or {}
            extracted_text_paths[detected_language] = text_path

            await self._update_content_item(
                content_id=content_id,
                extracted_text_path=text_path,
                extracted_text_paths=extracted_text_paths,
                metadata=metadata,
                detected_language=detected_language
            )

            # Update tags (link_tags_to_content deletes old tags automatically)
            if tag_names:
                try:
                    tag_ids = await self.tag_service.get_or_create_tags(tag_names)
                    await self.tag_service.link_tags_to_content(content_id, tag_ids)
                except Exception as e:
                    logger.error(f"Error updating tags for content: {e}")

            content = await self._get_by_id(content_id)
            logger.info(f"Reprocessed existing content {content_id} for hash {content_hash}")
            return content, False

        # Create new content item in database
        extracted_text_paths = {detected_language: text_path}
        content_id = await self._create_content_item(
            content_hash=content_hash,
            source_type=source_type,
            source_url=url,
            file_reference=None,
            extracted_text_path=text_path,
            extracted_text_paths=extracted_text_paths,
            metadata=metadata,
            user_id=user_id,
            status=ProcessingStatus.COMPLETED.value,
            detected_language=detected_language
        )

        # Link tags to content
        if tag_names:
            try:
                tag_ids = await self.tag_service.get_or_create_tags(tag_names)
                await self.tag_service.link_tags_to_content(content_id, tag_ids)
            except Exception as e:
                logger.error(f"Error linking tags to content: {e}")

        content = await self._get_by_id(content_id)
        logger.info(f"Created new content {content_id} for hash {content_hash}")
        return content, True

    async def get_or_create_from_file(
        self,
        file,
        filename: str,
        user_id: int,
        force_reprocess: bool = False
    ) -> Tuple[Dict[str, Any], bool]:
        """Get existing content by file or create new.

        Args:
            file: File object (file-like object)
            filename: Original filename
            user_id: User ID
            force_reprocess: Force reprocessing even if exists

        Returns:
            Tuple of (content_dict, is_new)
        """
        # Read file content
        file_data = file.read()

        # Calculate hash of file content
        from io import BytesIO
        file_obj = BytesIO(file_data)
        content_hash = await self.hash_service.hash_file_content(file_obj)

        # Check if exists
        if not force_reprocess:
            existing = await self._get_by_hash(content_hash)
            if existing:
                logger.info(f"Content already exists for file hash {content_hash}")
                return existing, False

        # Save uploaded file
        file_path, extension = await self.file_storage.save_uploaded_file(
            file_data, filename, content_hash
        )

        # Extract content from file
        file_obj.seek(0)  # Reset file pointer
        extracted_text = await PDFProcessor.extract_text_from_bytes(file_obj)

        if not extracted_text:
            raise ValueError(f"Failed to extract text from PDF file")

        # Save extracted text
        text_path = await self.file_storage.save_extracted_text(content_hash, extracted_text)

        # Prepare metadata
        metadata = {
            "filename": filename,
            "size": len(file_data),
            "char_count": len(extracted_text)
        }

        # Create content item
        content_id = await self._create_content_item(
            content_hash=content_hash,
            source_type=SourceType.PDF_FILE.value,
            source_url=None,
            file_reference=file_path,
            extracted_text_path=text_path,
            metadata=metadata,
            user_id=user_id,
            status=ProcessingStatus.COMPLETED.value
        )

        content = await self._get_by_id(content_id)
        logger.info(f"Created new content {content_id} from uploaded file")
        return content, True

    async def _extract_from_url(self, url: str, source_type: str) -> Tuple[Optional[str], Dict]:
        """Extract content from URL based on type.

        Args:
            url: Source URL
            source_type: Content type

        Returns:
            Tuple of (extracted_text, metadata)
        """
        metadata = {}

        try:
            if source_type == SourceType.PDF_URL.value:
                text = await PDFProcessor.extract_text_from_url(url)
                metadata = {
                    "url": url,
                    "char_count": len(text) if text else 0
                }
                return text, metadata

            elif source_type == SourceType.YOUTUBE.value:
                youtube_processor = YouTubeProcessor()
                video_data = await youtube_processor.extract_content_from_url(url)

                if not video_data:
                    return None, {}

                # Combine title and transcript
                transcript = video_data.get('transcript', '')
                title = video_data.get('title', '')
                text = f"Title: {title}\n\nTranscript: {transcript}"

                metadata = {
                    "url": url,
                    "title": title,
                    "duration": video_data.get('duration'),
                    "char_count": len(text)
                }
                return text, metadata

            elif source_type == SourceType.WEB.value:
                web_data = await WebScraperProcessor.extract_content_from_url(url)

                if not web_data or not web_data.get('success'):
                    return None, {}

                content = WebScraperProcessor.clean_extracted_content(web_data.get('content', ''))
                title = web_data.get('title', 'Unknown Title')
                description = web_data.get('description', '')

                text = f"Title: {title}\n\n"
                if description:
                    text += f"Description: {description}\n\n"
                text += f"Content: {content}"

                metadata = {
                    "url": url,
                    "title": title,
                    "description": description,
                    "word_count": web_data.get('word_count', 0),
                    "char_count": len(text)
                }
                return text, metadata

        except Exception as e:
            logger.error(f"Error extracting from {url}: {e}")
            return None, {}

        return None, {}

    def _parse_content_row(self, row) -> Dict[str, Any]:
        """Parse content row and convert JSON fields."""
        import json
        if not row:
            return None

        content = dict(row)

        # Map content_metadata column to metadata field for API response
        # (metadata is reserved in SQLAlchemy, so DB column is content_metadata)
        if 'content_metadata' in content:
            content['metadata'] = content.pop('content_metadata')

        # Parse metadata JSON if it's a string
        if isinstance(content.get('metadata'), str):
            try:
                content['metadata'] = json.loads(content['metadata']) if content['metadata'] else {}
            except json.JSONDecodeError:
                content['metadata'] = {}
        elif content.get('metadata') is None:
            content['metadata'] = {}

        # Parse extracted_text_paths JSON if it's a string
        if isinstance(content.get('extracted_text_paths'), str):
            try:
                content['extracted_text_paths'] = json.loads(content['extracted_text_paths']) if content['extracted_text_paths'] else None
            except json.JSONDecodeError:
                content['extracted_text_paths'] = None

        return content

    async def _get_by_hash(self, content_hash: str) -> Optional[Dict[str, Any]]:
        """Get content by hash.

        Args:
            content_hash: Content hash

        Returns:
            Content dict or None
        """
        async with self.db._pool.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT * FROM content_items WHERE content_hash = $1",
                content_hash
            )
            return self._parse_content_row(row)

    async def _get_by_id(self, content_id: UUID) -> Optional[Dict[str, Any]]:
        """Get content by ID.

        Args:
            content_id: Content UUID

        Returns:
            Content dict or None
        """
        async with self.db._pool.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT * FROM content_items WHERE id = $1",
                content_id
            )
            return self._parse_content_row(row)

    async def _create_content_item(
        self,
        content_hash: str,
        source_type: str,
        source_url: Optional[str],
        file_reference: Optional[str],
        extracted_text_path: str,
        extracted_text_paths: Dict[str, str],
        metadata: Dict,
        user_id: int,
        status: str,
        detected_language: Optional[str] = None
    ) -> UUID:
        """Create content item in database.

        Returns:
            Content UUID
        """
        import json

        async with self.db._pool.acquire() as conn:
            row = await conn.fetchrow(
                """
                INSERT INTO content_items (
                    content_hash, source_type, source_url, file_reference,
                    extracted_text_path, extracted_text_paths, content_metadata, user_id, processing_status,
                    detected_language, created_at, updated_at
                )
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $11)
                RETURNING id
                """,
                content_hash,
                source_type,
                source_url,
                file_reference,
                extracted_text_path,
                json.dumps(extracted_text_paths),
                json.dumps(metadata),
                user_id,
                status,
                detected_language,
                datetime.utcnow()
            )
            return row['id']

    async def _update_content_item(
        self,
        content_id: UUID,
        extracted_text_path: str,
        extracted_text_paths: Dict[str, str],
        metadata: Dict,
        detected_language: Optional[str] = None
    ) -> None:
        """Update existing content item in database.

        Args:
            content_id: Content UUID
            extracted_text_path: Path to extracted text file
            metadata: Content metadata
            detected_language: Detected language code
        """
        import json

        async with self.db._pool.acquire() as conn:
            await conn.execute(
                """
                UPDATE content_items
                SET extracted_text_path = $1,
                    extracted_text_paths = $2,
                    metadata = $3,
                    detected_language = $4,
                    updated_at = $5
                WHERE id = $6
                """,
                extracted_text_path,
                json.dumps(extracted_text_paths),
                json.dumps(metadata),
                detected_language,
                datetime.utcnow(),
                content_id
            )

    async def get_user_content(
        self,
        user_id: int,
        limit: int = 20,
        offset: int = 0,
        source_type: Optional[str] = None
    ) -> Tuple[list, int]:
        """Get user's content with pagination.

        Args:
            user_id: User ID
            limit: Page size
            offset: Page offset
            source_type: Filter by source type

        Returns:
            Tuple of (content_list, total_count)
        """
        async with self.db._pool.acquire() as conn:
            # Build query
            where_clause = "WHERE ci.user_id = $1"
            params = [user_id]

            if source_type:
                where_clause += " AND ci.source_type = $2"
                params.append(source_type)

            # Get total count
            count_query = f"SELECT COUNT(*) FROM content_items ci {where_clause}"
            total = await conn.fetchval(count_query, *params)

            # Get items with tags in a single query using JSON aggregation
            items_query = f"""
                SELECT
                    ci.*,
                    COALESCE(
                        json_agg(t.name ORDER BY t.name) FILTER (WHERE t.name IS NOT NULL),
                        '[]'
                    ) as tags
                FROM content_items ci
                LEFT JOIN content_tags ct ON ci.id = ct.content_id
                LEFT JOIN tags t ON ct.tag_id = t.id
                {where_clause}
                GROUP BY ci.id
                ORDER BY ci.created_at DESC
                LIMIT ${len(params) + 1} OFFSET ${len(params) + 2}
            """
            params.extend([limit, offset])
            rows = await conn.fetch(items_query, *params)

            items = []
            for row in rows:
                item = self._parse_content_row(row)
                # tags are already included as JSON array from the query
                import json
                if isinstance(item.get('tags'), str):
                    item['tags'] = json.loads(item['tags'])
                items.append(item)

            return items, total

    async def get_content_by_id(self, content_id: UUID, user_id: int) -> Optional[Dict[str, Any]]:
        """Get content by ID with authorization check.

        Args:
            content_id: Content UUID
            user_id: User ID for authorization

        Returns:
            Content dict or None
        """
        import json

        async with self.db._pool.acquire() as conn:
            row = await conn.fetchrow(
                """
                SELECT
                    ci.*,
                    COALESCE(
                        json_agg(t.name ORDER BY t.name) FILTER (WHERE t.name IS NOT NULL),
                        '[]'
                    ) as tags
                FROM content_items ci
                LEFT JOIN content_tags ct ON ci.id = ct.content_id
                LEFT JOIN tags t ON ct.tag_id = t.id
                WHERE ci.id = $1 AND ci.user_id = $2
                GROUP BY ci.id
                """,
                content_id,
                user_id
            )

            if not row:
                return None

            content = self._parse_content_row(row)
            # Parse tags JSON array
            if isinstance(content.get('tags'), str):
                content['tags'] = json.loads(content['tags'])

            return content

    async def get_content_with_text(self, content_id: UUID, user_id: int, language: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Get content with extracted text included.

        Args:
            content_id: Content UUID
            user_id: User ID for authorization
            language: Optional language code to get specific language version

        Returns:
            Content dict with 'extracted_text' field or None
        """
        content = await self.get_content_by_id(content_id, user_id)
        if not content:
            return None

        # Determine which text file to read
        text_path = content['extracted_text_path']
        if language and content.get('extracted_text_paths'):
            # Try to get specific language version
            text_path = content['extracted_text_paths'].get(language, text_path)

        # Read text from file
        text = await self.file_storage.read_extracted_text(text_path)
        content['extracted_text'] = text or ""
        return content

    async def get_content_text(self, content_id: UUID) -> Optional[str]:
        """Get extracted text for content.

        Args:
            content_id: Content UUID

        Returns:
            Extracted text or None
        """
        content = await self._get_by_id(content_id)
        if not content:
            return None

        text_path = content['extracted_text_path']
        return await self.file_storage.read_extracted_text(text_path)

    async def update_detected_language(self, content_id: UUID, language: str, user_id: int) -> bool:
        """Update only the detected language field without touching file references.

        Args:
            content_id: Content UUID
            language: Language code (en/ru/es)
            user_id: User ID (for authorization)

        Returns:
            True if updated successfully, False if content not found
        """
        # Verify content belongs to user
        content = await self.get_content_by_id(content_id, user_id)
        if not content:
            return False

        # Validate language
        valid_languages = ['en', 'ru', 'es']
        if language not in valid_languages:
            raise ValueError(f"Invalid language: {language}. Must be one of {valid_languages}")

        async with self.db._pool.acquire() as conn:
            await conn.execute(
                """
                UPDATE content_items
                SET detected_language = $1,
                    updated_at = $2
                WHERE id = $3
                """,
                language,
                datetime.utcnow(),
                content_id
            )

        logger.info(f"Updated detected_language to {language} for content {content_id}")
        return True

    async def delete_content(self, content_id: UUID, user_id: int) -> bool:
        """Delete content item and associated files.

        Args:
            content_id: Content UUID
            user_id: User ID (for authorization)

        Returns:
            True if deleted
        """
        content = await self._get_by_id(content_id)
        if not content or content['user_id'] != user_id:
            return False

        # Delete files
        await self.file_storage.delete_file(content['extracted_text_path'])
        if content['file_reference']:
            await self.file_storage.delete_file(content['file_reference'])

        # Delete from database (cascade will delete related jobs)
        async with self.db._pool.acquire() as conn:
            await conn.execute(
                "DELETE FROM content_items WHERE id = $1",
                content_id
            )

        logger.info(f"Deleted content {content_id}")
        return True