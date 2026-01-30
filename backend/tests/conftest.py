"""
Configuration globale pour les tests pytest.
Gère les imports optionnels et les mocks pour les tests CI/CD.
"""

import os
import sys
from unittest.mock import MagicMock

import pytest

# Configuration des variables d'environnement pour les tests
os.environ.setdefault("TEST_MODE", "true")
os.environ.setdefault("SKIP_EXTERNAL_APIS", "true")


# Mock des imports optionnels pour les tests
def mock_optional_imports():
    """Mock les imports optionnels qui peuvent manquer en CI/CD."""

    # Mock pour google.generativeai
    google_mock = MagicMock()
    google_mock.genai = MagicMock()
    google_mock.genai.configure = MagicMock()
    google_mock.genai.GenerativeModel = MagicMock(
        return_value=MagicMock(
            generate_content=MagicMock(return_value=MagicMock(text="Mocked response"))
        )
    )

    # Mock pour chromadb
    chromadb_mock = MagicMock()
    chromadb_mock.PersistentClient = MagicMock(
        return_value=MagicMock(
            get_or_create_collection=MagicMock(
                return_value=MagicMock(
                    add=MagicMock(),
                    query=MagicMock(
                        return_value={
                            "documents": [["Mocked document"]],
                            "metadatas": [[{"source": "test"}]],
                            "distances": [[0.1]],
                        }
                    ),
                    count=MagicMock(return_value=0),
                )
            )
        )
    )

    # Mock pour crewai
    crewai_mock = MagicMock()
    crewai_mock.Agent = MagicMock()
    crewai_mock.Task = MagicMock()
    crewai_mock.Crew = MagicMock(
        return_value=MagicMock(kickoff=MagicMock(return_value="Mocked crew output"))
    )

    # Mock pour llama_index
    llama_mock = MagicMock()
    llama_mock.ServiceContext = MagicMock()
    llama_mock.StorageContext = MagicMock()
    llama_mock.VectorStoreIndex = MagicMock()

    # Appliquer les mocks
    mock_modules = {
        "google.generativeai": google_mock,
        "chromadb": chromadb_mock,
        "crewai": crewai_mock,
        "llama_index": llama_mock,
        "langgraph": MagicMock(),
        "spacy": MagicMock(),
    }

    for module_name, mock_obj in mock_modules.items():
        sys.modules[module_name] = mock_obj


# Appeler la fonction pour mock les imports
mock_optional_imports()


# Configuration pytest
def pytest_configure(config):
    """Configuration pytest."""
    config.addinivalue_line("markers", "integration: mark test as integration test")
    config.addinivalue_line("markers", "e2e: mark test as end-to-end test")
    config.addinivalue_line("markers", "slow: mark test as slow running")
    config.addinivalue_line(
        "markers", "requires_external_api: test requires external API"
    )


def pytest_collection_modifyitems(config, items):
    """Modifie la collection de tests en fonction des marqueurs."""
    skip_integration = os.getenv("SKIP_INTEGRATION_TESTS", "false").lower() == "true"
    skip_e2e = os.getenv("SKIP_E2E_TESTS", "true").lower() == "true"
    skip_slow = os.getenv("SKIP_SLOW_TESTS", "true").lower() == "true"
    skip_external = os.getenv("SKIP_EXTERNAL_APIS", "true").lower() == "true"

    skip_markers = []
    if skip_integration:
        skip_markers.append("integration")
    if skip_e2e:
        skip_markers.append("e2e")
    if skip_slow:
        skip_markers.append("slow")
    if skip_external:
        skip_markers.append("requires_external_api")

    for item in items:
        for marker in skip_markers:
            if marker in item.keywords:
                item.add_marker(
                    pytest.mark.skip(reason=f"Skipping {marker} tests in CI")
                )
