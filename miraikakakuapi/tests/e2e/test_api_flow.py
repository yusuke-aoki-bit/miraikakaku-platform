"""
End-to-end tests for complete API workflows.
"""
import pytest
from fastapi.testclient import TestClient


@pytest.mark.e2e
def test_complete_stock_workflow(client: TestClient):
    """Test complete workflow: search -> get stock -> get prediction."""
    # 1. Search for a stock
    search_response = client.get("/api/search?q=apple")
    assert search_response.status_code == 200

    search_data = search_response.json()
    if search_data:
        symbol = search_data[0]["symbol"]

        # 2. Get stock information
        stock_response = client.get(f"/api/stocks/{symbol}")
        if stock_response.status_code == 200:
            stock_data = stock_response.json()
            assert stock_data["symbol"] == symbol

            # 3. Get prediction for the stock
            prediction_response = client.get(f"/api/predictions/{symbol}")
            if prediction_response.status_code == 200:
                prediction_data = prediction_response.json()
                assert prediction_data["symbol"] == symbol


@pytest.mark.e2e
def test_rankings_to_details_workflow(client: TestClient):
    """Test workflow from rankings to stock details."""
    # 1. Get stock rankings
    rankings_response = client.get("/api/rankings")
    assert rankings_response.status_code == 200

    rankings = rankings_response.json()
    if rankings:
        top_stock = rankings[0]
        symbol = top_stock["symbol"]

        # 2. Get detailed information for top-ranked stock
        details_response = client.get(f"/api/stocks/{symbol}")
        if details_response.status_code == 200:
            details = details_response.json()
            assert details["symbol"] == symbol

            # 3. Verify ranking data matches details
            assert "score" in top_stock or "rank" in top_stock


@pytest.mark.e2e
def test_health_check_comprehensive(client: TestClient):
    """Test comprehensive health check workflow."""
    # 1. Basic health check
    health_response = client.get("/api/system/health")
    assert health_response.status_code == 200

    health_data = health_response.json()
    assert "status" in health_data

    # 2. If system is healthy, test main endpoints
    if health_data.get("status") == "healthy":
        # Test core endpoints work
        endpoints_to_test = [
            "/api/rankings",
            "/api/search?q=test"
        ]

        for endpoint in endpoints_to_test:
            response = client.get(endpoint)
            # Should not return 5xx errors if system is healthy
            assert response.status_code < 500


@pytest.mark.e2e
@pytest.mark.slow
def test_api_response_times(client: TestClient):
    """Test API response times are within acceptable limits."""
    import time

    endpoints = [
        "/api/system/health",
        "/api/rankings",
        "/api/search?q=apple"
    ]

    for endpoint in endpoints:
        start_time = time.time()
        response = client.get(endpoint)
        end_time = time.time()

        response_time = end_time - start_time

        # Health check should be fast
        if "health" in endpoint:
            assert response_time < 1.0  # Should respond within 1 second

        # Other endpoints should be reasonably fast
        else:
            assert response_time < 5.0  # Should respond within 5 seconds

        # All endpoints should return valid responses
        assert response.status_code < 500


@pytest.mark.e2e
def test_error_handling_workflow(client: TestClient):
    """Test error handling across different scenarios."""
    # 1. Test invalid stock symbol
    response = client.get("/api/stocks/INVALIDSTOCK123")
    assert response.status_code in [404, 422]

    error_data = response.json()
    assert "detail" in error_data or "error" in error_data

    # 2. Test malformed requests
    response = client.get("/api/search")  # Missing required query parameter
    assert response.status_code == 422

    # 3. Test non-existent endpoints
    response = client.get("/api/nonexistent")
    assert response.status_code == 404


@pytest.mark.e2e
def test_data_consistency(client: TestClient):
    """Test data consistency across different endpoints."""
    # Get rankings
    rankings_response = client.get("/api/rankings")
    if rankings_response.status_code == 200:
        rankings = rankings_response.json()

        if rankings:
            # Pick first stock from rankings
            first_stock = rankings[0]
            symbol = first_stock["symbol"]

            # Get detailed stock info
            stock_response = client.get(f"/api/stocks/{symbol}")
            if stock_response.status_code == 200:
                stock_data = stock_response.json()

                # Verify symbol consistency
                assert stock_data["symbol"] == symbol

                # Basic data validation
                if "price" in stock_data:
                    assert isinstance(stock_data["price"], (int, float))
                    assert stock_data["price"] > 0