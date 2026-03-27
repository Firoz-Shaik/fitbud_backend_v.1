# tests/conftest.py
# Configuration file for the pytest test suite with PostgreSQL test database setup.

import pytest
import uuid
import os
from typing import Generator
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import NullPool

# Disable Redis-backed auth caching during tests (no REDIS_URL required).
os.environ.setdefault("DISABLE_AUTH_CACHE", "1")

from app.main import app
from app.core.database import Base, get_db
from app.core.security import get_password_hash, create_access_token
from app.models.user import User
from app.models.client import Client
from app.models.template import ExerciseLibrary, FoodItemLibrary


# Get test database URL from environment variable
TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    "postgresql://test_user:test_password@localhost:5433/test_db"
)

# Create engine with NullPool to avoid connection issues in tests
engine = create_engine(
    TEST_DATABASE_URL,
    poolclass=NullPool,
    echo=False  # Set to True for SQL debugging
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="session", autouse=True)
def setup_test_database():
    """
    Create all tables once at the start of the test session.
    Drop all tables at the end of the test session.
    """
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def test_db() -> Generator[Session, None, None]:
    """
    Creates a fresh database session for each test function.
    Uses transactions that are rolled back after each test for isolation.
    """
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    
    # Begin a nested transaction (using SAVEPOINT)
    nested = connection.begin_nested()
    
    # If the application code calls session.commit(), it will only commit the nested transaction
    @event.listens_for(session, "after_transaction_end")
    def end_savepoint(session, transaction):
        nonlocal nested
        if not nested.is_active:
            nested = connection.begin_nested()
    
    yield session
    
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture(scope="function")
def client(test_db: Session, test_trainer: User) -> Generator[TestClient, None, None]:
    """
    Provides a TestClient instance with overridden database dependency.
    Depends on test_trainer so the trainer user exists in users table before
    any API request (avoids FK violations for diet_plan_templates, clients, etc.).
    """
    def override_get_db():
        try:
            yield test_db
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def test_trainer(test_db: Session) -> User:
    """
    Creates a test trainer user.
    """
    trainer = User(
        id=uuid.uuid4(),
        email="trainer@test.com",
        hashed_password=get_password_hash("password123"),
        full_name="Test Trainer",
        user_role="trainer"
    )
    test_db.add(trainer)
    test_db.commit()
    test_db.refresh(trainer)
    return trainer


@pytest.fixture
def trainer_user(test_db: Session) -> User:
    """
    Alias for test_trainer. Ensures trainer user exists before any fixture
    that creates clients, templates, or assignments (FK to users).
    """
    trainer = User(
        id=uuid.uuid4(),
        email="trainer_user@test.com",
        hashed_password=get_password_hash("password123"),
        full_name="Trainer User",
        user_role="trainer"
    )
    test_db.add(trainer)
    test_db.commit()
    test_db.refresh(trainer)
    return trainer


@pytest.fixture
def test_client_user(test_db: Session) -> User:
    """
    Creates a test client user.
    """
    client_user = User(
        id=uuid.uuid4(),
        email="client@test.com",
        hashed_password=get_password_hash("password123"),
        full_name="Test Client",
        user_role="client"
    )
    test_db.add(client_user)
    test_db.commit()
    test_db.refresh(client_user)
    return client_user


@pytest.fixture
def test_client_profile(test_db: Session, test_trainer: User, test_client_user: User) -> Client:
    """
    Creates a test client profile linked to trainer and client user.
    """
    client_profile = Client(
        id=uuid.uuid4(),
        trainer_user_id=test_trainer.id,
        client_user_id=test_client_user.id,
        client_status="active",
        goal="Weight Loss",
        invited_full_name=test_client_user.full_name,
        invited_email=test_client_user.email,
        deleted_at=None
    )
    test_db.add(client_profile)
    test_db.commit()
    test_db.refresh(client_profile)
    return client_profile


@pytest.fixture
def trainer_token(test_trainer: User) -> str:
    """
    Generates a JWT token for the test trainer.
    """
    return create_access_token(subject=test_trainer.email)


@pytest.fixture
def client_token(test_client_user: User) -> str:
    """
    Generates a JWT token for the test client.
    """
    return create_access_token(subject=test_client_user.email)


@pytest.fixture
def test_exercise(test_db: Session) -> ExerciseLibrary:
    """
    Creates a test exercise in the library.
    """
    exercise = ExerciseLibrary(
        id=uuid.uuid4(),
        name="Bench Press",
        description="Chest exercise",
        is_verified=True
    )
    test_db.add(exercise)
    test_db.commit()
    test_db.refresh(exercise)
    return exercise


@pytest.fixture
def test_food_item(test_db: Session) -> FoodItemLibrary:
    """
    Creates a test food item in the library.
    """
    food = FoodItemLibrary(
        id=uuid.uuid4(),
        name="Chicken Breast",
        is_verified=True,
        base_unit_type="MASS",
        calories_per_100g=165,
        protein_per_100g=31.0,
        carbs_per_100g=0.0,
        fat_per_100g=3.6
    )
    test_db.add(food)
    test_db.commit()
    test_db.refresh(food)
    return food
