"""Universal asset service - everything is an asset.

This service manages all assets (scripts, text, audio, video, images, shots, films, characters)
using a single unified interface with type-specific helper methods.
"""

import logging
from typing import List, Optional, Dict, Any
from uuid import UUID, uuid4
from datetime import datetime

from core.database import DatabaseManager

logger = logging.getLogger(__name__)


class AssetService:
    """Universal asset management service.

    Handles all asset types with a unified interface:
    - Core CRUD: create, get, update, delete
    - Relationships: link assets together (shot → character, film → shot, etc.)
    - Collections: group assets for organization
    - Type-specific helpers: for common operations on specific asset types
    """

    def __init__(self, db: DatabaseManager):
        self.db = db

    # ========================================================================
    # CORE CRUD OPERATIONS
    # ========================================================================

    async def create_asset(
        self,
        workspace_id: Optional[str],
        asset_type: str,
        name: str,
        url: Optional[str] = None,
        file_path: Optional[str] = None,
        size: Optional[int] = None,
        duration: Optional[float] = None,
        asset_metadata: Optional[Dict[str, Any]] = None,
        tags: Optional[List[str]] = None,
        source: Optional[str] = None,
        generation_cost: Optional[float] = None,
        generation_metadata: Optional[Dict[str, Any]] = None,
    ) -> UUID:
        """Create a new asset.

        Args:
            workspace_id: Workspace UUID (optional for global assets)
            asset_type: Asset type (script, text, audio, video, image, shot, shot_take, film, character_ref, scene)
            name: Asset name
            url: Public CDN URL
            file_path: Local filesystem path
            size: File size in bytes
            duration: Duration for audio/video
            asset_metadata: Type-specific metadata (JSONB)
            tags: Asset tags array
            source: Source (upload, generation, import, derivative)
            generation_cost: Cost to generate
            generation_metadata: Generation details (provider, model, prompt, seed)

        Returns:
            UUID of created asset
        """
        asset_id = str(uuid4())

        query = """
            INSERT INTO assets (
                id, workspace_id, type, name, url, file_path, size, duration,
                asset_metadata, tags, source, generation_cost, generation_metadata,
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
                asset_metadata or {},
                tags or [],
                source,
                generation_cost,
                generation_metadata,
            )

        logger.info(f"✓ Created asset: {asset_id} (type={asset_type}, name={name})")
        return UUID(result)

    async def get_asset(self, asset_id: UUID) -> Optional[Dict[str, Any]]:
        """Get asset by ID.

        Args:
            asset_id: Asset UUID

        Returns:
            Asset data or None if not found
        """
        query = "SELECT * FROM assets WHERE id = $1"

        async with self.db._pool.acquire() as conn:
            row = await conn.fetchrow(query, str(asset_id))

        return dict(row) if row else None

    async def list_assets(
        self,
        workspace_id: Optional[str] = None,
        asset_type: Optional[str] = None,
        tags: Optional[List[str]] = None,
        source: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[Dict[str, Any]]:
        """List assets with filters.

        Args:
            workspace_id: Filter by workspace
            asset_type: Filter by type
            tags: Filter by tags (assets must have all specified tags)
            source: Filter by source
            limit: Max results
            offset: Results offset

        Returns:
            List of asset data
        """
        conditions = []
        params = []
        param_count = 0

        if workspace_id:
            param_count += 1
            conditions.append(f"workspace_id = ${param_count}")
            params.append(workspace_id)

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

        where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""
        query = f"""
            SELECT * FROM assets
            {where_clause}
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
        asset_metadata: Optional[Dict[str, Any]] = None,
        tags: Optional[List[str]] = None,
    ) -> bool:
        """Update asset fields.

        Args:
            asset_id: Asset UUID
            name: New name
            url: New URL
            file_path: New file path
            asset_metadata: Updated metadata (merged with existing)
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

        if asset_metadata is not None:
            param_count += 1
            updates.append(f"asset_metadata = asset_metadata || ${param_count}::jsonb")
            params.append(asset_metadata)

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
            UPDATE assets
            SET {', '.join(updates)}
            WHERE id = ${param_count}
            RETURNING id
        """

        async with self.db._pool.acquire() as conn:
            result = await conn.fetchval(query, *params)

        if result:
            logger.info(f"✓ Updated asset: {asset_id}")
            return True
        return False

    async def delete_asset(self, asset_id: UUID) -> bool:
        """Delete asset by ID.

        Args:
            asset_id: Asset UUID

        Returns:
            True if deleted, False if not found
        """
        query = "DELETE FROM assets WHERE id = $1 RETURNING id"

        async with self.db._pool.acquire() as conn:
            result = await conn.fetchval(query, str(asset_id))

        if result:
            logger.info(f"✓ Deleted asset: {asset_id}")
            return True
        return False

    # ========================================================================
    # RELATIONSHIP OPERATIONS
    # ========================================================================

    async def create_relationship(
        self,
        parent_asset_id: UUID,
        child_asset_id: UUID,
        relationship_type: str,
        sequence: Optional[int] = None,
        relationship_metadata: Optional[Dict[str, Any]] = None,
    ) -> UUID:
        """Create relationship between assets.

        Examples:
        - Film → Shot: relationship_type='contains_shot', sequence=1
        - Shot → Character: relationship_type='uses_character'
        - Shot → Audio: relationship_type='uses_audio'
        - Shot → Take: relationship_type='generation_attempt', sequence=1
        - Take → Video: relationship_type='generated_video'

        Args:
            parent_asset_id: Parent asset UUID
            child_asset_id: Child asset UUID
            relationship_type: Type (contains_shot, uses_character, uses_audio, uses_script, generation_attempt, etc.)
            sequence: Optional sequence order
            relationship_metadata: Relationship-specific metadata

        Returns:
            Relationship UUID
        """
        rel_id = str(uuid4())

        query = """
            INSERT INTO asset_relationships (
                id, parent_asset_id, child_asset_id, relationship_type,
                sequence, asset_metadata, created_at
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
                relationship_metadata or {},
            )

        logger.info(f"✓ Created relationship: {parent_asset_id} --[{relationship_type}]--> {child_asset_id}")
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
            SELECT a.*, r.relationship_type, r.sequence, r.asset_metadata as rel_metadata
            FROM assets a
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
            SELECT a.*, r.relationship_type, r.sequence, r.asset_metadata as rel_metadata
            FROM assets a
            JOIN asset_relationships r ON r.parent_asset_id = a.id
            WHERE {where_clause}
            ORDER BY a.created_at
        """

        async with self.db._pool.acquire() as conn:
            rows = await conn.fetch(query, *params)

        return [dict(row) for row in rows]

    # ========================================================================
    # TYPE-SPECIFIC HELPER METHODS
    # ========================================================================

    async def create_character(
        self,
        workspace_id: str,
        name: str,
        description: Optional[str] = None,
        attributes: Optional[Dict[str, Any]] = None,
        consistency_prompt: Optional[str] = None,
    ) -> UUID:
        """Create a character asset.

        Args:
            workspace_id: Workspace UUID
            name: Character name
            description: Character description
            attributes: Character attributes (age, gender, etc.)
            consistency_prompt: AI consistency prompt

        Returns:
            Character asset UUID
        """
        return await self.create_asset(
            workspace_id=workspace_id,
            asset_type="character_ref",
            name=name,
            asset_metadata={
                "description": description,
                "attributes": attributes or {},
                "consistency_prompt": consistency_prompt,
            },
            source="upload",
        )

    async def add_character_reference_image(
        self,
        character_id: UUID,
        image_url: str,
        file_path: Optional[str] = None,
        size: Optional[int] = None,
        generation_cost: Optional[float] = None,
        generation_metadata: Optional[Dict[str, Any]] = None,
    ) -> UUID:
        """Add reference image to character.

        Args:
            character_id: Character asset UUID
            image_url: Image URL
            file_path: Local file path
            size: File size in bytes
            generation_cost: Cost to generate
            generation_metadata: Generation details

        Returns:
            Image asset UUID
        """
        # Get character to use workspace_id
        character = await self.get_asset(character_id)
        if not character:
            raise ValueError(f"Character {character_id} not found")

        # Create image asset
        image_id = await self.create_asset(
            workspace_id=character["workspace_id"],
            asset_type="image",
            name=f"{character['name']} - Reference Image",
            url=image_url,
            file_path=file_path,
            size=size,
            source="generation" if generation_cost else "upload",
            generation_cost=generation_cost,
            generation_metadata=generation_metadata,
        )

        # Link image to character
        await self.create_relationship(
            parent_asset_id=character_id,
            child_asset_id=image_id,
            relationship_type="reference_for",
        )

        logger.info(f"✓ Added reference image {image_id} to character {character_id}")
        return image_id

    async def get_character_images(self, character_id: UUID) -> List[Dict[str, Any]]:
        """Get all reference images for a character.

        Args:
            character_id: Character asset UUID

        Returns:
            List of image assets
        """
        return await self.get_child_assets(
            parent_asset_id=character_id,
            relationship_type="reference_for",
            asset_type="image",
        )

    async def create_shot(
        self,
        workspace_id: str,
        name: str,
        description: str,
        shot_number: Optional[str] = None,
        camera_angle: Optional[str] = None,
        duration_target: Optional[float] = None,
        prompt: Optional[str] = None,
    ) -> UUID:
        """Create a shot asset (zero shot - text description only).

        Args:
            workspace_id: Workspace UUID
            name: Shot name
            description: Shot description
            shot_number: Shot number/identifier
            camera_angle: Camera angle description
            duration_target: Target duration in seconds
            prompt: AI generation prompt

        Returns:
            Shot asset UUID
        """
        return await self.create_asset(
            workspace_id=workspace_id,
            asset_type="shot",
            name=name,
            asset_metadata={
                "shot_number": shot_number,
                "description": description,
                "camera_angle": camera_angle,
                "duration_target": duration_target,
                "prompt": prompt,
            },
            source="upload",
        )

    async def link_shot_assets(
        self,
        shot_id: UUID,
        characters: Optional[List[UUID]] = None,
        audios: Optional[List[UUID]] = None,
        scripts: Optional[List[UUID]] = None,
    ) -> None:
        """Link multiple assets to a shot.

        A shot can use:
        - Multiple characters
        - Multiple audio tracks
        - Multiple scripts/text

        Args:
            shot_id: Shot asset UUID
            characters: List of character asset UUIDs
            audios: List of audio asset UUIDs
            scripts: List of script/text asset UUIDs
        """
        # Link characters
        if characters:
            for char_id in characters:
                await self.create_relationship(
                    parent_asset_id=shot_id,
                    child_asset_id=char_id,
                    relationship_type="uses_character",
                )
            logger.info(f"✓ Linked {len(characters)} characters to shot {shot_id}")

        # Link audios
        if audios:
            for seq, audio_id in enumerate(audios, start=1):
                await self.create_relationship(
                    parent_asset_id=shot_id,
                    child_asset_id=audio_id,
                    relationship_type="uses_audio",
                    sequence=seq,
                )
            logger.info(f"✓ Linked {len(audios)} audio tracks to shot {shot_id}")

        # Link scripts
        if scripts:
            for script_id in scripts:
                await self.create_relationship(
                    parent_asset_id=shot_id,
                    child_asset_id=script_id,
                    relationship_type="uses_script",
                )
            logger.info(f"✓ Linked {len(scripts)} scripts to shot {shot_id}")

    async def create_shot_take(
        self,
        shot_id: UUID,
        attempt_number: int,
        selected: bool = False,
        generation_params: Optional[Dict[str, Any]] = None,
        quality_score: Optional[float] = None,
        director_notes: Optional[str] = None,
        generation_cost: Optional[float] = None,
    ) -> UUID:
        """Create a shot take (generation attempt).

        Args:
            shot_id: Shot asset UUID
            attempt_number: Take number (1, 2, 3, etc.)
            selected: Is this the selected take for final cut?
            generation_params: Generation parameters used
            quality_score: Quality score (0.0 - 10.0)
            director_notes: Director's notes on this take
            generation_cost: Cost to generate this take

        Returns:
            Take asset UUID
        """
        # Get shot to use workspace_id and name
        shot = await self.get_asset(shot_id)
        if not shot:
            raise ValueError(f"Shot {shot_id} not found")

        take_id = await self.create_asset(
            workspace_id=shot["workspace_id"],
            asset_type="shot_take",
            name=f"{shot['name']} - Take {attempt_number}",
            asset_metadata={
                "attempt_number": attempt_number,
                "selected": selected,
                "generation_params": generation_params or {},
                "quality_score": quality_score,
                "director_notes": director_notes,
            },
            source="generation",
            generation_cost=generation_cost,
        )

        # Link take to shot
        await self.create_relationship(
            parent_asset_id=shot_id,
            child_asset_id=take_id,
            relationship_type="generation_attempt",
            sequence=attempt_number,
        )

        logger.info(f"✓ Created take {attempt_number} for shot {shot_id} (selected={selected})")
        return take_id

    async def get_shot_takes(self, shot_id: UUID) -> List[Dict[str, Any]]:
        """Get all takes for a shot, ordered by attempt number.

        Args:
            shot_id: Shot asset UUID

        Returns:
            List of take assets with metadata
        """
        return await self.get_child_assets(
            parent_asset_id=shot_id,
            relationship_type="generation_attempt",
            asset_type="shot_take",
        )

    async def get_selected_take(self, shot_id: UUID) -> Optional[Dict[str, Any]]:
        """Get the selected take for a shot.

        Args:
            shot_id: Shot asset UUID

        Returns:
            Selected take asset or None
        """
        takes = await self.get_shot_takes(shot_id)
        for take in takes:
            if take.get("asset_metadata", {}).get("selected"):
                return take
        return None

    async def link_take_video(
        self,
        take_id: UUID,
        video_url: str,
        file_path: Optional[str] = None,
        size: Optional[int] = None,
        duration: Optional[float] = None,
        video_metadata: Optional[Dict[str, Any]] = None,
    ) -> UUID:
        """Link generated video to a take.

        Args:
            take_id: Take asset UUID
            video_url: Video URL
            file_path: Local file path
            size: File size
            duration: Video duration
            video_metadata: Video metadata (width, height, fps, codec, etc.)

        Returns:
            Video asset UUID
        """
        # Get take to use workspace_id
        take = await self.get_asset(take_id)
        if not take:
            raise ValueError(f"Take {take_id} not found")

        video_id = await self.create_asset(
            workspace_id=take["workspace_id"],
            asset_type="video",
            name=f"{take['name']} - Video",
            url=video_url,
            file_path=file_path,
            size=size,
            duration=duration,
            asset_metadata=video_metadata or {},
            source="generation",
        )

        # Link video to take
        await self.create_relationship(
            parent_asset_id=take_id,
            child_asset_id=video_id,
            relationship_type="generated_video",
        )

        logger.info(f"✓ Linked video {video_id} to take {take_id}")
        return video_id

    async def create_film(
        self,
        workspace_id: str,
        title: str,
        synopsis: Optional[str] = None,
        total_duration: Optional[float] = None,
        status: str = "in_production",
    ) -> UUID:
        """Create a film project asset.

        Args:
            workspace_id: Workspace UUID
            title: Film title
            synopsis: Film synopsis
            total_duration: Total duration in seconds
            status: Production status

        Returns:
            Film asset UUID
        """
        return await self.create_asset(
            workspace_id=workspace_id,
            asset_type="film",
            name=title,
            asset_metadata={
                "title": title,
                "synopsis": synopsis,
                "total_duration": total_duration,
                "status": status,
            },
            source="upload",
        )

    async def add_shot_to_film(
        self,
        film_id: UUID,
        shot_id: UUID,
        sequence: int,
    ) -> UUID:
        """Add shot to film in sequence.

        Args:
            film_id: Film asset UUID
            shot_id: Shot asset UUID
            sequence: Position in film (1, 2, 3, etc.)

        Returns:
            Relationship UUID
        """
        return await self.create_relationship(
            parent_asset_id=film_id,
            child_asset_id=shot_id,
            relationship_type="contains_shot",
            sequence=sequence,
        )

    async def get_film_shots(self, film_id: UUID) -> List[Dict[str, Any]]:
        """Get all shots in a film, ordered by sequence.

        Args:
            film_id: Film asset UUID

        Returns:
            List of shot assets with sequence numbers
        """
        return await self.get_child_assets(
            parent_asset_id=film_id,
            relationship_type="contains_shot",
            asset_type="shot",
        )
