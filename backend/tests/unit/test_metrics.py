"""Tests for monitoring metrics."""

import pytest
from prometheus_client.registry import REGISTRY

from src.monitoring.metrics import (
    API_LATENCY,
    CV_PROCESSED,
    LETTER_QUALITY,
    MATCH_SCORE,
    OFFERS_FETCHED,
)


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
    initial_value = CV_PROCESSED._value.get()
    CV_PROCESSED.inc()
    assert CV_PROCESSED._value.get() == initial_value + 1

    # Test avec labels
    OFFERS_FETCHED.labels(source="france_travail").inc()
    assert OFFERS_FETCHED.labels(source="france_travail")._value.get() == 1


def test_histogram_observation():
    """Test that histograms can record observations."""
    # Enregistrer une observation
    API_LATENCY.labels(endpoint="/test").observe(0.5)

    # Vérifier que l'histogramme a des données
    samples = list(API_LATENCY.labels(endpoint="/test")._buckets)
    assert len(samples) > 0


def test_gauge_set():
    """Test that gauges can be set to values."""
    MATCH_SCORE.set(0.85)
    assert MATCH_SCORE._value.get() == 0.85

    # Test avec labels
    LETTER_QUALITY.labels(document_type="cover_letter").set(0.92)
    assert LETTER_QUALITY.labels(document_type="cover_letter")._value.get() == 0.92


def test_metrics_endpoint_integration():
    """Test that metrics endpoint returns expected metrics."""
    # Ce test nécessite l'application FastAPI avec les métriques montées
    # À implémenter dans tests d'intégration
    pass


def test_metrics_labels():
    """Test that metrics with labels work correctly."""
    # Test counter avec labels
    OFFERS_FETCHED.labels(source="france_travail").inc()
    OFFERS_FETCHED.labels(source="web_scraped").inc(2)

    assert OFFERS_FETCHED.labels(source="france_travail")._value.get() == 1
    assert OFFERS_FETCHED.labels(source="web_scraped")._value.get() == 2

    # Test histogram avec labels
    API_LATENCY.labels(endpoint="/api/cv", method="POST").observe(1.2)
    API_LATENCY.labels(endpoint="/api/offers", method="GET").observe(0.3)

    # Vérifier que les buckets existent pour chaque label
    samples_post = list(API_LATENCY.labels(endpoint="/api/cv", method="POST")._buckets)
    samples_get = list(
        API_LATENCY.labels(endpoint="/api/offers", method="GET")._buckets
    )
    assert len(samples_post) > 0
    assert len(samples_get) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
