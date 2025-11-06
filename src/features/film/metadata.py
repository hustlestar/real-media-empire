"""
Multi-dimensional metadata indexing for asset discovery.

Enables powerful asset queries by:
- Characters
- Landscapes/locations
- Visual styles
- Mood/emotion
- Time of day
- Prompt similarity

This allows reusing assets across projects and discovering existing
assets that match new requirements.
"""

import json
import logging
from collections import defaultdict
from pathlib import Path
from typing import List, Optional, Dict, Set
from datetime import datetime

from config import CONFIG
from film.models import AssetMetadata

logger = logging.getLogger(__name__)


# ============================================================================
# Metadata Index
# ============================================================================


class MetadataIndex:
    """
    Multi-dimensional index for asset metadata.

    Allows querying assets by various criteria to find reusable assets.
    """

    def __init__(self, base_dir: Optional[str] = None):
        self.base_dir = Path(base_dir or CONFIG.get("FILM_GALLERY_DIR", "./film_gallery"))
        self.metadata_dir = self.base_dir / "metadata"

        # Index directories
        self.by_character_dir = self.metadata_dir / "by_character"
        self.by_landscape_dir = self.metadata_dir / "by_landscape"
        self.by_style_dir = self.metadata_dir / "by_style"
        self.by_mood_dir = self.metadata_dir / "by_mood"
        self.by_time_dir = self.metadata_dir / "by_time_of_day"
        self.by_shot_type_dir = self.metadata_dir / "by_shot_type"

        # Ensure directories exist
        for directory in [
            self.metadata_dir,
            self.by_character_dir,
            self.by_landscape_dir,
            self.by_style_dir,
            self.by_mood_dir,
            self.by_time_dir,
            self.by_shot_type_dir,
        ]:
            directory.mkdir(parents=True, exist_ok=True)

    # ========================================================================
    # Indexing
    # ========================================================================

    def index_asset(self, metadata: AssetMetadata):
        """
        Index asset across all dimensions.

        Creates cross-references so assets can be found by any criteria.
        """
        asset_id = metadata.asset_id

        # Index by characters
        for character in metadata.characters:
            self._add_to_index(self.by_character_dir, character, asset_id)

        # Index by landscapes
        for landscape in metadata.landscapes:
            self._add_to_index(self.by_landscape_dir, landscape, asset_id)

        # Index by styles
        for style in metadata.styles:
            self._add_to_index(self.by_style_dir, style, asset_id)

        # Index by mood
        if metadata.mood:
            self._add_to_index(self.by_mood_dir, metadata.mood, asset_id)

        # Index by time of day
        if metadata.time_of_day:
            self._add_to_index(self.by_time_dir, metadata.time_of_day, asset_id)

        # Index by shot type
        if metadata.shot_type:
            self._add_to_index(self.by_shot_type_dir, metadata.shot_type, asset_id)

        logger.debug(f"Indexed asset {asset_id[:12]}... across all dimensions")

    def _add_to_index(self, index_dir: Path, key: str, asset_id: str):
        """Add asset ID to an index file"""
        # Normalize key (lowercase, replace spaces with underscores)
        normalized_key = key.lower().replace(" ", "_")
        index_file = index_dir / f"{normalized_key}.json"

        # Load existing index
        asset_ids = set()
        if index_file.exists():
            try:
                with open(index_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    asset_ids = set(data.get("asset_ids", []))
            except Exception as e:
                logger.warning(f"Failed to load index {index_file}: {e}")

        # Add new asset ID
        asset_ids.add(asset_id)

        # Save updated index
        with open(index_file, "w", encoding="utf-8") as f:
            json.dump(
                {
                    "key": key,
                    "normalized_key": normalized_key,
                    "asset_ids": sorted(list(asset_ids)),
                    "count": len(asset_ids),
                    "updated_at": datetime.now().isoformat(),
                },
                f,
                indent=2,
            )

    # ========================================================================
    # Querying
    # ========================================================================

    def find_assets(
        self,
        characters: Optional[List[str]] = None,
        landscapes: Optional[List[str]] = None,
        styles: Optional[List[str]] = None,
        mood: Optional[str] = None,
        time_of_day: Optional[str] = None,
        shot_type: Optional[str] = None,
        asset_type: Optional[str] = None,  # 'image', 'video', 'audio'
    ) -> List[AssetMetadata]:
        """
        Find assets matching given criteria.

        Returns intersection of all specified criteria.

        Example:
            # Find all images of characters in a forest at dawn
            assets = index.find_assets(
                characters=['emma'],
                landscapes=['forest'],
                time_of_day='dawn',
                asset_type='image'
            )
        """
        # Collect asset IDs from each dimension
        asset_id_sets: List[Set[str]] = []

        if characters:
            for character in characters:
                ids = self._get_from_index(self.by_character_dir, character)
                asset_id_sets.append(ids)

        if landscapes:
            for landscape in landscapes:
                ids = self._get_from_index(self.by_landscape_dir, landscape)
                asset_id_sets.append(ids)

        if styles:
            for style in styles:
                ids = self._get_from_index(self.by_style_dir, style)
                asset_id_sets.append(ids)

        if mood:
            ids = self._get_from_index(self.by_mood_dir, mood)
            asset_id_sets.append(ids)

        if time_of_day:
            ids = self._get_from_index(self.by_time_dir, time_of_day)
            asset_id_sets.append(ids)

        if shot_type:
            ids = self._get_from_index(self.by_shot_type_dir, shot_type)
            asset_id_sets.append(ids)

        # If no criteria specified, return empty
        if not asset_id_sets:
            return []

        # Intersect all sets to find assets matching ALL criteria
        matching_ids = asset_id_sets[0]
        for id_set in asset_id_sets[1:]:
            matching_ids = matching_ids.intersection(id_set)

        # Load full metadata for matching assets
        metadata_list = []
        for asset_id in matching_ids:
            metadata = self._load_asset_metadata(asset_id)
            if metadata:
                # Filter by asset type if specified
                if asset_type and metadata.asset_type != asset_type:
                    continue
                metadata_list.append(metadata)

        logger.info(f"Found {len(metadata_list)} assets matching criteria")
        return metadata_list

    def _get_from_index(self, index_dir: Path, key: str) -> Set[str]:
        """Get asset IDs from an index file"""
        normalized_key = key.lower().replace(" ", "_")
        index_file = index_dir / f"{normalized_key}.json"

        if not index_file.exists():
            return set()

        try:
            with open(index_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                return set(data.get("asset_ids", []))
        except Exception as e:
            logger.warning(f"Failed to read index {index_file}: {e}")
            return set()

    def _load_asset_metadata(self, asset_id: str) -> Optional[AssetMetadata]:
        """Load asset metadata by ID"""
        metadata_file = self.metadata_dir / "by_prompt_hash" / f"{asset_id}.json"

        if not metadata_file.exists():
            return None

        try:
            with open(metadata_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                return AssetMetadata(**data)
        except Exception as e:
            logger.warning(f"Failed to load metadata {asset_id}: {e}")
            return None

    # ========================================================================
    # Discovery & Statistics
    # ========================================================================

    def get_all_characters(self) -> List[str]:
        """Get list of all indexed characters"""
        return self._get_all_keys(self.by_character_dir)

    def get_all_landscapes(self) -> List[str]:
        """Get list of all indexed landscapes"""
        return self._get_all_keys(self.by_landscape_dir)

    def get_all_styles(self) -> List[str]:
        """Get list of all indexed styles"""
        return self._get_all_keys(self.by_style_dir)

    def get_all_moods(self) -> List[str]:
        """Get list of all indexed moods"""
        return self._get_all_keys(self.by_mood_dir)

    def _get_all_keys(self, index_dir: Path) -> List[str]:
        """Get all keys from an index directory"""
        keys = []
        for index_file in index_dir.glob("*.json"):
            try:
                with open(index_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    key = data.get("key")
                    if key:
                        keys.append(key)
            except Exception:
                continue
        return sorted(keys)

    def get_index_stats(self) -> Dict[str, int]:
        """Get statistics about the index"""
        return {
            "total_characters": len(list(self.by_character_dir.glob("*.json"))),
            "total_landscapes": len(list(self.by_landscape_dir.glob("*.json"))),
            "total_styles": len(list(self.by_style_dir.glob("*.json"))),
            "total_moods": len(list(self.by_mood_dir.glob("*.json"))),
            "total_assets": len(list((self.metadata_dir / "by_prompt_hash").glob("*.json"))),
        }

    # ========================================================================
    # Asset Usage Tracking
    # ========================================================================

    def mark_asset_used(self, asset_id: str, project_id: str):
        """Mark an asset as used in a project"""
        metadata = self._load_asset_metadata(asset_id)
        if metadata:
            metadata.mark_used(project_id)
            self._save_asset_metadata(metadata)
            logger.debug(f"Marked asset {asset_id[:12]}... as used in {project_id}")

    def _save_asset_metadata(self, metadata: AssetMetadata):
        """Save updated asset metadata"""
        metadata_file = self.metadata_dir / "by_prompt_hash" / f"{metadata.asset_id}.json"
        with open(metadata_file, "w", encoding="utf-8") as f:
            json.dump(metadata.model_dump(), f, indent=2, default=str)

    def get_most_reused_assets(self, limit: int = 10) -> List[AssetMetadata]:
        """Get assets with highest reuse count"""
        all_assets = []

        metadata_dir = self.metadata_dir / "by_prompt_hash"
        for metadata_file in metadata_dir.glob("*.json"):
            metadata = self._load_asset_metadata(metadata_file.stem)
            if metadata:
                all_assets.append(metadata)

        # Sort by reuse count
        all_assets.sort(key=lambda x: x.reuse_count, reverse=True)
        return all_assets[:limit]


# ============================================================================
# Prompt Similarity (Future Enhancement)
# ============================================================================


class PromptSimilarity:
    """
    Find assets with similar prompts using text similarity.

    Future enhancement: Use embeddings (OpenAI, sentence-transformers)
    for semantic similarity search.
    """

    def __init__(self):
        pass

    def find_similar_prompts(
        self,
        query_prompt: str,
        threshold: float = 0.8,
    ) -> List[AssetMetadata]:
        """
        Find assets with similar prompts.

        TODO: Implement using:
        - OpenAI embeddings API
        - or sentence-transformers locally
        - Vector database (FAISS, ChromaDB, etc.)
        """
        raise NotImplementedError("Prompt similarity search not yet implemented. " "Requires embeddings and vector database.")
