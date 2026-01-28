"""Point d'entrée principal FastAPI."""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Configuration logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gestion du cycle de vie de l'application."""
    # Startup
    logger.info("Starting Chat Emploi backend...")
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


@app.get("/")
async def root():
    """Endpoint racine."""
    return {"message": "Chat Emploi Backend API", "version": "0.1.0"}


@app.get("/health")
async def health():
    """Endpoint de santé."""
    return {"status": "healthy"}