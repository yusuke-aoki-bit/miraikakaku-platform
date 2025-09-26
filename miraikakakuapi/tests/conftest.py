"""
Test configuration and fixtures for MiraiKakaku API
"""
import os
import pytest
from unittest.mock import MagicMock
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

# Set test environment
os.environ["DATABASE_URL"] = "sqlite:///test.db"
os.environ["JWT_SECRET_KEY"] = "test-secret-key"
os.environ["LOG_LEVEL"] = "DEBUG"

@pytest.fixture(scope="session")
def test_db():
    """Create test database"""
    engine = create_engine("sqlite:///test.db", echo=False)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    # Import models after setting environment
    from functions.database.models.base import Base
    Base.metadata.create_all(bind=engine)

    yield TestingSessionLocal

    # Cleanup
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def db_session(test_db):
    """Create database session for tests"""
    session = test_db()
    try:
        yield session
    finally:
        session.close()

@pytest.fixture
def client():
    """Create a test client"""
    from fastapi.testclient import TestClient
    from functions.main import app
    return TestClient(app)

@pytest.fixture
def mock_yfinance():
    """Mock yfinance for tests"""
    mock = MagicMock()
    mock.download.return_value = {
        'Close': [100, 101, 102],
        'Open': [99, 100, 101],
        'High': [101, 102, 103],
        'Low': [98, 99, 100],
        'Volume': [1000, 1100, 1200]
    }
    return mock

@pytest.fixture
def sample_stock_data():
    """Sample stock data for testing"""
    return {
        "symbol": "AAPL",
        "name": "Apple Inc.",
        "exchange": "NASDAQ",
        "price": 150.0,
        "change": 2.5,
        "change_percent": 1.69
    }