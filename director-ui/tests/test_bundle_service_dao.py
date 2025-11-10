"""
Comprehensive DAO tests for BundleService with SQLite.

Tests all database operations for bundles and bundle attempts including CRUD and diffs.
"""

import pytest
from uuid import UUID, uuid4
import json


@pytest.mark.asyncio
class TestBundleServiceDAO:
    """Test BundleService database operations."""

    async def test_create_bundle(self, bundle_service, test_content, test_user):
        """Test creating a bundle."""
        content_ids = [test_content, str(uuid4())]

        bundle = await bundle_service.create_bundle(
            user_id=test_user,
            content_ids=content_ids,
            name="Test Bundle"
        )

        assert bundle is not None
        assert 'id' in bundle
        assert bundle['name'] == "Test Bundle"
        assert bundle['user_id'] == test_user

        # Parse content_ids
        bundle_content_ids = bundle['content_ids']
        if isinstance(bundle_content_ids, str):
            bundle_content_ids = json.loads(bundle_content_ids)
        assert len(bundle_content_ids) == 2

    async def test_create_bundle_without_name(self, bundle_service, test_content, test_user):
        """Test creating a bundle without a name."""
        content_ids = [test_content]

        bundle = await bundle_service.create_bundle(
            user_id=test_user,
            content_ids=content_ids
        )

        assert bundle is not None
        assert bundle['name'] is None
        assert bundle['user_id'] == test_user

    async def test_get_bundle_by_id(self, bundle_service, test_content, test_user):
        """Test retrieving bundle by ID."""
        # Create bundle
        content_ids = [test_content]
        created_bundle = await bundle_service.create_bundle(
            user_id=test_user,
            content_ids=content_ids,
            name="Get Test Bundle"
        )

        # Retrieve bundle
        bundle = await bundle_service.get_bundle_by_id(
            created_bundle['id'],
            test_user
        )

        assert bundle is not None
        assert bundle['id'] == created_bundle['id']
        assert bundle['name'] == "Get Test Bundle"

    async def test_get_bundle_by_id_unauthorized(self, bundle_service, test_content, test_user):
        """Test retrieving bundle with wrong user."""
        # Create bundle
        content_ids = [test_content]
        created_bundle = await bundle_service.create_bundle(
            user_id=test_user,
            content_ids=content_ids,
            name="Auth Test Bundle"
        )

        # Try to get with wrong user
        bundle = await bundle_service.get_bundle_by_id(
            created_bundle['id'],
            test_user + 999
        )

        assert bundle is None

    async def test_get_bundle_by_id_nonexistent(self, bundle_service, test_user):
        """Test retrieving non-existent bundle."""
        fake_id = str(uuid4())
        bundle = await bundle_service.get_bundle_by_id(fake_id, test_user)
        assert bundle is None

    async def test_get_user_bundles_pagination(self, bundle_service, test_content, test_user):
        """Test paginating user bundles."""
        # Create multiple bundles
        bundle_ids = []
        for i in range(5):
            bundle = await bundle_service.create_bundle(
                user_id=test_user,
                content_ids=[test_content],
                name=f"Bundle {i}"
            )
            bundle_ids.append(bundle['id'])

        # Get first page
        bundles, total = await bundle_service.get_user_bundles(
            test_user,
            limit=2,
            offset=0
        )

        assert total == 5
        assert len(bundles) == 2

        # Get second page
        bundles2, total2 = await bundle_service.get_user_bundles(
            test_user,
            limit=2,
            offset=2
        )

        assert total2 == 5
        assert len(bundles2) == 2

        # Ensure no overlap
        page1_ids = {b['id'] for b in bundles}
        page2_ids = {b['id'] for b in bundles2}
        assert page1_ids.isdisjoint(page2_ids)

    async def test_update_bundle_name(self, bundle_service, test_content, test_user):
        """Test updating bundle name."""
        # Create bundle
        bundle = await bundle_service.create_bundle(
            user_id=test_user,
            content_ids=[test_content],
            name="Original Name"
        )

        # Update name
        success = await bundle_service.update_bundle(
            bundle['id'],
            test_user,
            name="Updated Name"
        )

        assert success is True

        # Verify update
        updated = await bundle_service.get_bundle_by_id(bundle['id'], test_user)
        assert updated['name'] == "Updated Name"

    async def test_update_bundle_content_ids(self, bundle_service, test_content, test_user):
        """Test updating bundle content IDs."""
        # Create bundle
        bundle = await bundle_service.create_bundle(
            user_id=test_user,
            content_ids=[test_content],
            name="Content Update Bundle"
        )

        # Update content_ids
        new_content_ids = [test_content, str(uuid4()), str(uuid4())]
        success = await bundle_service.update_bundle(
            bundle['id'],
            test_user,
            content_ids=new_content_ids
        )

        assert success is True

        # Verify update
        updated = await bundle_service.get_bundle_by_id(bundle['id'], test_user)
        updated_ids = updated['content_ids']
        if isinstance(updated_ids, str):
            updated_ids = json.loads(updated_ids)
        assert len(updated_ids) == 3

    async def test_update_bundle_unauthorized(self, bundle_service, test_content, test_user):
        """Test updating bundle with wrong user."""
        # Create bundle
        bundle = await bundle_service.create_bundle(
            user_id=test_user,
            content_ids=[test_content],
            name="Auth Update Bundle"
        )

        # Try to update with wrong user
        success = await bundle_service.update_bundle(
            bundle['id'],
            test_user + 999,
            name="Hacked Name"
        )

        assert success is False

        # Verify unchanged
        unchanged = await bundle_service.get_bundle_by_id(bundle['id'], test_user)
        assert unchanged['name'] == "Auth Update Bundle"

    async def test_update_bundle_no_changes(self, bundle_service, test_content, test_user):
        """Test updating bundle with no actual changes."""
        # Create bundle
        bundle = await bundle_service.create_bundle(
            user_id=test_user,
            content_ids=[test_content],
            name="No Change Bundle"
        )

        # Update with no parameters
        success = await bundle_service.update_bundle(
            bundle['id'],
            test_user
        )

        assert success is True  # Should succeed even with no changes

    async def test_delete_bundle(self, bundle_service, test_content, test_user):
        """Test deleting a bundle."""
        # Create bundle
        bundle = await bundle_service.create_bundle(
            user_id=test_user,
            content_ids=[test_content],
            name="Delete Bundle"
        )

        # Delete
        success = await bundle_service.delete_bundle(bundle['id'], test_user)
        assert success is True

        # Verify deleted
        deleted = await bundle_service.get_bundle_by_id(bundle['id'], test_user)
        assert deleted is None

    async def test_delete_bundle_unauthorized(self, bundle_service, test_content, test_user):
        """Test deleting bundle with wrong user."""
        # Create bundle
        bundle = await bundle_service.create_bundle(
            user_id=test_user,
            content_ids=[test_content],
            name="Auth Delete Bundle"
        )

        # Try to delete with wrong user
        success = await bundle_service.delete_bundle(bundle['id'], test_user + 999)
        assert success is False

        # Verify still exists
        still_exists = await bundle_service.get_bundle_by_id(bundle['id'], test_user)
        assert still_exists is not None

    async def test_delete_bundle_nonexistent(self, bundle_service, test_user):
        """Test deleting non-existent bundle."""
        fake_id = str(uuid4())
        success = await bundle_service.delete_bundle(fake_id, test_user)
        assert success is False

    async def test_create_bundle_attempt(self, bundle_service, test_content, test_user):
        """Test creating a bundle attempt."""
        # Create bundle
        bundle = await bundle_service.create_bundle(
            user_id=test_user,
            content_ids=[test_content],
            name="Attempt Test Bundle"
        )

        # Create attempt
        attempt = await bundle_service.create_bundle_attempt(
            bundle_id=bundle['id'],
            processing_type="summary",
            output_language="en",
            system_prompt="System prompt text",
            user_prompt="User prompt text",
            combined_content_preview="Preview text",
            custom_instructions="Custom instructions"
        )

        assert attempt is not None
        assert attempt['bundle_id'] == bundle['id']
        assert attempt['attempt_number'] == 1
        assert attempt['processing_type'] == "summary"
        assert attempt['output_language'] == "en"
        assert attempt['system_prompt'] == "System prompt text"

    async def test_create_multiple_bundle_attempts(self, bundle_service, test_content, test_user):
        """Test creating multiple attempts for same bundle."""
        # Create bundle
        bundle = await bundle_service.create_bundle(
            user_id=test_user,
            content_ids=[test_content],
            name="Multiple Attempts Bundle"
        )

        # Create first attempt
        attempt1 = await bundle_service.create_bundle_attempt(
            bundle_id=bundle['id'],
            processing_type="summary",
            output_language="en",
            system_prompt="First system prompt"
        )

        # Create second attempt
        attempt2 = await bundle_service.create_bundle_attempt(
            bundle_id=bundle['id'],
            processing_type="mvp_plan",
            output_language="ru",
            system_prompt="Second system prompt"
        )

        # Create third attempt
        attempt3 = await bundle_service.create_bundle_attempt(
            bundle_id=bundle['id'],
            processing_type="content_ideas",
            output_language="es",
            system_prompt="Third system prompt"
        )

        # Verify attempt numbers are sequential
        assert attempt1['attempt_number'] == 1
        assert attempt2['attempt_number'] == 2
        assert attempt3['attempt_number'] == 3

    async def test_update_bundle_attempt_result(self, bundle_service, test_content, test_user):
        """Test updating bundle attempt with result path."""
        # Create bundle and attempt
        bundle = await bundle_service.create_bundle(
            user_id=test_user,
            content_ids=[test_content],
            name="Result Bundle"
        )

        attempt = await bundle_service.create_bundle_attempt(
            bundle_id=bundle['id'],
            processing_type="summary",
            output_language="en",
            system_prompt="System prompt"
        )

        # Update with result
        result_path = "/path/to/result.txt"
        success = await bundle_service.update_bundle_attempt_result(
            attempt['id'],
            result_path
        )

        assert success is True

        # Verify update
        updated = await bundle_service.get_bundle_attempt_by_id(attempt['id'], test_user)
        assert updated['result_path'] == result_path

    async def test_get_bundle_attempts(self, bundle_service, test_content, test_user):
        """Test retrieving all attempts for a bundle."""
        # Create bundle
        bundle = await bundle_service.create_bundle(
            user_id=test_user,
            content_ids=[test_content],
            name="Get Attempts Bundle"
        )

        # Create 3 attempts
        for i in range(3):
            await bundle_service.create_bundle_attempt(
                bundle_id=bundle['id'],
                processing_type="summary",
                output_language="en",
                system_prompt=f"Prompt {i}"
            )

        # Get all attempts
        attempts = await bundle_service.get_bundle_attempts(bundle['id'], test_user)

        assert len(attempts) == 3
        assert attempts[0]['attempt_number'] == 1
        assert attempts[1]['attempt_number'] == 2
        assert attempts[2]['attempt_number'] == 3

    async def test_get_bundle_attempts_unauthorized(self, bundle_service, test_content, test_user):
        """Test getting attempts with wrong user."""
        # Create bundle
        bundle = await bundle_service.create_bundle(
            user_id=test_user,
            content_ids=[test_content],
            name="Auth Attempts Bundle"
        )

        # Create attempt
        await bundle_service.create_bundle_attempt(
            bundle_id=bundle['id'],
            processing_type="summary",
            output_language="en",
            system_prompt="System prompt"
        )

        # Try to get with wrong user
        attempts = await bundle_service.get_bundle_attempts(bundle['id'], test_user + 999)

        assert len(attempts) == 0

    async def test_get_bundle_attempt_by_id(self, bundle_service, test_content, test_user):
        """Test retrieving specific bundle attempt by ID."""
        # Create bundle and attempt
        bundle = await bundle_service.create_bundle(
            user_id=test_user,
            content_ids=[test_content],
            name="Get Attempt Bundle"
        )

        created_attempt = await bundle_service.create_bundle_attempt(
            bundle_id=bundle['id'],
            processing_type="summary",
            output_language="en",
            system_prompt="System prompt"
        )

        # Retrieve attempt
        attempt = await bundle_service.get_bundle_attempt_by_id(
            created_attempt['id'],
            test_user
        )

        assert attempt is not None
        assert attempt['id'] == created_attempt['id']
        assert attempt['bundle_id'] == bundle['id']

    async def test_get_bundle_attempt_by_id_unauthorized(self, bundle_service, test_content, test_user):
        """Test getting attempt with wrong user."""
        # Create bundle and attempt
        bundle = await bundle_service.create_bundle(
            user_id=test_user,
            content_ids=[test_content],
            name="Auth Attempt Bundle"
        )

        attempt = await bundle_service.create_bundle_attempt(
            bundle_id=bundle['id'],
            processing_type="summary",
            output_language="en",
            system_prompt="System prompt"
        )

        # Try to get with wrong user
        result = await bundle_service.get_bundle_attempt_by_id(
            attempt['id'],
            test_user + 999
        )

        assert result is None

    async def test_get_bundle_attempt_diff(self, bundle_service, test_content, test_user):
        """Test getting diff between two attempts."""
        # Create bundle
        bundle = await bundle_service.create_bundle(
            user_id=test_user,
            content_ids=[test_content],
            name="Diff Bundle"
        )

        # Create two attempts with different parameters
        attempt1 = await bundle_service.create_bundle_attempt(
            bundle_id=bundle['id'],
            processing_type="summary",
            output_language="en",
            system_prompt="First prompt",
            custom_instructions="First instructions"
        )

        attempt2 = await bundle_service.create_bundle_attempt(
            bundle_id=bundle['id'],
            processing_type="mvp_plan",
            output_language="ru",
            system_prompt="Second prompt",
            custom_instructions="Second instructions"
        )

        # Get diff
        diff = await bundle_service.get_bundle_attempt_diff(
            attempt1['id'],
            attempt2['id'],
            test_user
        )

        assert diff is not None
        assert 'attempt_1' in diff
        assert 'attempt_2' in diff
        assert 'changes' in diff

        # Verify changes detected
        assert diff['changes']['processing_type_changed'] is True
        assert diff['changes']['language_changed'] is True
        assert diff['changes']['custom_instructions_changed'] is True
        assert diff['changes']['system_prompt_changed'] is True

    async def test_get_bundle_attempt_diff_same_bundle(self, bundle_service, test_content, test_user):
        """Test diff between attempts of same bundle."""
        # Create bundle
        bundle = await bundle_service.create_bundle(
            user_id=test_user,
            content_ids=[test_content],
            name="Same Bundle Diff"
        )

        # Create two attempts
        attempt1 = await bundle_service.create_bundle_attempt(
            bundle_id=bundle['id'],
            processing_type="summary",
            output_language="en",
            system_prompt="Same prompt"
        )

        attempt2 = await bundle_service.create_bundle_attempt(
            bundle_id=bundle['id'],
            processing_type="summary",
            output_language="en",
            system_prompt="Same prompt"
        )

        # Get diff
        diff = await bundle_service.get_bundle_attempt_diff(
            attempt1['id'],
            attempt2['id'],
            test_user
        )

        assert diff is not None
        # No changes detected
        assert diff['changes']['processing_type_changed'] is False
        assert diff['changes']['language_changed'] is False
        assert diff['changes']['system_prompt_changed'] is False

    async def test_get_bundle_attempt_diff_different_bundles(self, bundle_service, test_content, test_user):
        """Test diff between attempts of different bundles fails."""
        # Create two bundles
        bundle1 = await bundle_service.create_bundle(
            user_id=test_user,
            content_ids=[test_content],
            name="Bundle 1"
        )

        bundle2 = await bundle_service.create_bundle(
            user_id=test_user,
            content_ids=[test_content],
            name="Bundle 2"
        )

        # Create attempts for each
        attempt1 = await bundle_service.create_bundle_attempt(
            bundle_id=bundle1['id'],
            processing_type="summary",
            output_language="en",
            system_prompt="Prompt 1"
        )

        attempt2 = await bundle_service.create_bundle_attempt(
            bundle_id=bundle2['id'],
            processing_type="summary",
            output_language="en",
            system_prompt="Prompt 2"
        )

        # Try to get diff (should fail)
        diff = await bundle_service.get_bundle_attempt_diff(
            attempt1['id'],
            attempt2['id'],
            test_user
        )

        assert diff is None

    async def test_get_bundle_with_details(self, bundle_service, test_content, test_user):
        """Test getting bundle with content details and attempt count."""
        # Create bundle
        bundle = await bundle_service.create_bundle(
            user_id=test_user,
            content_ids=[test_content],
            name="Details Bundle"
        )

        # Create attempts
        for i in range(3):
            await bundle_service.create_bundle_attempt(
                bundle_id=bundle['id'],
                processing_type="summary",
                output_language="en",
                system_prompt=f"Prompt {i}"
            )

        # Get with details
        detailed = await bundle_service.get_bundle_with_details(bundle['id'], test_user)

        assert detailed is not None
        assert 'attempt_count' in detailed
        assert detailed['attempt_count'] == 3
        assert 'content_items' in detailed
        assert len(detailed['content_items']) >= 1

    async def test_empty_user_bundles_list(self, bundle_service, db_manager):
        """Test getting bundles for user with no bundles."""
        # Create user with no bundles
        async with db_manager.session() as session:
            from sqlalchemy import text
            result = await session.execute(
                text("""
                    INSERT INTO users (id, email, hashed_password, is_active, created_at, updated_at)
                    VALUES (777, 'nobundles@example.com', 'hashed', TRUE, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                    RETURNING id
                """)
            )
            await session.commit()

        bundles, total = await bundle_service.get_user_bundles(777, limit=20, offset=0)

        assert total == 0
        assert len(bundles) == 0

    async def test_bundle_cascade_delete_attempts(self, bundle_service, test_content, test_user):
        """Test that deleting bundle cascades to delete attempts."""
        # Create bundle
        bundle = await bundle_service.create_bundle(
            user_id=test_user,
            content_ids=[test_content],
            name="Cascade Bundle"
        )

        # Create attempt
        attempt = await bundle_service.create_bundle_attempt(
            bundle_id=bundle['id'],
            processing_type="summary",
            output_language="en",
            system_prompt="System prompt"
        )

        # Delete bundle
        success = await bundle_service.delete_bundle(bundle['id'], test_user)
        assert success is True

        # Verify attempt is also deleted
        deleted_attempt = await bundle_service.get_bundle_attempt_by_id(
            attempt['id'],
            test_user
        )
        assert deleted_attempt is None

    async def test_bundle_timestamps(self, bundle_service, test_content, test_user):
        """Test that bundle timestamps are set correctly."""
        bundle = await bundle_service.create_bundle(
            user_id=test_user,
            content_ids=[test_content],
            name="Timestamp Bundle"
        )

        assert 'created_at' in bundle
        assert 'updated_at' in bundle
        assert bundle['created_at'] is not None
        assert bundle['updated_at'] is not None

    async def test_bundle_attempt_timestamps(self, bundle_service, test_content, test_user):
        """Test that bundle attempt timestamps are set correctly."""
        # Create bundle
        bundle = await bundle_service.create_bundle(
            user_id=test_user,
            content_ids=[test_content],
            name="Timestamp Attempt Bundle"
        )

        # Create attempt
        attempt = await bundle_service.create_bundle_attempt(
            bundle_id=bundle['id'],
            processing_type="summary",
            output_language="en",
            system_prompt="System prompt"
        )

        assert 'created_at' in attempt
        assert attempt['created_at'] is not None
