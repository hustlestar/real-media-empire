"""Bundle service for managing content bundles and processing attempts."""

import logging
import json
from typing import Optional, Dict, Any, List, Tuple
from uuid import UUID
from datetime import datetime

logger = logging.getLogger(__name__)


class BundleService:
    """Service for bundle and bundle attempt management."""

    def __init__(self, database):
        """Initialize bundle service.

        Args:
            database: DatabaseManager instance
        """
        self.db = database

    # Bundle CRUD Operations

    async def create_bundle(
        self,
        user_id: int,
        content_ids: List[UUID],
        name: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create a new bundle.

        Args:
            user_id: User ID
            content_ids: List of content UUIDs to include in bundle
            name: Optional bundle name

        Returns:
            Bundle dict
        """
        async with self.db._pool.acquire() as conn:
            row = await conn.fetchrow(
                """
                INSERT INTO bundles (user_id, name, content_ids, created_at, updated_at)
                VALUES ($1, $2, $3, NOW(), NOW())
                RETURNING *
                """,
                user_id,
                name,
                content_ids
            )
            bundle = dict(row)
            logger.info(f"Created bundle {bundle['id']} with {len(content_ids)} content items")
            return bundle

    async def get_bundle_by_id(
        self,
        bundle_id: UUID,
        user_id: int
    ) -> Optional[Dict[str, Any]]:
        """Get bundle by ID.

        Args:
            bundle_id: Bundle UUID
            user_id: User ID (for authorization)

        Returns:
            Bundle dict or None
        """
        async with self.db._pool.acquire() as conn:
            row = await conn.fetchrow(
                """
                SELECT * FROM bundles
                WHERE id = $1 AND user_id = $2
                """,
                bundle_id,
                user_id
            )
            return dict(row) if row else None

    async def get_user_bundles(
        self,
        user_id: int,
        limit: int = 20,
        offset: int = 0
    ) -> Tuple[List[Dict[str, Any]], int]:
        """Get user's bundles with pagination.

        Args:
            user_id: User ID
            limit: Max items to return
            offset: Offset for pagination

        Returns:
            Tuple of (bundles list, total count)
        """
        async with self.db._pool.acquire() as conn:
            # Get bundles
            rows = await conn.fetch(
                """
                SELECT * FROM bundles
                WHERE user_id = $1
                ORDER BY created_at DESC
                LIMIT $2 OFFSET $3
                """,
                user_id,
                limit,
                offset
            )
            bundles = [dict(row) for row in rows]

            # Get total count
            total = await conn.fetchval(
                "SELECT COUNT(*) FROM bundles WHERE user_id = $1",
                user_id
            )

            return bundles, total

    async def update_bundle(
        self,
        bundle_id: UUID,
        user_id: int,
        name: Optional[str] = None,
        content_ids: Optional[List[UUID]] = None
    ) -> bool:
        """Update bundle.

        Args:
            bundle_id: Bundle UUID
            user_id: User ID (for authorization)
            name: Optional new name
            content_ids: Optional new content IDs list

        Returns:
            True if updated, False if not found
        """
        updates = []
        params = []
        param_idx = 1

        if name is not None:
            updates.append(f"name = ${param_idx}")
            params.append(name)
            param_idx += 1

        if content_ids is not None:
            updates.append(f"content_ids = ${param_idx}")
            params.append(content_ids)
            param_idx += 1

        if not updates:
            return True  # Nothing to update

        updates.append(f"updated_at = NOW()")
        params.extend([bundle_id, user_id])

        query = f"""
            UPDATE bundles
            SET {', '.join(updates)}
            WHERE id = ${param_idx} AND user_id = ${param_idx + 1}
        """

        async with self.db._pool.acquire() as conn:
            result = await conn.execute(query, *params)
            updated = result.split()[-1] == "1"
            if updated:
                logger.info(f"Updated bundle {bundle_id}")
            return updated

    async def delete_bundle(
        self,
        bundle_id: UUID,
        user_id: int
    ) -> bool:
        """Delete bundle and associated attempts.

        Args:
            bundle_id: Bundle UUID
            user_id: User ID (for authorization)

        Returns:
            True if deleted, False if not found
        """
        async with self.db._pool.acquire() as conn:
            result = await conn.execute(
                """
                DELETE FROM bundles
                WHERE id = $1 AND user_id = $2
                """,
                bundle_id,
                user_id
            )
            deleted = result.split()[-1] == "1"
            if deleted:
                logger.info(f"Deleted bundle {bundle_id}")
            return deleted

    # Bundle Attempt Operations

    async def create_bundle_attempt(
        self,
        bundle_id: UUID,
        processing_type: str,
        output_language: str,
        system_prompt: str,
        user_prompt: Optional[str] = None,
        combined_content_preview: Optional[str] = None,
        custom_instructions: Optional[str] = None,
        job_id: Optional[UUID] = None
    ) -> Dict[str, Any]:
        """Create a bundle processing attempt.

        Args:
            bundle_id: Bundle UUID
            processing_type: Type of processing (summary/mvp_plan/content_ideas)
            output_language: Output language code
            system_prompt: Full system prompt used
            user_prompt: User prompt template
            combined_content_preview: Preview of combined content
            custom_instructions: Custom user instructions
            job_id: Associated job ID

        Returns:
            Bundle attempt dict
        """
        async with self.db._pool.acquire() as conn:
            # Get next attempt number for this bundle
            attempt_number = await conn.fetchval(
                """
                SELECT COALESCE(MAX(attempt_number), 0) + 1
                FROM bundle_attempts
                WHERE bundle_id = $1
                """,
                bundle_id
            )

            # Create attempt
            row = await conn.fetchrow(
                """
                INSERT INTO bundle_attempts (
                    bundle_id, attempt_number, processing_type, output_language,
                    system_prompt, user_prompt, combined_content_preview,
                    custom_instructions, job_id, created_at
                )
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, NOW())
                RETURNING *
                """,
                bundle_id,
                attempt_number,
                processing_type,
                output_language,
                system_prompt,
                user_prompt,
                combined_content_preview,
                custom_instructions,
                job_id
            )
            attempt = dict(row)
            logger.info(f"Created bundle attempt #{attempt_number} for bundle {bundle_id}")
            return attempt

    async def update_bundle_attempt_result(
        self,
        attempt_id: UUID,
        result_path: str
    ) -> bool:
        """Update bundle attempt with result path.

        Args:
            attempt_id: Attempt UUID
            result_path: Path to result file

        Returns:
            True if updated, False if not found
        """
        async with self.db._pool.acquire() as conn:
            result = await conn.execute(
                """
                UPDATE bundle_attempts
                SET result_path = $1
                WHERE id = $2
                """,
                result_path,
                attempt_id
            )
            updated = result.split()[-1] == "1"
            if updated:
                logger.info(f"Updated bundle attempt {attempt_id} with result")
            return updated

    async def get_bundle_attempts(
        self,
        bundle_id: UUID,
        user_id: int
    ) -> List[Dict[str, Any]]:
        """Get all attempts for a bundle.

        Args:
            bundle_id: Bundle UUID
            user_id: User ID (for authorization)

        Returns:
            List of bundle attempt dicts
        """
        async with self.db._pool.acquire() as conn:
            # Verify bundle belongs to user
            bundle = await conn.fetchrow(
                "SELECT id FROM bundles WHERE id = $1 AND user_id = $2",
                bundle_id,
                user_id
            )
            if not bundle:
                return []

            # Get attempts
            rows = await conn.fetch(
                """
                SELECT * FROM bundle_attempts
                WHERE bundle_id = $1
                ORDER BY attempt_number ASC
                """,
                bundle_id
            )
            return [dict(row) for row in rows]

    async def get_bundle_attempt_by_id(
        self,
        attempt_id: UUID,
        user_id: int
    ) -> Optional[Dict[str, Any]]:
        """Get bundle attempt by ID.

        Args:
            attempt_id: Attempt UUID
            user_id: User ID (for authorization)

        Returns:
            Bundle attempt dict or None
        """
        async with self.db._pool.acquire() as conn:
            row = await conn.fetchrow(
                """
                SELECT ba.* FROM bundle_attempts ba
                JOIN bundles b ON ba.bundle_id = b.id
                WHERE ba.id = $1 AND b.user_id = $2
                """,
                attempt_id,
                user_id
            )
            return dict(row) if row else None

    async def get_bundle_attempt_diff(
        self,
        attempt_id_1: UUID,
        attempt_id_2: UUID,
        user_id: int
    ) -> Optional[Dict[str, Any]]:
        """Get diff between two bundle attempts.

        Args:
            attempt_id_1: First attempt UUID
            attempt_id_2: Second attempt UUID
            user_id: User ID (for authorization)

        Returns:
            Dict with diff information or None if not authorized
        """
        # Get both attempts
        attempt1 = await self.get_bundle_attempt_by_id(attempt_id_1, user_id)
        attempt2 = await self.get_bundle_attempt_by_id(attempt_id_2, user_id)

        if not attempt1 or not attempt2:
            return None

        # Verify both attempts belong to same bundle
        if attempt1['bundle_id'] != attempt2['bundle_id']:
            logger.warning(f"Attempts {attempt_id_1} and {attempt_id_2} belong to different bundles")
            return None

        # Calculate diff
        diff = {
            "attempt_1": {
                "id": str(attempt1['id']),
                "attempt_number": attempt1['attempt_number'],
                "processing_type": attempt1['processing_type'],
                "output_language": attempt1['output_language'],
                "custom_instructions": attempt1['custom_instructions'],
                "created_at": attempt1['created_at'].isoformat()
            },
            "attempt_2": {
                "id": str(attempt2['id']),
                "attempt_number": attempt2['attempt_number'],
                "processing_type": attempt2['processing_type'],
                "output_language": attempt2['output_language'],
                "custom_instructions": attempt2['custom_instructions'],
                "created_at": attempt2['created_at'].isoformat()
            },
            "changes": {
                "processing_type_changed": attempt1['processing_type'] != attempt2['processing_type'],
                "language_changed": attempt1['output_language'] != attempt2['output_language'],
                "custom_instructions_changed": attempt1['custom_instructions'] != attempt2['custom_instructions'],
                "system_prompt_changed": attempt1['system_prompt'] != attempt2['system_prompt']
            }
        }

        return diff

    async def get_bundle_with_details(
        self,
        bundle_id: UUID,
        user_id: int
    ) -> Optional[Dict[str, Any]]:
        """Get bundle with content items and attempt count.

        Args:
            bundle_id: Bundle UUID
            user_id: User ID (for authorization)

        Returns:
            Bundle dict with additional details or None
        """
        bundle = await self.get_bundle_by_id(bundle_id, user_id)
        if not bundle:
            return None

        async with self.db._pool.acquire() as conn:
            # Get attempt count
            attempt_count = await conn.fetchval(
                "SELECT COUNT(*) FROM bundle_attempts WHERE bundle_id = $1",
                bundle_id
            )

            # Get content items details
            content_rows = await conn.fetch(
                """
                SELECT id, source_type, metadata
                FROM content_items
                WHERE id = ANY($1)
                """,
                bundle['content_ids']
            )
            content_items = []
            for row in content_rows:
                item = dict(row)
                # Parse metadata JSON
                if isinstance(item.get('metadata'), str):
                    try:
                        item['metadata'] = json.loads(item['metadata']) if item['metadata'] else {}
                    except json.JSONDecodeError:
                        item['metadata'] = {}
                content_items.append(item)

            bundle['attempt_count'] = attempt_count
            bundle['content_items'] = content_items

        return bundle
