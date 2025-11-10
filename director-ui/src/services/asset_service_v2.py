"""Asset service for V2 schema - universal asset management.

This service provides CRUD operations for the new asset-centric schema,
treating everything (scripts, text, audio, video, images, shots, films) as assets.
"""

import logging
from typing import List, Optional, Dict, Any
from uuid import UUID, uuid4
from datetime import datetime

from ..data.models_v2 import AssetV2, AssetRelationship, AssetCollection, AssetCollectionMember
from ..core.database import DatabaseConnection

logger = logging.getLogger(__name__)


class AssetServiceV2:
    """Service for managing universal assets."""

    def __init__(self, db: DatabaseConnection):
        self.db = db

    async def create_asset(
        self,
        workspace_id: str,
        asset_type: str,
        name: str,
        url: Optional[str] = None,
        file_path: Optional[str] = None,
        size: Optional[int] = None,
        duration: Optional[float] = None,
        metadata: Optional[Dict[str, Any]] = None,
        tags: Optional[List[str]] = None,
        source: Optional[str] = None,
        generation_cost: Optional[float] = None,
        generation_metadata: Optional[Dict[str, Any]] = None,
    ) -> UUID:
        """Create a new asset.

        Args:
            workspace_id: Workspace UUID
            asset_type: Asset type (script, text, audio, video, image, shot, film, character_ref, scene)
            name: Asset name
            url: Public CDN URL
            file_path: Local filesystem path
            size: File size in bytes
            duration: Duration for audio/video
            metadata: Type-specific metadata
            tags: Asset tags
            source: Source (upload, generation, import, derivative)
            generation_cost: Cost to generate
            generation_metadata: Generation details

        Returns:
            UUID of created asset
        """
        asset_id = str(uuid4())

        query = """
            INSERT INTO assets_v2 (
                id, workspace_id, type, name, url, file_path, size, duration,
                metadata, tags, source, generation_cost, generation_metadata,
                created_at, updated_at
            ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, NOW(), NOW())
            RETURNING id
        """

        async with self.db._pool.acquire() as conn:
            result = await conn.fetchval(
                query,
                asset_id,
                workspace_id,
                asset_type,
                name,
                url,
                file_path,
                size,
                duration,
                metadata or {},
                tags or [],
                source,
                generation_cost,
                generation_metadata,
            )

        logger.info(f"Created asset: {asset_id} (type={asset_type}, name={name})")
        return UUID(result)

    async def get_asset(self, asset_id: UUID) -> Optional[Dict[str, Any]]:
        """Get asset by ID.

        Args:
            asset_id: Asset UUID

        Returns:
            Asset data or None if not found
        """
        query = """
            SELECT * FROM assets_v2 WHERE id = $1
        """

        async with self.db._pool.acquire() as conn:
            row = await conn.fetchrow(query, str(asset_id))

        return dict(row) if row else None

    async def list_assets(
        self,
        workspace_id: str,
        asset_type: Optional[str] = None,
        tags: Optional[List[str]] = None,
        source: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[Dict[str, Any]]:
        """List assets with filters.

        Args:
            workspace_id: Workspace UUID
            asset_type: Filter by asset type
            tags: Filter by tags (assets must have all specified tags)
            source: Filter by source
            limit: Max results
            offset: Results offset

        Returns:
            List of asset data
        """
        conditions = ["workspace_id = $1"]
        params = [workspace_id]
        param_count = 1

        if asset_type:
            param_count += 1
            conditions.append(f"type = ${param_count}")
            params.append(asset_type)

        if tags:
            param_count += 1
            conditions.append(f"tags @> ${param_count}")
            params.append(tags)

        if source:
            param_count += 1
            conditions.append(f"source = ${param_count}")
            params.append(source)

        where_clause = " AND ".join(conditions)
        query = f"""
            SELECT * FROM assets_v2
            WHERE {where_clause}
            ORDER BY created_at DESC
            LIMIT ${param_count + 1} OFFSET ${param_count + 2}
        """
        params.extend([limit, offset])

        async with self.db._pool.acquire() as conn:
            rows = await conn.fetch(query, *params)

        return [dict(row) for row in rows]

    async def update_asset(
        self,
        asset_id: UUID,
        name: Optional[str] = None,
        url: Optional[str] = None,
        file_path: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        tags: Optional[List[str]] = None,
    ) -> bool:
        """Update asset fields.

        Args:
            asset_id: Asset UUID
            name: New name
            url: New URL
            file_path: New file path
            metadata: Updated metadata (merged with existing)
            tags: Updated tags (replaces existing)

        Returns:
            True if updated, False if not found
        """
        updates = []
        params = []
        param_count = 0

        if name is not None:
            param_count += 1
            updates.append(f"name = ${param_count}")
            params.append(name)

        if url is not None:
            param_count += 1
            updates.append(f"url = ${param_count}")
            params.append(url)

        if file_path is not None:
            param_count += 1
            updates.append(f"file_path = ${param_count}")
            params.append(file_path)

        if metadata is not None:
            param_count += 1
            updates.append(f"metadata = metadata || ${param_count}::jsonb")
            params.append(metadata)

        if tags is not None:
            param_count += 1
            updates.append(f"tags = ${param_count}")
            params.append(tags)

        if not updates:
            return False

        updates.append("updated_at = NOW()")
        param_count += 1
        params.append(str(asset_id))

        query = f"""
            UPDATE assets_v2
            SET {', '.join(updates)}
            WHERE id = ${param_count}
            RETURNING id
        """

        async with self.db._pool.acquire() as conn:
            result = await conn.fetchval(query, *params)

        logger.info(f"Updated asset: {asset_id}")
        return result is not None

    async def delete_asset(self, asset_id: UUID) -> bool:
        """Delete asset by ID.

        Args:
            asset_id: Asset UUID

        Returns:
            True if deleted, False if not found
        """
        query = "DELETE FROM assets_v2 WHERE id = $1 RETURNING id"

        async with self.db._pool.acquire() as conn:
            result = await conn.fetchval(query, str(asset_id))

        if result:
            logger.info(f"Deleted asset: {asset_id}")
            return True
        return False

    async def create_relationship(
        self,
        parent_asset_id: UUID,
        child_asset_id: UUID,
        relationship_type: str,
        sequence: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> UUID:
        """Create relationship between assets.

        Args:
            parent_asset_id: Parent asset UUID
            child_asset_id: Child asset UUID
            relationship_type: Relationship type (used_in, derived_from, part_of, etc.)
            sequence: Optional sequence order
            metadata: Relationship-specific metadata

        Returns:
            Relationship UUID
        """
        rel_id = str(uuid4())

        query = """
            INSERT INTO asset_relationships (
                id, parent_asset_id, child_asset_id, relationship_type,
                sequence, metadata, created_at
            ) VALUES ($1, $2, $3, $4, $5, $6, NOW())
            RETURNING id
        """

        async with self.db._pool.acquire() as conn:
            result = await conn.fetchval(
                query,
                rel_id,
                str(parent_asset_id),
                str(child_asset_id),
                relationship_type,
                sequence,
                metadata or {},
            )

        logger.info(
            f"Created relationship: {parent_asset_id} --[{relationship_type}]--> {child_asset_id}"
        )
        return UUID(result)

    async def get_child_assets(
        self,
        parent_asset_id: UUID,
        relationship_type: Optional[str] = None,
        asset_type: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Get child assets linked to parent.

        Args:
            parent_asset_id: Parent asset UUID
            relationship_type: Filter by relationship type
            asset_type: Filter by child asset type

        Returns:
            List of child assets with relationship data
        """
        conditions = ["r.parent_asset_id = $1"]
        params = [str(parent_asset_id)]
        param_count = 1

        if relationship_type:
            param_count += 1
            conditions.append(f"r.relationship_type = ${param_count}")
            params.append(relationship_type)

        if asset_type:
            param_count += 1
            conditions.append(f"a.type = ${param_count}")
            params.append(asset_type)

        where_clause = " AND ".join(conditions)
        query = f"""
            SELECT a.*, r.relationship_type, r.sequence, r.metadata as rel_metadata
            FROM assets_v2 a
            JOIN asset_relationships r ON r.child_asset_id = a.id
            WHERE {where_clause}
            ORDER BY r.sequence NULLS LAST, a.created_at
        """

        async with self.db._pool.acquire() as conn:
            rows = await conn.fetch(query, *params)

        return [dict(row) for row in rows]

    async def get_parent_assets(
        self,
        child_asset_id: UUID,
        relationship_type: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Get parent assets linked to child.

        Args:
            child_asset_id: Child asset UUID
            relationship_type: Filter by relationship type

        Returns:
            List of parent assets with relationship data
        """
        conditions = ["r.child_asset_id = $1"]
        params = [str(child_asset_id)]

        if relationship_type:
            conditions.append("r.relationship_type = $2")
            params.append(relationship_type)

        where_clause = " AND ".join(conditions)
        query = f"""
            SELECT a.*, r.relationship_type, r.sequence, r.metadata as rel_metadata
            FROM assets_v2 a
            JOIN asset_relationships r ON r.parent_asset_id = a.id
            WHERE {where_clause}
            ORDER BY a.created_at
        """

        async with self.db._pool.acquire() as conn:
            rows = await conn.fetch(query, *params)

        return [dict(row) for row in rows]

    async def create_collection(
        self,
        workspace_id: str,
        name: str,
        collection_type: str,
        description: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> UUID:
        """Create asset collection.

        Args:
            workspace_id: Workspace UUID
            name: Collection name
            collection_type: Collection type (project, character, storyboard, library)
            description: Collection description
            metadata: Collection metadata

        Returns:
            Collection UUID
        """
        collection_id = str(uuid4())

        query = """
            INSERT INTO asset_collections (
                id, workspace_id, name, type, description, metadata,
                created_at, updated_at
            ) VALUES ($1, $2, $3, $4, $5, $6, NOW(), NOW())
            RETURNING id
        """

        async with self.db._pool.acquire() as conn:
            result = await conn.fetchval(
                query,
                collection_id,
                workspace_id,
                name,
                collection_type,
                description,
                metadata or {},
            )

        logger.info(f"Created collection: {collection_id} (type={collection_type}, name={name})")
        return UUID(result)

    async def add_asset_to_collection(
        self,
        collection_id: UUID,
        asset_id: UUID,
        sequence: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> UUID:
        """Add asset to collection.

        Args:
            collection_id: Collection UUID
            asset_id: Asset UUID
            sequence: Position in collection
            metadata: Member-specific metadata

        Returns:
            Membership UUID
        """
        member_id = str(uuid4())

        query = """
            INSERT INTO asset_collection_members (
                id, collection_id, asset_id, sequence, metadata, created_at
            ) VALUES ($1, $2, $3, $4, $5, NOW())
            RETURNING id
        """

        async with self.db._pool.acquire() as conn:
            result = await conn.fetchval(
                query,
                member_id,
                str(collection_id),
                str(asset_id),
                sequence,
                metadata or {},
            )

        logger.info(f"Added asset {asset_id} to collection {collection_id}")
        return UUID(result)

    async def get_collection_assets(
        self,
        collection_id: UUID,
        asset_type: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Get all assets in collection.

        Args:
            collection_id: Collection UUID
            asset_type: Filter by asset type

        Returns:
            List of assets with membership data
        """
        conditions = ["m.collection_id = $1"]
        params = [str(collection_id)]

        if asset_type:
            conditions.append("a.type = $2")
            params.append(asset_type)

        where_clause = " AND ".join(conditions)
        query = f"""
            SELECT a.*, m.sequence, m.metadata as member_metadata
            FROM assets_v2 a
            JOIN asset_collection_members m ON m.asset_id = a.id
            WHERE {where_clause}
            ORDER BY m.sequence NULLS LAST, a.created_at
        """

        async with self.db._pool.acquire() as conn:
            rows = await conn.fetch(query, *params)

        return [dict(row) for row in rows]
