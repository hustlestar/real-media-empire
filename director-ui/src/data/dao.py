"""Database access layer for director-ui."""
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import Session

# Lazy imports to avoid circular dependencies
_engine = None
_SessionLocal = None


def get_engine():
    """Get or create database engine."""
    global _engine
    if _engine is None:
        from data.models import Base
        DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./mediaempire.db")
        _engine = create_engine(
            DATABASE_URL,
            pool_size=20,
            max_overflow=100,
            connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {},
        )
        # Create all tables
        Base.metadata.create_all(bind=_engine)
    return _engine


def get_session_local():
    """Get or create session local factory."""
    global _SessionLocal
    if _SessionLocal is None:
        _SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=get_engine())
    return _SessionLocal


def get_db():
    """Get database session."""
    SessionLocal = get_session_local()
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_or_create(db: Session, model, **kwargs):
    """Get or create a model instance."""
    instance = db.query(model).filter_by(**kwargs).first()
    if instance:
        return instance
    else:
        instance = model(**kwargs)
        db.add(instance)
        db.commit()
        db.refresh(instance)
        return instance
