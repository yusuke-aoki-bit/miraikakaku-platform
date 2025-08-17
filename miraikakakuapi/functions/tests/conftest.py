import pytest
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
from database.database import get_db, Base
from main import app

# テスト用データベースURL
TEST_DATABASE_URL = "sqlite:///./test_miraikakaku.db"

@pytest.fixture(scope="session")
def test_engine():
    """テスト用データベースエンジン"""
    engine = create_engine(
        TEST_DATABASE_URL, 
        connect_args={"check_same_thread": False}
    )
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)
    
    # テストDBファイルを削除
    if os.path.exists("./test_miraikakaku.db"):
        os.remove("./test_miraikakaku.db")

@pytest.fixture(scope="function")
def test_db_session(test_engine):
    """テスト用データベースセッション"""
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
    session = TestingSessionLocal()
    yield session
    session.close()

@pytest.fixture(scope="function")
def client(test_db_session):
    """テスト用FastAPIクライアント"""
    def override_get_db():
        try:
            yield test_db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()

@pytest.fixture
def sample_stock_data():
    """テスト用株式データ"""
    return {
        "symbol": "TEST",
        "company_name": "Test Company Inc.",
        "sector": "Technology",
        "market": "NASDAQ",
        "description": "Test company for testing purposes",
        "is_active": True,
        "pe_ratio": 25.5,
        "dividend_yield": 0.025,
        "beta": 1.2
    }

@pytest.fixture
def sample_price_data():
    """テスト用株価データ"""
    return {
        "symbol": "TEST",
        "date": "2024-01-01",
        "open_price": 100.0,
        "high_price": 105.0,
        "low_price": 98.0,
        "close_price": 103.0,
        "volume": 1000000,
        "adjusted_close": 103.0
    }

@pytest.fixture
def mock_auth_token():
    """モック認証トークン"""
    return "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.test-payload.test-signature"

@pytest.fixture
def auth_headers(mock_auth_token):
    """認証ヘッダー"""
    return {"Authorization": f"Bearer {mock_auth_token}"}

@pytest.fixture
def admin_user_data():
    """管理者ユーザーテストデータ"""
    return {
        "email": "admin@test.com",
        "name": "Test Admin",
        "role": "admin",
        "is_active": True
    }

@pytest.fixture
def regular_user_data():
    """一般ユーザーテストデータ"""
    return {
        "email": "user@test.com", 
        "name": "Test User",
        "role": "user",
        "is_active": True
    }