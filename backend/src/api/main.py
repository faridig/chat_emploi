"""Point d'entrée principal FastAPI."""

import logging
import time
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import make_asgi_app
from starlette.middleware.base import BaseHTTPMiddleware

# Import des métriques
from src.monitoring.metrics import (
    API_LATENCY,
)

# Configuration logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


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
    logger.info("Starting Chat Emploi backend...")
    logger.info("Prometheus metrics available at /metrics")

    yield

    # Shutdown
    logger.info("Shutting down Chat Emploi backend...")


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
    return {"message": "Chat Emploi Backend API", "version": "0.1.0"}


@app.get("/health")
async def health() -> dict[str, str]:
    """Endpoint de santé."""
    return {"status": "healthy"}
