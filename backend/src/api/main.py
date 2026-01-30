"""Point d'entrée principal FastAPI."""

import time
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# Import des métriques
from monitoring.metrics import (
    API_LATENCY,
)
from prometheus_client import make_asgi_app
from starlette.middleware.base import BaseHTTPMiddleware

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


@app.get("/api/status")
async def api_status() -> dict:
    """Endpoint de statut de l'API."""
    logger.info("api_status_called")
    return {
        "status": "operational",
        "version": "0.1.0",
        "services": {
            "api": "running",
            "database": "connected",  # À vérifier dynamiquement
            "monitoring": "enabled",
        },
        "timestamp": time.time(),
    }


@app.get("/api/debug/metrics")
async def debug_metrics() -> dict:
    """Endpoint de debug pour les métriques."""
    logger.debug("debug_metrics_called")

    # Récupérer les métriques Prometheus (exemple simplifié)
    import io

    from prometheus_client import generate_latest

    io.StringIO()
    generate_latest().decode("utf-8")

    return {
        "metrics_available": True,
        "endpoints": {
            "prometheus": "/metrics",
            "health": "/health",
            "status": "/api/status",
        },
    }


@app.post("/api/test/jsonrpc")
async def test_jsonrpc(request: dict) -> dict:
    """Endpoint de test pour le protocole JSON-RPC.

    Note: Cet endpoint est pour le test uniquement, la communication réelle
    se fait via stdin/stdout avec le serveur JSON-RPC dédié.
    """
    logger.info("test_jsonrpc_called", method=request.get("method"))

    # Simuler une réponse JSON-RPC
    method = request.get("method", "")
    params = request.get("params", {})

    if method == "test.ping":
        return {
            "jsonrpc": "2.0",
            "result": {"status": "pong", "timestamp": time.time()},
            "id": request.get("id"),
        }
    elif method == "test.echo":
        return {"jsonrpc": "2.0", "result": {"echo": params}, "id": request.get("id")}
    else:
        raise HTTPException(
            status_code=400,
            detail={
                "jsonrpc": "2.0",
                "error": {"code": -32601, "message": "Method not found"},
                "id": request.get("id"),
            },
        )


@app.get("/api/docs")
async def api_docs_redirect():
    """Redirige vers la documentation OpenAPI."""
    from starlette.responses import RedirectResponse

    return RedirectResponse(url="/docs")


# Handler d'erreurs global
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handler d'erreurs HTTP personnalisé."""
    logger.error(
        "http_exception",
        status_code=exc.status_code,
        detail=exc.detail,
        path=request.url.path,
    )

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": exc.status_code,
                "message": str(exc.detail),
                "path": request.url.path,
            }
        },
    )


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    """Handler d'exceptions génériques."""
    logger.exception("unhandled_exception", error=str(exc), path=request.url.path)

    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "code": 500,
                "message": "Internal server error",
                "path": request.url.path,
            }
        },
    )
