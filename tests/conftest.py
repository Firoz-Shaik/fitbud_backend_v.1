# tests/conftest.py
# Configuration file for the pytest test suite.

import pytest
from typing import Generator
from fastapi.testclient import TestClient
from httpx import Client

from app.main import app
from app.core.database import get_db, Base, engine

# For now, we will test against the actual development database.
# In a more advanced setup, we would create a separate test database.

@pytest.fixture(scope="session")
def db() -> Generator:
    # You might want to create a separate test DB and run migrations here
    # For V1, we'll use the main dev DB.
    yield
    # You could clean up the DB here after tests run

@pytest.fixture(scope="module")
def client() -> Generator[Client, None, None]:
    """
    Provides a TestClient instance for making requests to the FastAPI app.
    """
    with TestClient(app) as c:
        yield c

