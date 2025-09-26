"""
Unit tests for stock API endpoints.
"""
import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient


@pytest.mark.unit
def test_get_stock_info_success(client: TestClient, sample_stock_data):
    """Test successful stock info retrieval."""
    with patch('functions.main.get_stock_info') as mock_get_stock:
        mock_get_stock.return_value = sample_stock_data

        response = client.get("/api/stocks/AAPL")
        assert response.status_code == 200

        data = response.json()
        assert data["symbol"] == "AAPL"
        assert "price" in data


@pytest.mark.unit
def test_get_stock_info_not_found(client: TestClient):
    """Test stock not found scenario."""
    with patch('functions.main.get_stock_info') as mock_get_stock:
        mock_get_stock.return_value = None

        response = client.get("/api/stocks/INVALID")
        assert response.status_code == 404

        data = response.json()
        assert "detail" in data


@pytest.mark.unit
def test_get_stock_prediction_success(client: TestClient, sample_prediction_data):
    """Test successful stock prediction retrieval."""
    with patch('functions.main.get_stock_prediction') as mock_prediction:
        mock_prediction.return_value = sample_prediction_data

        response = client.get("/api/predictions/AAPL")
        assert response.status_code == 200

        data = response.json()
        assert data["symbol"] == "AAPL"
        assert "predicted_price" in data
        assert "confidence_score" in data


@pytest.mark.unit
def test_get_stock_prediction_not_found(client: TestClient):
    """Test prediction not found scenario."""
    with patch('functions.main.get_stock_prediction') as mock_prediction:
        mock_prediction.return_value = None

        response = client.get("/api/predictions/INVALID")
        assert response.status_code == 404


@pytest.mark.unit
def test_stock_symbol_validation(client: TestClient):
    """Test stock symbol validation."""
    # Test invalid characters
    response = client.get("/api/stocks/INVALID@SYMBOL")
    assert response.status_code in [400, 422]

    # Test too long symbol
    response = client.get("/api/stocks/TOOLONGSYMBOL")
    assert response.status_code in [400, 422]


@pytest.mark.unit
def test_get_stock_rankings_success(client: TestClient):
    """Test stock rankings endpoint."""
    mock_rankings = [
        {"symbol": "AAPL", "score": 95, "rank": 1},
        {"symbol": "GOOGL", "score": 88, "rank": 2},
        {"symbol": "MSFT", "score": 85, "rank": 3}
    ]

    with patch('functions.main.get_stock_rankings') as mock_rankings_func:
        mock_rankings_func.return_value = mock_rankings

        response = client.get("/api/rankings")
        assert response.status_code == 200

        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 3
        assert data[0]["rank"] == 1


@pytest.mark.unit
def test_search_stocks_success(client: TestClient):
    """Test stock search functionality."""
    mock_results = [
        {"symbol": "AAPL", "name": "Apple Inc.", "match_score": 1.0},
        {"symbol": "APP", "name": "AppLovin Corporation", "match_score": 0.8}
    ]

    with patch('functions.main.search_stocks') as mock_search:
        mock_search.return_value = mock_results

        response = client.get("/api/search?q=apple")
        assert response.status_code == 200

        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 2
        assert data[0]["symbol"] == "AAPL"


@pytest.mark.unit
def test_search_stocks_empty_query(client: TestClient):
    """Test search with empty query."""
    response = client.get("/api/search?q=")
    assert response.status_code == 400

    response = client.get("/api/search")
    assert response.status_code == 422  # Missing required parameter