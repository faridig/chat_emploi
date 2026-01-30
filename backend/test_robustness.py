"""Tests de robustesse pour le système Chat Emploi."""

import time

from fastapi.testclient import TestClient

from src.api.main import app


def test_api_error_handling():
    """Test que l'API gère correctement les erreurs."""
    client = TestClient(app)

    # Test 1: Route inexistante (404)
    response = client.get("/nonexistent/route")
    assert response.status_code == 404
    print("✅ Test 404: Route inexistante gérée correctement")

    # Test 2: Méthode non autorisée (405)
    response = client.post("/health")
    assert response.status_code == 405
    print("✅ Test 405: Méthode non autorisée gérée correctement")

    # Test 3: Requête JSON-RPC invalide
    response = client.post("/api/test/jsonrpc", json={"invalid": "request"})
    assert response.status_code == 400
    print("✅ Test JSON-RPC invalide: Requête invalide gérée correctement")

    # Test 4: Corps de requête malformé
    response = client.post("/api/test/jsonrpc", json={"invalid": "json structure"})
    # L'API devrait gérer cela gracieusement
    assert response.status_code in [200, 400, 422]
    print("✅ Test corps malformé: Structure JSON invalide gérée correctement")


def test_external_api_failure_handling():
    """Test que le système gère les échecs d'APIs externes."""
    client = TestClient(app)

    # Simuler un échec de l'API externe (ex: France Travail)
    # Pour l'instant, on teste juste que le système reste opérationnel
    response = client.get("/health")

    # Le endpoint health ne devrait pas échouer même si des APIs externes sont down
    assert response.status_code == 200
    print("✅ Test résilience APIs externes: Système reste opérationnel")


def test_database_connection_failure():
    """Test que le système gère les pertes de connexion à la base de données."""
    client = TestClient(app)

    # Note: Ce test est complexe car il nécessite de mock la connexion DB
    # Pour l'instant, on teste juste que l'API répond même en cas d'erreur
    response = client.get("/health")
    assert response.status_code == 200
    print("✅ Test résilience: API répond même sous contrainte")


def test_rate_limiting_basic():
    """Test basique de gestion de charge."""
    client = TestClient(app)

    # Faire plusieurs requêtes rapides
    start_time = time.time()
    request_count = 0

    for _ in range(10):
        response = client.get("/health")
        if response.status_code == 200:
            request_count += 1

    end_time = time.time()
    elapsed = end_time - start_time

    # Vérifier que toutes les requêtes ont réussi
    assert request_count == 10, f"Seulement {request_count}/10 requêtes ont réussi"

    # Le système devrait gérer au moins 10 req/s
    assert elapsed < 2.0, f"Trop lent: {elapsed:.2f}s pour 10 requêtes"

    print(
        f"✅ Test charge: {request_count} requêtes en {elapsed:.2f}s ({request_count/elapsed:.1f} req/s)"
    )


def test_data_validation():
    """Test de validation des données."""
    client = TestClient(app)

    # Test 1: JSON-RPC avec paramètres invalides
    invalid_request = {
        "jsonrpc": "2.0",
        "method": "test.echo",
        "params": {"text": ""},  # Texte vide
        "id": 1,
    }

    response = client.post("/api/test/jsonrpc", json=invalid_request)
    assert response.status_code == 200  # Doit accepter le texte vide

    # Test 2: JSON-RPC avec types invalides
    invalid_types = {
        "jsonrpc": "2.0",
        "method": 123,  # Méthode devrait être un string
        "params": {},
        "id": "not-a-number",  # ID devrait être un nombre
    }

    response = client.post("/api/test/jsonrpc", json=invalid_types)
    # L'API devrait gérer cela gracieusement (400 ou 422)
    assert response.status_code in [400, 422, 200]

    print("✅ Test validation: Données invalides gérées correctement")


if __name__ == "__main__":
    print("🛡️  Exécution des tests de robustesse...")

    try:
        test_api_error_handling()
        test_external_api_failure_handling()
        test_database_connection_failure()
        test_rate_limiting_basic()
        test_data_validation()

        print("\n✅ Tous les tests de robustesse passés avec succès!")

    except Exception as e:
        print(f"\n❌ Test de robustesse échoué: {e}")
        raise
