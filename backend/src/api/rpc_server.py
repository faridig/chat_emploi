"""Point d'entrée principal du serveur JSON-RPC pour Chat Emploi."""

import os
import sys
from pathlib import Path
from typing import Any

# Ajouter le répertoire parent au PYTHONPATH pour les imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import structlog

from src.api.jsonrpc_server import JSONRPCServer

logger = structlog.get_logger(__name__)


def get_config() -> dict[str, Any]:
    """Récupère la configuration depuis les variables d'environnement.

    Returns:
        Dictionnaire de configuration
    """
    return {
        "gemini_api_key": os.environ.get("GEMINI_API_KEY", "test-key"),
        "chromadb_persist_directory": os.environ.get(
            "CHROMADB_PERSIST_DIRECTORY", str(Path.home() / ".chat_emploi" / "chromadb")
        ),
        "redis_host": os.environ.get("REDIS_HOST", "localhost"),
        "redis_port": int(os.environ.get("REDIS_PORT", "6379")),
        "redis_db": int(os.environ.get("REDIS_DB", "0")),
    }


def register_all_methods(server: JSONRPCServer, config: dict[str, Any]) -> None:
    """Enregistre toutes les méthodes JSON-RPC disponibles.

    Args:
        server: Instance du serveur JSON-RPC
        config: Configuration des services
    """
    # Initialiser les services avec la configuration
    try:
        from src.services.cv.cv_service import CVService

        cv_service = CVService(api_key=config["gemini_api_key"])

        # Enregistrer les méthodes CV
        server.register_method("cv.analyze_cv_text", cv_service.analyze_cv_text)
        server.register_method("cv.extract_skills", cv_service.extract_skills)
        logger.debug("cv_methods_registered")

    except ImportError as e:
        logger.warning("cv_service_not_available", error=str(e))
    except Exception as e:
        logger.error("failed_to_initialize_cv_service", error=str(e))

    try:
        from src.services.embedding.embedding_service import EmbeddingService

        embedding_service = EmbeddingService(api_key=config["gemini_api_key"])

        # Enregistrer les méthodes Embedding
        server.register_method("embedding.embed_text", embedding_service.embed_text)
        server.register_method(
            "embedding.embed_text_batch", embedding_service.embed_text_batch
        )
        logger.debug("embedding_methods_registered")

    except ImportError as e:
        logger.warning("embedding_service_not_available", error=str(e))
    except Exception as e:
        logger.error("failed_to_initialize_embedding_service", error=str(e))

    try:
        from src.services.vector_store.vector_store_service import VectorStoreService

        vector_store_service = VectorStoreService(
            persist_directory=config["chromadb_persist_directory"]
        )

        # Enregistrer les méthodes Vector Store
        server.register_method(
            "vector_store.add_embeddings", vector_store_service.add_embeddings
        )
        server.register_method(
            "vector_store.query_similarity", vector_store_service.query_similarity
        )
        server.register_method(
            "vector_store.get_collection_stats",
            vector_store_service.get_collection_stats,
        )
        logger.debug("vector_store_methods_registered")

    except ImportError as e:
        logger.warning("vector_store_service_not_available", error=str(e))
    except Exception as e:
        logger.error("failed_to_initialize_vector_store_service", error=str(e))

    try:
        from src.services.cache.cache_service import CacheService

        redis_url = f"redis://{config['redis_host']}:{config['redis_port']}/{config['redis_db']}"
        cache_service = CacheService(redis_url=redis_url)

        # Enregistrer les méthodes Cache
        server.register_method("cache.get", cache_service.get)
        server.register_method("cache.set", cache_service.set)
        server.register_method("cache.delete", cache_service.delete)
        server.register_method("cache.clear_cache", cache_service.clear_cache)
        logger.debug("cache_methods_registered")

    except ImportError as e:
        logger.warning("cache_service_not_available", error=str(e))
    except Exception as e:
        logger.error("failed_to_initialize_cache_service", error=str(e))

    # Méthodes de test
    server.register_method("test.ping", _ping_method)
    server.register_method("test.echo", _echo_method)

    logger.info("all_methods_registered", count=len(server.methods))


def _ping_method(params: dict) -> dict:
    """Méthode de test ping.

    Args:
        params: Paramètres de la méthode

    Returns:
        Résultat avec timestamp
    """
    import time

    return {
        "status": "pong",
        "timestamp": time.time(),
        "service": "chat-emploi-backend",
    }


def _echo_method(params: dict) -> dict:
    """Méthode de test echo.

    Args:
        params: Paramètres de la méthode

    Returns:
        Même paramètres reçus
    """
    return {"echo": params}


def main() -> None:
    """Point d'entrée principal du serveur JSON-RPC."""
    logger.info("starting_jsonrpc_server", version="0.1.0")

    # Créer le serveur
    server = JSONRPCServer()

    # Récupérer la configuration
    config = get_config()

    # Enregistrer toutes les méthodes
    register_all_methods(server, config)

    # Lancer la boucle principale
    logger.info("jsonrpc_server_ready", methods=list(server.methods.keys()))
    server.run()


if __name__ == "__main__":
    main()
