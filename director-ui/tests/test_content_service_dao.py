"""
Comprehensive DAO tests for ContentService with SQLite.

Tests all database operations including CRUD, deduplication, and edge cases.
"""

import pytest
from uuid import UUID
from io import BytesIO
import json


@pytest.mark.asyncio
class TestContentServiceDAO:
    """Test ContentService database operations."""

    async def test_get_by_hash_existing(self, content_service, test_content, test_user):
        """Test retrieving content by hash when it exists."""
        # Get the content to find its hash
        content = await content_service._get_by_id(test_content)
        assert content is not None

        content_hash = content['content_hash']

        # Retrieve by hash
        result = await content_service._get_by_hash(content_hash)

        assert result is not None
        assert result['id'] == test_content
        assert result['content_hash'] == content_hash

    async def test_get_by_hash_nonexistent(self, content_service):
        """Test retrieving content by non-existent hash."""
        result = await content_service._get_by_hash("nonexistent_hash")
        assert result is None

    async def test_get_by_id_existing(self, content_service, test_content):
        """Test retrieving content by ID when it exists."""
        result = await content_service._get_by_id(test_content)

        assert result is not None
        assert result['id'] == test_content
        assert result['source_type'] == 'pdf_url'

    async def test_get_by_id_nonexistent(self, content_service):
        """Test retrieving content by non-existent ID."""
        from uuid import uuid4
        fake_id = str(uuid4())

        result = await content_service._get_by_id(fake_id)
        assert result is None

    async def test_create_content_item(self, db_manager, content_service, file_storage, test_user):
        """Test creating a new content item."""
        import uuid

        content_hash = f"test_hash_{uuid.uuid4().hex[:8]}"

        # Write test text file
        test_text = "This is test content"
        text_path = await file_storage.save_extracted_text(content_hash, test_text)

        # Create content item
        content_id = await content_service._create_content_item(
            content_hash=content_hash,
            source_type="pdf_url",
            source_url="https://example.com/test2.pdf",
            file_reference=None,
            extracted_text_path=text_path,
            extracted_text_paths={"en": text_path},
            metadata={"title": "Test Document"},
            user_id=test_user,
            status="completed",
            detected_language="en"
        )

        assert content_id is not None
        assert isinstance(content_id, str)

        # Verify it was created
        content = await content_service._get_by_id(content_id)
        assert content is not None
        assert content['content_hash'] == content_hash
        assert content['user_id'] == test_user

    async def test_update_content_item(self, content_service, test_content, file_storage):
        """Test updating an existing content item."""
        # Get original content
        original = await content_service._get_by_id(test_content)
        original_hash = original['content_hash']

        # Create new text file
        new_text = "Updated content text"
        new_text_path = await file_storage.save_extracted_text(f"{original_hash}_updated", new_text)

        # Update content
        await content_service._update_content_item(
            content_id=test_content,
            extracted_text_path=new_text_path,
            extracted_text_paths={"en": new_text_path, "ru": "/test/russian.txt"},
            metadata={"title": "Updated Title"},
            detected_language="en"
        )

        # Verify update
        updated = await content_service._get_by_id(test_content)
        assert updated['extracted_text_path'] == new_text_path

        # Parse extracted_text_paths
        paths = updated['extracted_text_paths']
        if isinstance(paths, str):
            paths = json.loads(paths)
        assert "en" in paths
        assert "ru" in paths

    async def test_get_user_content_pagination(self, content_service, db_manager, test_user, file_storage):
        """Test paginating user content."""
        import uuid

        # Create multiple content items
        content_ids = []
        for i in range(5):
            content_hash = f"hash_{i}_{uuid.uuid4().hex[:8]}"
            text_path = await file_storage.save_extracted_text(content_hash, f"Content {i}")

            content_id = await content_service._create_content_item(
                content_hash=content_hash,
                source_type="pdf_url",
                source_url=f"https://example.com/test{i}.pdf",
                file_reference=None,
                extracted_text_path=text_path,
                extracted_text_paths={"en": text_path},
                metadata={"title": f"Test {i}"},
                user_id=test_user,
                status="completed"
            )
            content_ids.append(content_id)

        # Get first page
        items, total = await content_service.get_user_content(test_user, limit=2, offset=0)

        assert total >= 5  # At least our 5 items + test_content fixture
        assert len(items) == 2

        # Get second page
        items2, total2 = await content_service.get_user_content(test_user, limit=2, offset=2)

        assert total2 == total
        assert len(items2) == 2

        # Ensure no overlap
        page1_ids = {item['id'] for item in items}
        page2_ids = {item['id'] for item in items2}
        assert page1_ids.isdisjoint(page2_ids)

    async def test_get_user_content_filter_by_source_type(self, content_service, db_manager, test_user, file_storage):
        """Test filtering user content by source type."""
        import uuid

        # Create PDF and YouTube content
        pdf_hash = f"pdf_hash_{uuid.uuid4().hex[:8]}"
        pdf_path = await file_storage.save_extracted_text(pdf_hash, "PDF content")

        pdf_id = await content_service._create_content_item(
            content_hash=pdf_hash,
            source_type="pdf_url",
            source_url="https://example.com/doc.pdf",
            file_reference=None,
            extracted_text_path=pdf_path,
            extracted_text_paths={"en": pdf_path},
            metadata={},
            user_id=test_user,
            status="completed"
        )

        yt_hash = f"yt_hash_{uuid.uuid4().hex[:8]}"
        yt_path = await file_storage.save_extracted_text(yt_hash, "YouTube transcript")

        yt_id = await content_service._create_content_item(
            content_hash=yt_hash,
            source_type="youtube",
            source_url="https://youtube.com/watch?v=test",
            file_reference=None,
            extracted_text_path=yt_path,
            extracted_text_paths={"en": yt_path},
            metadata={},
            user_id=test_user,
            status="completed"
        )

        # Filter by PDF
        pdf_items, pdf_total = await content_service.get_user_content(
            test_user,
            source_type="pdf_url"
        )

        pdf_ids = {item['id'] for item in pdf_items}
        assert pdf_id in pdf_ids
        assert yt_id not in pdf_ids

        # Filter by YouTube
        yt_items, yt_total = await content_service.get_user_content(
            test_user,
            source_type="youtube"
        )

        yt_ids = {item['id'] for item in yt_items}
        assert yt_id in yt_ids
        assert pdf_id not in yt_ids

    async def test_get_content_by_id_with_authorization(self, content_service, test_content, test_user):
        """Test retrieving content with user authorization check."""
        # Correct user
        result = await content_service.get_content_by_id(test_content, test_user)
        assert result is not None
        assert result['id'] == test_content

        # Wrong user
        result = await content_service.get_content_by_id(test_content, test_user + 999)
        assert result is None

    async def test_get_content_with_text(self, content_service, test_content, test_user, file_storage):
        """Test retrieving content with extracted text included."""
        # Write actual text file
        content = await content_service._get_by_id(test_content)
        test_text = "This is the extracted text content"
        await file_storage.save_extracted_text(content['content_hash'], test_text)

        # Update content with real path
        from pathlib import Path
        text_path = f"{file_storage.extracted_text_path}/{content['content_hash']}.txt"
        await content_service._update_content_item(
            content_id=test_content,
            extracted_text_path=text_path,
            extracted_text_paths={"en": text_path},
            metadata=content.get('metadata', {}),
            detected_language="en"
        )

        # Get with text
        result = await content_service.get_content_with_text(test_content, test_user)

        assert result is not None
        assert 'extracted_text' in result
        assert result['extracted_text'] == test_text

    async def test_get_content_text(self, content_service, test_content, file_storage):
        """Test retrieving only the extracted text."""
        # Write actual text file
        content = await content_service._get_by_id(test_content)
        test_text = "Just the text, please"
        await file_storage.save_extracted_text(content['content_hash'], test_text)

        # Update content with real path
        from pathlib import Path
        text_path = f"{file_storage.extracted_text_path}/{content['content_hash']}.txt"
        await content_service._update_content_item(
            content_id=test_content,
            extracted_text_path=text_path,
            extracted_text_paths={"en": text_path},
            metadata=content.get('metadata', {}),
            detected_language="en"
        )

        # Get text
        result = await content_service.get_content_text(test_content)

        assert result is not None
        assert result == test_text

    async def test_update_detected_language(self, content_service, test_content, test_user):
        """Test updating detected language field."""
        # Update to Russian
        success = await content_service.update_detected_language(test_content, "ru", test_user)
        assert success is True

        # Verify update
        content = await content_service._get_by_id(test_content)
        assert content['detected_language'] == "ru"

        # Update to Spanish
        success = await content_service.update_detected_language(test_content, "es", test_user)
        assert success is True

        content = await content_service._get_by_id(test_content)
        assert content['detected_language'] == "es"

    async def test_update_detected_language_invalid_language(self, content_service, test_content, test_user):
        """Test updating with invalid language code."""
        with pytest.raises(ValueError, match="Invalid language"):
            await content_service.update_detected_language(test_content, "invalid", test_user)

    async def test_update_detected_language_unauthorized(self, content_service, test_content, test_user):
        """Test updating language with wrong user."""
        success = await content_service.update_detected_language(
            test_content,
            "ru",
            test_user + 999
        )
        assert success is False

    async def test_delete_content(self, content_service, db_manager, test_user, file_storage):
        """Test deleting content item."""
        import uuid

        # Create content to delete
        content_hash = f"delete_hash_{uuid.uuid4().hex[:8]}"
        text_path = await file_storage.save_extracted_text(content_hash, "Content to delete")

        content_id = await content_service._create_content_item(
            content_hash=content_hash,
            source_type="pdf_url",
            source_url="https://example.com/delete.pdf",
            file_reference=None,
            extracted_text_path=text_path,
            extracted_text_paths={"en": text_path},
            metadata={},
            user_id=test_user,
            status="completed"
        )

        # Verify exists
        content = await content_service._get_by_id(content_id)
        assert content is not None

        # Delete
        success = await content_service.delete_content(content_id, test_user)
        assert success is True

        # Verify deleted
        content = await content_service._get_by_id(content_id)
        assert content is None

    async def test_delete_content_unauthorized(self, content_service, test_content, test_user):
        """Test deleting content with wrong user."""
        success = await content_service.delete_content(test_content, test_user + 999)
        assert success is False

        # Verify still exists
        content = await content_service._get_by_id(test_content)
        assert content is not None

    async def test_parse_content_row_with_json_fields(self, content_service):
        """Test parsing content row with JSON metadata."""
        # Create mock row with JSON strings
        class MockRow:
            def __init__(self):
                self.data = {
                    'id': 'test-id',
                    'content_hash': 'test-hash',
                    'content_metadata': '{"title": "Test", "count": 42}',
                    'extracted_text_paths': '{"en": "/path/en.txt", "ru": "/path/ru.txt"}'
                }

            def __getitem__(self, key):
                return self.data[key]

            def keys(self):
                return self.data.keys()

        row = MockRow()
        parsed = content_service._parse_content_row(row)

        assert parsed is not None
        assert parsed['id'] == 'test-id'
        assert isinstance(parsed['metadata'], dict)
        assert parsed['metadata']['title'] == "Test"
        assert parsed['metadata']['count'] == 42
        assert isinstance(parsed['extracted_text_paths'], dict)
        assert parsed['extracted_text_paths']['en'] == "/path/en.txt"

    async def test_parse_content_row_with_null_metadata(self, content_service):
        """Test parsing content row with null metadata."""
        class MockRow:
            def __init__(self):
                self.data = {
                    'id': 'test-id',
                    'content_hash': 'test-hash',
                    'content_metadata': None,
                    'extracted_text_paths': None
                }

            def __getitem__(self, key):
                return self.data[key]

            def keys(self):
                return self.data.keys()

        row = MockRow()
        parsed = content_service._parse_content_row(row)

        assert parsed is not None
        assert parsed['metadata'] == {}
        assert parsed['extracted_text_paths'] is None

    async def test_create_content_item_in_transaction(self, db_manager, content_service, test_user, file_storage):
        """Test creating content item within a transaction."""
        import uuid

        content_hash = f"transaction_hash_{uuid.uuid4().hex[:8]}"
        text_path = await file_storage.save_extracted_text(content_hash, "Transaction test")

        async with db_manager._pool.acquire() as conn:
            async with conn.transaction():
                content_id = await content_service._create_content_item_in_transaction(
                    conn,
                    content_hash=content_hash,
                    source_type="web",
                    source_url="https://example.com/web",
                    file_reference=None,
                    extracted_text_path=text_path,
                    extracted_text_paths={"en": text_path},
                    metadata={"url": "https://example.com/web"},
                    user_id=test_user,
                    status="completed",
                    detected_language="en"
                )

                assert content_id is not None

        # Verify content was committed
        content = await content_service._get_by_id(content_id)
        assert content is not None
        assert content['content_hash'] == content_hash

    async def test_concurrent_content_creation(self, content_service, test_user, file_storage):
        """Test creating multiple content items concurrently."""
        import uuid
        import asyncio

        async def create_content(i):
            content_hash = f"concurrent_{i}_{uuid.uuid4().hex[:8]}"
            text_path = await file_storage.save_extracted_text(content_hash, f"Concurrent {i}")

            return await content_service._create_content_item(
                content_hash=content_hash,
                source_type="pdf_url",
                source_url=f"https://example.com/concurrent{i}.pdf",
                file_reference=None,
                extracted_text_path=text_path,
                extracted_text_paths={"en": text_path},
                metadata={},
                user_id=test_user,
                status="completed"
            )

        # Create 3 content items concurrently
        content_ids = await asyncio.gather(*[create_content(i) for i in range(3)])

        assert len(content_ids) == 3
        assert len(set(content_ids)) == 3  # All unique

        # Verify all exist
        for content_id in content_ids:
            content = await content_service._get_by_id(content_id)
            assert content is not None

    async def test_empty_user_content_list(self, content_service, db_manager):
        """Test getting content for user with no content."""
        # Create a new user with no content
        async with db_manager.session() as session:
            from sqlalchemy import text
            result = await session.execute(
                text("""
                    INSERT INTO users (id, email, hashed_password, is_active, created_at, updated_at)
                    VALUES (999, 'empty@example.com', 'hashed', TRUE, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                    RETURNING id
                """)
            )
            await session.commit()

        items, total = await content_service.get_user_content(999, limit=20, offset=0)

        assert total == 0
        assert len(items) == 0
