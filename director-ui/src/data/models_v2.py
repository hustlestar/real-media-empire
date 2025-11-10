"""Asset-centric SQLAlchemy models (V2 Schema).

This module contains the new asset-centric schema models that will eventually
replace the existing models. During migration, both schemas coexist.
"""

from datetime import datetime
from typing import Optional, Dict, Any, List
from sqlalchemy import (
    Column,
    String,
    Text,
    Integer,
    BigInteger,
    Float,
    Boolean,
    DateTime,
    ForeignKey,
    JSON,
    ARRAY,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship, Mapped
from .models import Base


class AssetV2(Base):
    """Universal asset model - everything is an asset.

    This model represents any piece of content: scripts, text, audio, video,
    images, shots, films, character references, scenes, etc.

    Type-specific data is stored in the metadata JSONB field, allowing for
    flexible schema evolution without migrations.
    """
    __tablename__ = "assets_v2"

    id: Mapped[str] = Column(String, primary_key=True)
    workspace_id: Mapped[Optional[str]] = Column(
        String,
        ForeignKey("workspaces.id", ondelete="CASCADE"),
        nullable=True,
        index=True
    )

    # Core universal fields
    type: Mapped[str] = Column(
        String(50),
        nullable=False,
        index=True,
        comment="Asset type: script, text, audio, video, image, shot, film, character_ref, scene"
    )
    name: Mapped[str] = Column(String(255), nullable=False)

    # Storage
    url: Mapped[Optional[str]] = Column(Text, nullable=True, comment="Public CDN URL")
    file_path: Mapped[Optional[str]] = Column(Text, nullable=True, comment="Local filesystem path")
    size: Mapped[Optional[int]] = Column(BigInteger, nullable=True, comment="File size in bytes")
    duration: Mapped[Optional[float]] = Column(Float, nullable=True, comment="Duration for audio/video in seconds")

    # Flexible metadata (type-specific data)
    metadata: Mapped[Dict[str, Any]] = Column(
        JSON,
        nullable=False,
        server_default='{}',
        comment="Type-specific metadata"
    )
    tags: Mapped[List[str]] = Column(
        ARRAY(String),
        nullable=False,
        server_default='{}',
        comment="Asset tags"
    )

    # Generation tracking
    source: Mapped[Optional[str]] = Column(
        String(50),
        nullable=True,
        index=True,
        comment="Source: upload, generation, import, derivative"
    )
    generation_cost: Mapped[Optional[float]] = Column(
        Float,
        nullable=True,
        comment="Cost to generate this asset"
    )
    generation_metadata: Mapped[Optional[Dict[str, Any]]] = Column(
        JSON,
        nullable=True,
        comment="Provider, model, prompt, seed"
    )

    # Timestamps
    created_at: Mapped[datetime] = Column(
        DateTime(timezone=True),
        server_default="NOW()",
        nullable=False
    )
    updated_at: Mapped[datetime] = Column(
        DateTime(timezone=True),
        server_default="NOW()",
        nullable=False
    )

    # Relationships
    # workspace = relationship("Workspace", back_populates="assets_v2")
    parent_relationships: Mapped[List["AssetRelationship"]] = relationship(
        "AssetRelationship",
        foreign_keys="AssetRelationship.parent_asset_id",
        back_populates="parent_asset",
        cascade="all, delete-orphan"
    )
    child_relationships: Mapped[List["AssetRelationship"]] = relationship(
        "AssetRelationship",
        foreign_keys="AssetRelationship.child_asset_id",
        back_populates="child_asset",
        cascade="all, delete-orphan"
    )
    collection_memberships: Mapped[List["AssetCollectionMember"]] = relationship(
        "AssetCollectionMember",
        back_populates="asset",
        cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<AssetV2(id={self.id}, type={self.type}, name={self.name})>"


class AssetRelationship(Base):
    """Universal asset relationships - defines how assets connect.

    Examples:
    - Film (parent) → Shot (child): relationship_type='part_of', sequence=1
    - Shot (parent) → Video (child): relationship_type='generated_from'
    - Character (parent) → Image (child): relationship_type='reference_for'
    - Image Original (parent) → Image Upscaled (child): relationship_type='derived_from'
    """
    __tablename__ = "asset_relationships"
    __table_args__ = (
        UniqueConstraint(
            'parent_asset_id',
            'child_asset_id',
            'relationship_type',
            name='uq_asset_relationships_parent_child_type'
        ),
    )

    id: Mapped[str] = Column(String, primary_key=True)
    parent_asset_id: Mapped[str] = Column(
        String,
        ForeignKey("assets_v2.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    child_asset_id: Mapped[str] = Column(
        String,
        ForeignKey("assets_v2.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    relationship_type: Mapped[str] = Column(
        String(50),
        nullable=False,
        index=True,
        comment="used_in, derived_from, variant_of, part_of, reference_for, generated_from"
    )
    sequence: Mapped[Optional[int]] = Column(
        Integer,
        nullable=True,
        comment="Order when relationship implies sequence"
    )
    metadata: Mapped[Dict[str, Any]] = Column(
        JSON,
        nullable=False,
        server_default='{}',
        comment="Relationship-specific data"
    )

    created_at: Mapped[datetime] = Column(
        DateTime(timezone=True),
        server_default="NOW()",
        nullable=False
    )

    # Relationships
    parent_asset: Mapped["AssetV2"] = relationship(
        "AssetV2",
        foreign_keys=[parent_asset_id],
        back_populates="parent_relationships"
    )
    child_asset: Mapped["AssetV2"] = relationship(
        "AssetV2",
        foreign_keys=[child_asset_id],
        back_populates="child_relationships"
    )

    def __repr__(self) -> str:
        return f"<AssetRelationship(parent={self.parent_asset_id}, child={self.child_asset_id}, type={self.relationship_type})>"


class AssetCollection(Base):
    """Asset collections for grouping and organization.

    Examples:
    - type='project': A film project containing all related assets
    - type='character': Character definition with reference images
    - type='storyboard': Collection of shots in sequence
    - type='library': Reusable asset library (music, sound effects, etc.)
    """
    __tablename__ = "asset_collections"

    id: Mapped[str] = Column(String, primary_key=True)
    workspace_id: Mapped[str] = Column(
        String,
        ForeignKey("workspaces.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    name: Mapped[str] = Column(String(255), nullable=False)
    type: Mapped[str] = Column(
        String(50),
        nullable=False,
        index=True,
        comment="project, character, storyboard, library"
    )
    description: Mapped[Optional[str]] = Column(Text, nullable=True)
    metadata: Mapped[Dict[str, Any]] = Column(
        JSON,
        nullable=False,
        server_default='{}'
    )

    created_at: Mapped[datetime] = Column(
        DateTime(timezone=True),
        server_default="NOW()",
        nullable=False
    )
    updated_at: Mapped[datetime] = Column(
        DateTime(timezone=True),
        server_default="NOW()",
        nullable=False
    )

    # Relationships
    # workspace = relationship("Workspace", back_populates="asset_collections")
    members: Mapped[List["AssetCollectionMember"]] = relationship(
        "AssetCollectionMember",
        back_populates="collection",
        cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<AssetCollection(id={self.id}, type={self.type}, name={self.name})>"


class AssetCollectionMember(Base):
    """Membership relationship between assets and collections.

    Tracks which assets belong to which collections, with optional sequencing
    and member-specific metadata.
    """
    __tablename__ = "asset_collection_members"
    __table_args__ = (
        UniqueConstraint(
            'collection_id',
            'asset_id',
            name='uq_collection_members_collection_asset'
        ),
    )

    id: Mapped[str] = Column(String, primary_key=True)
    collection_id: Mapped[str] = Column(
        String,
        ForeignKey("asset_collections.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    asset_id: Mapped[str] = Column(
        String,
        ForeignKey("assets_v2.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    sequence: Mapped[Optional[int]] = Column(
        Integer,
        nullable=True,
        comment="Order within collection"
    )
    metadata: Mapped[Dict[str, Any]] = Column(
        JSON,
        nullable=False,
        server_default='{}',
        comment="Member-specific data"
    )

    created_at: Mapped[datetime] = Column(
        DateTime(timezone=True),
        server_default="NOW()",
        nullable=False
    )

    # Relationships
    collection: Mapped["AssetCollection"] = relationship(
        "AssetCollection",
        back_populates="members"
    )
    asset: Mapped["AssetV2"] = relationship(
        "AssetV2",
        back_populates="collection_memberships"
    )

    def __repr__(self) -> str:
        return f"<AssetCollectionMember(collection={self.collection_id}, asset={self.asset_id}, seq={self.sequence})>"
