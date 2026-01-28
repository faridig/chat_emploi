"""Point d'entrée principal FastAPI."""

import time
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import make_asgi_app
from starlette.middleware.base import BaseHTTPMiddleware

# Import des métriques
from src.monitoring.metrics import (
    API_LATENCY,
)

# Configuration structlog pour logs structurés
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer(),
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

# Logger structlog
logger = structlog.get_logger(__name__)


# Middleware pour les métriques
class MetricsMiddleware(BaseHTTPMiddleware):
    """Middleware pour collecter les métriques d'API."""

    async def dispatch(self, request: Request, call_next):
        start_time = time.time()

        # Exécuter la requête
        response = await call_next(request)

        # Calculer la durée
        duration = time.time() - start_time

        # Enregistrer la latence
        API_LATENCY.labels(
            endpoint=request.url.path,
            method=request.method,
            status_code=response.status_code,
        ).observe(duration)

        return response


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Gestion du cycle de vie de l'application."""
    # Startup
    logger.info("starting_backend", version="0.1.0", service="chat-emploi-backend")
    logger.info("prometheus_metrics_available", endpoint="/metrics", port=8000)

    # Log des métriques configurées
    logger.debug(
        "metrics_configured",
        counters=["cv_processed", "offers_fetched", "letters_generated"],
        histograms=[
            "api_latency_seconds",
            "rag_matching_seconds",
            "llm_generation_seconds",
        ],
        gauges=[
            "match_score_current",
            "letter_quality_score",
            "user_satisfaction_score",
        ],
    )

    yield

    # Shutdown
    logger.info("shutting_down_backend", service="chat-emploi-backend")


# Création de l'application FastAPI
app = FastAPI(
    title="Chat Emploi Backend",
    description="Backend Python pour l'application Chat Emploi",
    version="0.1.0",
    lifespan=lifespan,
)

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # À restreindre en production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Middleware pour les métriques
app.add_middleware(MetricsMiddleware)

# Application ASGI pour les métriques Prometheus
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)


@app.get("/")
async def root() -> dict[str, str]:
    """Endpoint racine."""
    logger.info("root_endpoint_called", client_ip="localhost")
    return {"message": "Chat Emploi Backend API", "version": "0.1.0"}


@app.get("/health")
async def health() -> dict[str, str]:
    """Endpoint de santé."""
    logger.debug("health_check_called")
    return {"status": "healthy"}


@app.get("/api/test/logs")
async def test_logs() -> dict[str, str]:
    """Endpoint pour tester les logs structurés."""
    logger.debug("test_log_debug", test_data="debug_message")
    logger.info("test_log_info", test_data="info_message", user="test_user")
    logger.warning("test_log_warning", test_data="warning_message", severity="medium")
    logger.error("test_log_error", test_data="error_message", error_code="TEST_001")

    # Test avec exception
    try:
        raise ValueError("Test exception for structured logging")
    except ValueError as e:
        logger.exception("test_exception_log", error=str(e), context="test_endpoint")

    return {
        "status": "logs_generated",
        "message": "Check application logs for structured output",
    }
