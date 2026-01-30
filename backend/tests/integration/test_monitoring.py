"""Integration tests for monitoring features."""

import pytest
from api.main import app
from fastapi.testclient import TestClient


@pytest.fixture
def client():
    """Fixture providing a test client."""
    return TestClient(app)


def test_metrics_endpoint_returns_200(client):
    """Test that /metrics endpoint returns HTTP 200."""
    response = client.get("/metrics")
    assert response.status_code == 200
    assert (
        response.headers["content-type"] == "text/plain; version=0.0.4; charset=utf-8"
    )


def test_metrics_contains_expected_metrics(client):
    """Test that /metrics endpoint contains expected metric names."""
    response = client.get("/metrics")
    content = response.text

    # Vérifier la présence de métriques clés (au moins une)
    expected_patterns = [
        "cv_processed",
        "offers_fetched",
        "letters_generated",
        "api_latency_seconds",
        "rag_matching_seconds",
        "llm_generation_seconds",
    ]

    for pattern in expected_patterns:
        assert (
            pattern in content
        ), f"Metric pattern '{pattern}' not found in metrics output"


def test_metrics_increment_on_api_call(client):
    """Test that API calls increment metrics."""
    # Faire un appel API
    response = client.get("/")
    assert response.status_code == 200

    # Vérifier que l'endpoint metrics fonctionne toujours
    metrics_response = client.get("/metrics")
    assert metrics_response.status_code == 200
    assert "text/plain" in metrics_response.headers["content-type"]


def test_health_endpoint_works(client):
    """Test that health endpoint returns healthy status."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


def test_root_endpoint_works(client):
    """Test that root endpoint returns version info."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "version" in data
    assert data["version"] == "0.1.0"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
