"""Tag service for managing content tags."""

import logging
from typing import List, Dict, Any, Optional
from uuid import UUID

logger = logging.getLogger(__name__)


class TagService:
    """Service for managing tags and content-tag relationships."""

    def __init__(self, database):
        """Initialize tag service.

        Args:
            database: DatabaseManager instance
        """
        self.db = database

    async def get_all_tags(self) -> List[Dict[str, Any]]:
        """Get all tags with usage counts.

        Returns:
            List of tag dictionaries with id, name, created_at, and usage_count
        """
        async with self.db._pool.acquire() as conn:
            rows = await conn.fetch(
                """
                SELECT
                    t.id,
                    t.name,
                    t.created_at,
                    COUNT(ct.content_id) as usage_count
                FROM tags t
                LEFT JOIN content_tags ct ON t.id = ct.tag_id
                GROUP BY t.id, t.name, t.created_at
                ORDER BY usage_count DESC, t.name ASC
                """
            )
            return [dict(row) for row in rows]

    async def get_or_create_tags(self, tag_names: List[str]) -> List[UUID]:
        """Ensure tags exist and return their IDs.

        Args:
            tag_names: List of tag names

        Returns:
            List of tag UUIDs
        """
        if not tag_names:
            return []

        # Normalize tag names (lowercase, strip whitespace)
        normalized_names = [name.strip().lower() for name in tag_names if name.strip()]
        if not normalized_names:
            return []

        tag_ids = []
        async with self.db._pool.acquire() as conn:
            for name in normalized_names:
                # Try to get existing tag
                row = await conn.fetchrow(
                    "SELECT id FROM tags WHERE name = $1",
                    name
                )

                if row:
                    tag_ids.append(row['id'])
                else:
                    # Create new tag
                    row = await conn.fetchrow(
                        """
                        INSERT INTO tags (name, created_at)
                        VALUES ($1, NOW())
                        ON CONFLICT (name) DO UPDATE SET name = EXCLUDED.name
                        RETURNING id
                        """,
                        name
                    )
                    tag_ids.append(row['id'])
                    logger.info(f"Created new tag: {name}")

        return tag_ids

    async def link_tags_to_content(self, content_id: UUID, tag_ids: List[UUID], conn=None) -> None:
        """Link tags to content item.

        Args:
            content_id: Content UUID
            tag_ids: List of tag UUIDs to link
            conn: Optional database connection (for transaction support)
        """
        if not tag_ids:
            return

        async def _do_link(conn):
            # Delete existing tags for this content
            await conn.execute(
                "DELETE FROM content_tags WHERE content_id = $1",
                content_id
            )

            # Insert new tag links
            for tag_id in tag_ids:
                await conn.execute(
                    """
                    INSERT INTO content_tags (content_id, tag_id, created_at)
                    VALUES ($1, $2, NOW())
                    ON CONFLICT DO NOTHING
                    """,
                    content_id,
                    tag_id
                )

        if conn:
            # Use provided connection (transaction support)
            await _do_link(conn)
        else:
            # Acquire own connection
            async with self.db._pool.acquire() as conn:
                await _do_link(conn)

        logger.info(f"Linked {len(tag_ids)} tags to content {content_id}")

    async def get_content_tags(self, content_id: UUID) -> List[str]:
        """Get tag names for a content item.

        Args:
            content_id: Content UUID

        Returns:
            List of tag names
        """
        async with self.db._pool.acquire() as conn:
            rows = await conn.fetch(
                """
                SELECT t.name
                FROM tags t
                JOIN content_tags ct ON t.id = ct.tag_id
                WHERE ct.content_id = $1
                ORDER BY t.name ASC
                """,
                content_id
            )
            return [row['name'] for row in rows]

    async def get_content_by_tags(
        self,
        tag_names: List[str],
        user_id: Optional[int] = None,
        limit: int = 20,
        offset: int = 0
    ) -> tuple[List[UUID], int]:
        """Get content IDs that have all specified tags.

        Args:
            tag_names: List of tag names (all must match)
            user_id: Optional user ID filter
            limit: Page size
            offset: Page offset

        Returns:
            Tuple of (content_ids, total_count)
        """
        if not tag_names:
            return [], 0

        # Normalize tag names
        normalized_names = [name.strip().lower() for name in tag_names if name.strip()]
        if not normalized_names:
            return [], 0

        async with self.db._pool.acquire() as conn:
            # Build query with tag filtering
            where_clauses = ["t.name = ANY($1)"]
            params = [normalized_names]

            if user_id is not None:
                where_clauses.append(f"ci.user_id = ${len(params) + 1}")
                params.append(user_id)

            where_clause = " AND ".join(where_clauses)

            # Get content IDs that have ALL specified tags
            count_query = f"""
                SELECT COUNT(DISTINCT ci.id)
                FROM content_items ci
                JOIN content_tags ct ON ci.id = ct.content_id
                JOIN tags t ON ct.tag_id = t.id
                WHERE {where_clause}
                GROUP BY ci.id
                HAVING COUNT(DISTINCT t.name) = ${len(params) + 1}
            """
            params.append(len(normalized_names))

            total = await conn.fetchval(count_query, *params) or 0

            # Get content IDs
            items_query = f"""
                SELECT ci.id
                FROM content_items ci
                JOIN content_tags ct ON ci.id = ct.content_id
                JOIN tags t ON ct.tag_id = t.id
                WHERE {where_clause}
                GROUP BY ci.id
                HAVING COUNT(DISTINCT t.name) = ${len(params) + 1}
                ORDER BY ci.created_at DESC
                LIMIT ${len(params) + 2} OFFSET ${len(params) + 3}
            """
            params.extend([limit, offset])

            rows = await conn.fetch(items_query, *params)
            content_ids = [row['id'] for row in rows]

            return content_ids, total

    async def get_tag_by_name(self, tag_name: str) -> Optional[Dict[str, Any]]:
        """Get tag by name.

        Args:
            tag_name: Tag name

        Returns:
            Tag dict or None
        """
        normalized_name = tag_name.strip().lower()
        async with self.db._pool.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT id, name, created_at FROM tags WHERE name = $1",
                normalized_name
            )
            return dict(row) if row else None
