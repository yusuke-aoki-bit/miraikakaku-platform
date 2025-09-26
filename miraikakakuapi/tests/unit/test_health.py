"""
Unit tests for health check endpoint.
"""
import pytest
from fastapi.testclient import TestClient


@pytest.mark.unit
def test_health_endpoint(client: TestClient):
    """Test health check endpoint returns 200."""
    response = client.get("/api/system/health")
    assert response.status_code == 200

    data = response.json()
    assert "status" in data
    assert data["status"] in ["healthy", "degraded", "unhealthy"]
    assert "timestamp" in data
    assert "version" in data


@pytest.mark.unit
def test_health_endpoint_structure(client: TestClient):
    """Test health endpoint returns proper structure."""
    response = client.get("/api/system/health")
    assert response.status_code == 200

    data = response.json()
    required_fields = ["status", "timestamp", "version", "uptime", "checks"]
    for field in required_fields:
        assert field in data, f"Missing required field: {field}"


@pytest.mark.unit
def test_health_check_components(client: TestClient):
    """Test health check includes component status."""
    response = client.get("/api/system/health")
    assert response.status_code == 200

    data = response.json()
    assert "checks" in data

    # Validate checks structure
    checks = data["checks"]
    assert isinstance(checks, dict)

    # Should have at least database check
    if "database" in checks:
        db_check = checks["database"]
        assert "status" in db_check
        assert "response_time_ms" in db_check