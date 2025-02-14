# For test setup

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, NewsArticle, Weather
from app import app

# In-memory SQLite database for testing
TEST_DATABASE_URL = "sqlite:///:memory:"

@pytest.fixture(scope="function")
def test_session():
    """Creates a new database session for each test."""
    engine = create_engine(TEST_DATABASE_URL)
    TestingSessionLocal = sessionmaker(bind=engine)
    Base.metadata.create_all(engine) # Create tables
    session = TestingSessionLocal()
    yield session
    session.close()