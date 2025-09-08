"""
Database setup and configuration
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from pathlib import Path

# Database file path
DATABASE_URL = f"sqlite:///{Path(__file__).parent.parent / 'budget_app.db'}"

# Create engine
engine = create_engine(DATABASE_URL, echo=False)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()


def get_db() -> Session:
    """Get database session"""
    db = SessionLocal()
    try:
        return db
    finally:
        pass  # Don't close here, let caller handle


def create_tables():
    """Create all tables"""
    Base.metadata.create_all(bind=engine)


def drop_tables():
    """Drop all tables (for testing)"""
    Base.metadata.drop_all(bind=engine)