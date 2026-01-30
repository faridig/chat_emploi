"""Tests for monitoring metrics."""

import pytest
from monitoring.metrics import (
    API_LATENCY,
    CV_PROCESSED,
    LETTER_QUALITY,
    MATCH_SCORE,
    OFFERS_FETCHED,
)
from prometheus_client.registry import REGISTRY


def test_metrics_registered():
    """Test that all expected metrics are registered in Prometheus registry."""
    # Vérifier que les métriques sont dans le registre
    metric_names = {m.name for m in REGISTRY.collect()}

    expected_metrics = {
        "cv_processed",  # Counter: _total suffix is removed by client
        "offers_fetched",  # Counter: _total suffix is removed by client
        "letters_generated",  # Counter: _total suffix is removed by client
        "api_latency_seconds",
        "rag_matching_seconds",
        "llm_generation_seconds",
        "match_score_current",
        "letter_quality_score",
        "user_satisfaction_score",
        "memory_usage_bytes",
        "cpu_usage_percent",
        "disk_usage_bytes",
    }

    # Vérifier que chaque métrique attendue est présente
    for metric in expected_metrics:
        assert metric in metric_names, f"Metric '{metric}' not found in registry"


def test_counter_increment():
    """Test that counters can be incremented."""
    # Test avec labels - vérifier que l'appel ne lève pas d'exception
    CV_PROCESSED.labels(anonymization_method="auto").inc()
    OFFERS_FETCHED.labels(source="france_travail").inc()

    # Vérifier que les métriques sont dans le registre
    metric_names = {m.name for m in REGISTRY.collect()}
    assert "offers_fetched" in metric_names
    assert "cv_processed" in metric_names


def test_histogram_observation():
    """Test that histograms can record observations."""
    # Enregistrer une observation - vérifier que l'appel ne lève pas d'exception
    API_LATENCY.labels(endpoint="/test", method="GET", status_code=200).observe(0.5)

    # Vérifier que la métrique est dans le registre
    metric_names = {m.name for m in REGISTRY.collect()}
    assert "api_latency_seconds" in metric_names


def test_gauge_set():
    """Test that gauges can be set to values."""
    # Test gauge sans labels
    MATCH_SCORE.labels(search_id="test_search").set(0.85)

    # Test avec labels
    LETTER_QUALITY.labels(document_type="cover_letter").set(0.92)

    # Vérifier que les métriques sont dans le registre
    metric_names = {m.name for m in REGISTRY.collect()}
    assert "match_score_current" in metric_names
    assert "letter_quality_score" in metric_names


def test_metrics_endpoint_integration():
    """Test that metrics endpoint returns expected metrics."""
    # Ce test nécessite l'application FastAPI avec les métriques montées
    # À implémenter dans tests d'intégration
    pass


def test_metrics_labels():
    """Test that metrics with labels work correctly."""
    # Test counter avec labels - vérifier que les appels ne lèvent pas d'exception
    OFFERS_FETCHED.labels(source="france_travail").inc()
    OFFERS_FETCHED.labels(source="web_scraped").inc(2)

    # Test histogram avec labels
    API_LATENCY.labels(endpoint="/api/cv", method="POST", status_code=200).observe(1.2)
    API_LATENCY.labels(endpoint="/api/offers", method="GET", status_code=200).observe(
        0.3
    )

    # Vérifier que les métriques sont dans le registre
    metric_names = {m.name for m in REGISTRY.collect()}
    assert "offers_fetched" in metric_names
    assert "api_latency_seconds" in metric_names


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
