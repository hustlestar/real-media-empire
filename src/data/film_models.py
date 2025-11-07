"""
SQLAlchemy models for film generation assets.

Tracks:
- Film projects
- Generated assets (images, videos, audio)
- Asset reuse across projects
- Cost tracking
"""

from datetime import datetime
from sqlalchemy import (
    Column,
    String,
    Integer,
    Numeric,
    DateTime,
    Text,
    ForeignKey,
    Table,
    ARRAY,
    Boolean,
)
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

from data.models import Base  # Use existing Base from main models


# ============================================================================
# Association Tables
# ============================================================================

# Many-to-many: Film projects can use many assets, assets can be in many projects
film_project_assets = Table(
    "film_project_assets",
    Base.metadata,
    Column("project_id", String, ForeignKey("film_projects.id"), primary_key=True),
    Column("asset_id", String, ForeignKey("film_assets.id"), primary_key=True),
    Column("shot_id", String, nullable=True),  # Which shot used this asset
    Column("used_at", DateTime, default=datetime.now),
)


# ============================================================================
# Film Project Model
# ============================================================================


class FilmProject(Base):
    """
    A film generation project.

    Tracks metadata, costs, and status for a complete film.
    """

    __tablename__ = "film_projects"

    id = Column(String, primary_key=True)  # film_id
    name = Column(String, nullable=True)
    description = Column(Text, nullable=True)

    # Status
    status = Column(
        String,
        default="pending",
        # 'pending', 'generating', 'completed', 'failed'
    )

    # Costs
    estimated_cost_usd = Column(Numeric(10, 4), nullable=True)
    actual_cost_usd = Column(Numeric(10, 4), default=0)
    budget_limit_usd = Column(Numeric(10, 4), nullable=True)

    # Counts
    total_shots = Column(Integer, default=0)
    completed_shots = Column(Integer, default=0)

    # Timing
    created_at = Column(DateTime, default=datetime.now)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)

    # Output
    final_film_path = Column(String, nullable=True)
    shots_json_path = Column(String, nullable=True)  # Input file

    # Relationships
    assets = relationship(
        "FilmAsset",
        secondary=film_project_assets,
        back_populates="projects",
    )

    def __repr__(self):
        return f"<FilmProject(id='{self.id}', status='{self.status}', cost=${self.actual_cost_usd})>"


# ============================================================================
# Film Asset Model
# ============================================================================


class FilmAsset(Base):
    """
    A generated asset (image, video, or audio).

    Assets are content-addressed and can be reused across projects.
    """

    __tablename__ = "film_assets"

    id = Column(String, primary_key=True)  # UUID
    content_hash = Column(String, unique=True, index=True, nullable=False)
    asset_type = Column(String, nullable=False)  # 'image', 'video', 'audio'

    # Storage
    file_path = Column(String, nullable=False)
    file_url = Column(String, nullable=True)  # Original API URL
    file_size_bytes = Column(Integer, nullable=True)

    # Metadata for discovery
    characters = Column(ARRAY(String), default=list)
    landscapes = Column(ARRAY(String), default=list)
    styles = Column(ARRAY(String), default=list)
    mood = Column(String, nullable=True)
    time_of_day = Column(String, nullable=True)
    shot_type = Column(String, nullable=True)

    # Generation parameters
    prompt = Column(Text, nullable=False)
    negative_prompt = Column(Text, nullable=True)
    provider = Column(String, nullable=False)  # 'FAL', 'Minimax', 'OpenAI', etc.
    model = Column(String, nullable=False)
    config_json = Column(Text, nullable=True)  # JSON string of config

    # Dimensions (for images/videos)
    width = Column(Integer, nullable=True)
    height = Column(Integer, nullable=True)
    duration_seconds = Column(Numeric(8, 2), nullable=True)  # For videos/audio
    fps = Column(Integer, nullable=True)  # For videos

    # Cost tracking
    cost_usd = Column(Numeric(10, 4), nullable=False)
    generation_time_seconds = Column(Integer, nullable=False)

    # Usage tracking
    reuse_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.now)
    last_used_at = Column(DateTime, nullable=True)

    # Relationships
    projects = relationship(
        "FilmProject",
        secondary=film_project_assets,
        back_populates="assets",
    )

    def __repr__(self):
        return f"<FilmAsset(type='{self.asset_type}', " f"provider='{self.provider}', " f"reuse_count={self.reuse_count})>"

    def mark_used(self):
        """Increment reuse count and update last used timestamp"""
        self.reuse_count += 1
        self.last_used_at = datetime.now()


# ============================================================================
# Cost Report Model
# ============================================================================


class FilmCostReport(Base):
    """
    Detailed cost report for a film project.

    Stores itemized costs per shot and provider breakdown.
    """

    __tablename__ = "film_cost_reports"

    id = Column(Integer, primary_key=True, autoincrement=True)
    project_id = Column(String, ForeignKey("film_projects.id"), nullable=False)

    # Costs
    estimated_cost_usd = Column(Numeric(10, 4), nullable=False)
    actual_cost_usd = Column(Numeric(10, 4), nullable=False)
    cost_saved_usd = Column(Numeric(10, 4), default=0)  # From caching

    # Provider breakdown (stored as JSON)
    provider_costs_json = Column(Text, nullable=True)

    # Cache stats
    cache_hits = Column(Integer, default=0)
    cache_misses = Column(Integer, default=0)
    cache_hit_rate_percent = Column(Numeric(5, 2), default=0)

    # Timing
    total_generation_time_seconds = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.now)

    def __repr__(self):
        return f"<FilmCostReport(project='{self.project_id}', " f"actual=${self.actual_cost_usd}, " f"saved=${self.cost_saved_usd})>"


