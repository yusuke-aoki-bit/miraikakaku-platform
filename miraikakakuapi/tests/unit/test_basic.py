"""
Basic unit tests that don't require the full application.
"""
import pytest
import os


@pytest.mark.unit
def test_environment_variables():
    """Test that test environment is properly set up."""
    # Test environment variables are set by conftest.py
    # Just verify the test can access environment
    database_url = os.getenv("DATABASE_URL")
    assert database_url is not None
    assert "test.db" in database_url


@pytest.mark.unit
def test_database_models_import():
    """Test that database models can be imported."""
    try:
        from functions.database.models.stock_master import StockMaster
        from functions.database.models.stock_price_history import StockPriceHistory
        from functions.database.models.stock_predictions import StockPredictions

        # Basic validation that models have required attributes
        assert hasattr(StockMaster, '__tablename__')
        assert hasattr(StockPriceHistory, '__tablename__')
        assert hasattr(StockPredictions, '__tablename__')

    except ImportError as e:
        pytest.fail(f"Failed to import database models: {e}")


@pytest.mark.unit
def test_sample_data_fixtures(sample_stock_data):
    """Test that sample data fixtures work correctly."""
    assert isinstance(sample_stock_data, dict)
    assert "symbol" in sample_stock_data
    assert "name" in sample_stock_data
    assert sample_stock_data["symbol"] == "AAPL"


@pytest.mark.unit
def test_mock_yfinance_fixture(mock_yfinance):
    """Test that yfinance mock works correctly."""
    data = mock_yfinance.download.return_value
    assert isinstance(data, dict)
    assert "Close" in data
    assert len(data["Close"]) == 3


@pytest.mark.unit
def test_database_session_creation(test_db):
    """Test that database session can be created."""
    session = test_db()
    assert session is not None
    session.close()


@pytest.mark.unit
def test_basic_calculations():
    """Test basic calculation functions."""
    # Test percentage change calculation
    def calculate_percentage_change(old_value, new_value):
        if old_value == 0:
            return 0
        return ((new_value - old_value) / old_value) * 100

    assert calculate_percentage_change(100, 105) == 5.0
    assert calculate_percentage_change(200, 190) == -5.0
    assert calculate_percentage_change(0, 10) == 0