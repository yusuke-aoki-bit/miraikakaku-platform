"""
Integration tests for API endpoints
"""
import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from decimal import Decimal

@pytest.mark.integration
class TestAPIEndpoints:
    """Test API endpoints"""

    @pytest.fixture
    def client(self):
        """Create test client"""
        # Import after environment is set
        from functions.main import app
        return TestClient(app)

    def test_health_endpoint(self, client):
        """Test health check endpoint"""
        response = client.get("/health")
        assert response.status_code == 200

        data = response.json()
        assert "status" in data
        assert data["status"] == "healthy"

    @patch('functions.main.get_stock_data')
    def test_stock_data_endpoint(self, mock_get_stock, client, sample_stock_data):
        """Test stock data endpoint"""
        mock_get_stock.return_value = sample_stock_data

        response = client.get("/stock/AAPL")
        assert response.status_code == 200

        data = response.json()
        assert data["symbol"] == "AAPL"
        assert data["name"] == "Apple Inc."
        assert "price" in data

    @patch('functions.main.get_predictions')
    def test_predictions_endpoint(self, mock_get_predictions, client):
        """Test predictions endpoint"""
        mock_predictions = [
            {
                "symbol": "AAPL",
                "predicted_price": 155.0,
                "confidence": 0.85,
                "model_name": "LSTM_v1",
                "target_date": "2023-12-31"
            }
        ]
        mock_get_predictions.return_value = mock_predictions

        response = client.get("/predictions/AAPL")
        assert response.status_code == 200

        data = response.json()
        assert len(data) == 1
        assert data[0]["symbol"] == "AAPL"
        assert data[0]["predicted_price"] == 155.0

    def test_invalid_symbol_endpoint(self, client):
        """Test API with invalid symbol"""
        response = client.get("/stock/INVALID")
        # Should handle gracefully, either 404 or error message
        assert response.status_code in [404, 400, 500]

    @patch('functions.main.search_stocks')
    def test_search_endpoint(self, mock_search, client):
        """Test stock search endpoint"""
        mock_search.return_value = [
            {"symbol": "AAPL", "name": "Apple Inc."},
            {"symbol": "AMZN", "name": "Amazon.com Inc."}
        ]

        response = client.get("/search?q=app")
        assert response.status_code == 200

        data = response.json()
        assert len(data) == 2
        assert data[0]["symbol"] == "AAPL"