# ============================================================================
# Helper Functions
# ============================================================================


def create_film_project(db_session, project_id: str, shots_json_path: str, budget_limit_usd: float = None, **kwargs) -> FilmProject:
    """
    Create a new film project in database.

    Args:
        db_session: SQLAlchemy session
        project_id: Unique project identifier
        shots_json_path: Path to shots definition file
        budget_limit_usd: Optional budget limit
        **kwargs: Additional project fields

    Returns:
        FilmProject instance
    """
    project = FilmProject(id=project_id, shots_json_path=shots_json_path, budget_limit_usd=budget_limit_usd, **kwargs)

    db_session.add(project)
    db_session.commit()

    return project


def get_or_create_asset(db_session, content_hash: str, **asset_data) -> tuple[FilmAsset, bool]:
    """
    Get existing asset by content hash or create new one.

    Args:
        db_session: SQLAlchemy session
        content_hash: Content-based hash
        **asset_data: Asset fields

    Returns:
        (FilmAsset, was_created)
    """
    # Check if exists
    asset = db_session.query(FilmAsset).filter_by(content_hash=content_hash).first()

    if asset:
        # Existing asset - mark as used
        asset.mark_used()
        db_session.commit()
        return asset, False

    # Create new asset
    asset = FilmAsset(content_hash=content_hash, **asset_data)

    db_session.add(asset)
    db_session.commit()

    return asset, True


def link_asset_to_project(
    db_session,
    project_id: str,
    asset_id: str,
    shot_id: str = None,
):
    """
    Link an asset to a project.

    Creates entry in association table.
    """
    # This is handled automatically by SQLAlchemy relationships,
    # but we can also insert directly if needed
    from sqlalchemy import insert

    stmt = insert(film_project_assets).values(
        project_id=project_id,
        asset_id=asset_id,
        shot_id=shot_id,
        used_at=datetime.now(),
    )

    db_session.execute(stmt)
    db_session.commit()


def get_most_reused_assets(db_session, limit: int = 10):
    """
    Get assets with highest reuse count.

    Useful for understanding which assets provide most value.
    """
    return db_session.query(FilmAsset).order_by(FilmAsset.reuse_count.desc()).limit(limit).all()


# ============================================================================
# Shot Model (Individual shots within a film)
# ============================================================================


class FilmShot(Base):
    """
    An individual shot within a film project.

    Tracks shot-level assets, status, and review feedback.
    """

    __tablename__ = "film_shots"

    id = Column(String, primary_key=True)  # UUID
    shot_id = Column(String, nullable=False)  # shot_001, shot_002, etc.
    film_project_id = Column(String, ForeignKey("film_projects.id", ondelete="CASCADE"), nullable=False)

    # Assets
    image_url = Column(String, nullable=True)
    video_url = Column(String, nullable=False)
    thumbnail_url = Column(String, nullable=True)
    audio_url = Column(String, nullable=True)

    # Shot metadata
    prompt = Column(Text, nullable=False)
    duration = Column(Numeric(8, 2), default=5.0)  # Duration in seconds
    sequence_order = Column(Integer, nullable=True)  # Order within film

    # Status
    status = Column(String, default="completed")  # 'pending', 'generating', 'completed', 'approved', 'rejected', 'needs_revision'

    # Timing
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    # Relationships
    film_project = relationship("FilmProject", backref="shots")
    review = relationship("ShotReview", back_populates="shot", uselist=False)

    def __repr__(self):
        return f"<FilmShot(shot_id='{self.shot_id}', film_project_id='{self.film_project_id}', status='{self.status}')>"


# ============================================================================
# Shot Review Model (Director's feedback and approval)
# ============================================================================


class ShotReview(Base):
    """
    Review and feedback for a film shot.

    Tracks director's approval, rejection, or revision requests.
    """

    __tablename__ = "shot_reviews"

    id = Column(Integer, primary_key=True, autoincrement=True)
    shot_id = Column(String, ForeignKey("film_shots.id", ondelete="CASCADE"), nullable=False, unique=True)

    # Review decision
    status = Column(String, nullable=False)  # 'approved', 'rejected', 'needs_revision'
    notes = Column(Text, nullable=True)  # Director's feedback

    # Reviewer
    reviewer = Column(String, nullable=True)  # Username or email
    reviewed_at = Column(DateTime, default=datetime.now)

    # Relationship
    shot = relationship("FilmShot", back_populates="review")

    def __repr__(self):
        return f"<ShotReview(shot_id='{self.shot_id}', status='{self.status}', reviewer='{self.reviewer}')>"


def get_project_cost_summary(db_session, project_id: str) -> dict:
    """
    Get cost summary for a project.

    Returns dict with costs and stats.
    """
    project = db_session.query(FilmProject).filter_by(id=project_id).first()

    if not project:
        return None

    # Get associated assets
    assets = project.assets
    asset_costs_by_type = {
        "image": sum(a.cost_usd for a in assets if a.asset_type == "image"),
        "video": sum(a.cost_usd for a in assets if a.asset_type == "video"),
        "audio": sum(a.cost_usd for a in assets if a.asset_type == "audio"),
    }

    return {
        "project_id": project.id,
        "status": project.status,
        "estimated_cost": float(project.estimated_cost_usd or 0),
        "actual_cost": float(project.actual_cost_usd),
        "budget_limit": float(project.budget_limit_usd) if project.budget_limit_usd else None,
        "asset_costs": {k: float(v) for k, v in asset_costs_by_type.items()},
        "total_assets": len(assets),
        "completed_shots": project.completed_shots,
        "total_shots": project.total_shots,
    }
