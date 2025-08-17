# app/core/database.py
# Handles database connection and session management.

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from .config import settings

# Create the SQLAlchemy engine
# The pool_pre_ping argument ensures that the connection is alive before being used.
engine = create_engine(
    settings.DATABASE_URL, 
    pool_pre_ping=True
)

# Create a session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for our ORM models
Base = declarative_base()

# Dependency for getting a DB session in path operations
def get_db():
    """
    FastAPI dependency that provides a SQLAlchemy database session per request.
    It ensures the session is always closed after the request is finished.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
