"""Tests d'intégration système complets pour Chat Emploi."""

import time

from api.main import app
from fastapi.testclient import TestClient


class TestSystemIntegration:
    """Tests d'intégration système complets."""

    def setup_method(self):
        """Initialisation avant chaque test."""
        self.client = TestClient(app)

    def test_full_user_journey_mocked(self):
        """Test complet du parcours utilisateur avec mocks."""
        # Pour ce test d'intégration système, nous testons juste que l'API répond
        # Les mocks complets des services seront dans les tests unitaires

        # Étape 1: Vérifier que l'API est en ligne
        response = self.client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"

        # Étape 2: Vérifier le statut de l'API
        response = self.client.get("/api/status")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "operational"
        assert "services" in data

        # Étape 3: Tester l'endpoint JSON-RPC avec méthode ping
        request = {"jsonrpc": "2.0", "method": "test.ping", "params": {}, "id": 1}
        response = self.client.post("/api/test/jsonrpc", json=request)
        assert response.status_code == 200
        data = response.json()
        assert data["result"]["status"] == "pong"

        # Étape 4: Tester l'endpoint JSON-RPC avec méthode echo
        request = {
            "jsonrpc": "2.0",
            "method": "test.echo",
            "params": {"text": "Hello System Test"},
            "id": 2,
        }
        response = self.client.post("/api/test/jsonrpc", json=request)
        assert response.status_code == 200
        data = response.json()
        assert data["result"]["echo"]["text"] == "Hello System Test"

        print("✅ Parcours utilisateur de base testé avec succès")

    def test_api_metrics_endpoint(self):
        """Test que les métriques Prometheus sont disponibles."""
        response = self.client.get("/metrics")

        assert response.status_code == 200
        assert "text/plain" in response.headers["content-type"]

        # Vérifier que certaines métriques de base sont présentes
        metrics_text = response.text
        assert "python_gc_" in metrics_text or "process_" in metrics_text

        print("✅ Endpoint /metrics fonctionnel")

    def test_api_documentation(self):
        """Test que la documentation OpenAPI est disponible."""
        # Test de la documentation Swagger UI
        response = self.client.get("/docs")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]

        # Test du schéma OpenAPI JSON
        response = self.client.get("/openapi.json")
        assert response.status_code == 200
        schema = response.json()

        # Vérifier la structure de base
        assert "openapi" in schema
        assert "info" in schema
        assert "paths" in schema

        info = schema["info"]
        assert info["title"] == "Chat Emploi Backend"
        assert info["version"] == "0.1.0"

        print("✅ Documentation OpenAPI disponible")

    def test_cors_headers(self):
        """Test que les headers CORS sont correctement configurés."""
        # Tester avec une origine spécifique
        response = self.client.get(
            "/health", headers={"Origin": "http://localhost:3000"}
        )

        # Vérifier les headers CORS
        assert "access-control-allow-origin" in response.headers
        assert response.headers["access-control-allow-origin"] == "*"

        print("✅ Headers CORS configurés correctement")

    def test_error_handling_system(self):
        """Test du système de gestion d'erreurs."""
        # Test 1: Route inexistante
        response = self.client.get("/api/nonexistent")
        assert response.status_code == 404

        # Test 2: Méthode non supportée
        response = self.client.post("/health")
        assert response.status_code == 405

        # Test 3: Requête JSON-RPC invalide
        response = self.client.post("/api/test/jsonrpc", json={"invalid": "request"})
        assert response.status_code == 400

        print("✅ Système de gestion d'erreurs fonctionnel")

    def test_concurrent_api_requests(self):
        """Test de requêtes API concurrentes."""
        import concurrent.futures

        def make_health_request():
            response = self.client.get("/health")
            return response.status_code

        # Faire 10 requêtes concurrentes
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(make_health_request) for _ in range(10)]
            results = [
                future.result() for future in concurrent.futures.as_completed(futures)
            ]

        # Toutes les requêtes devraient réussir
        assert all(status == 200 for status in results)

        print(f"✅ {len(results)} requêtes concurrentes traitées avec succès")

    def test_api_response_times(self):
        """Test des temps de réponse de l'API."""
        endpoints_to_test = [
            ("GET", "/health"),
            ("GET", "/api/status"),
            ("GET", "/metrics"),
        ]

        max_response_time = 1000  # 1 seconde

        for method, endpoint in endpoints_to_test:
            start_time = time.time()

            if method == "GET":
                response = self.client.get(endpoint)
            else:
                response = self.client.post(endpoint)

            end_time = time.time()
            response_time = (end_time - start_time) * 1000  # ms

            assert response.status_code in [200, 307], f"Endpoint {endpoint} a échoué"
            assert (
                response_time < max_response_time
            ), f"Endpoint {endpoint} trop lent: {response_time:.2f}ms"

            print(f"  {endpoint}: {response_time:.2f}ms")

        print("✅ Tous les endpoints répondent dans les temps")

    def test_system_health_endpoints(self):
        """Test des différents endpoints de santé."""
        # Test endpoint de santé principal
        response = self.client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"

        # Test endpoint de statut détaillé
        response = self.client.get("/api/status")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "operational"
        assert "timestamp" in data
        assert "services" in data

        # Test endpoint de debug
        response = self.client.get("/api/debug/metrics")
        assert response.status_code == 200
        data = response.json()
        assert data["metrics_available"] is True

        print("✅ Endpoints de santé fonctionnels")

    def test_jsonrpc_protocol_compliance(self):
        """Test de conformité au protocole JSON-RPC 2.0."""
        # Test 1: Requête valide avec méthode ping
        valid_request = {"jsonrpc": "2.0", "method": "test.ping", "params": {}, "id": 1}

        response = self.client.post("/api/test/jsonrpc", json=valid_request)
        assert response.status_code == 200
        data = response.json()

        # Vérifier la conformité JSON-RPC
        assert data["jsonrpc"] == "2.0"
        assert data["id"] == 1
        assert "result" in data
        assert data["result"]["status"] == "pong"

        # Test 2: Requête avec méthode inconnue
        invalid_request = {
            "jsonrpc": "2.0",
            "method": "unknown.method",
            "params": {},
            "id": 2,
        }

        response = self.client.post("/api/test/jsonrpc", json=invalid_request)
        # Devrait retourner une erreur
        assert response.status_code == 400

        print("✅ Conformité JSON-RPC 2.0 vérifiée")


def test_system_throughput():
    """Test du débit du système."""
    client = TestClient(app)

    # Mesurer le temps pour 20 requêtes
    num_requests = 20
    start_time = time.time()

    successful_requests = 0
    for _ in range(num_requests):
        response = client.get("/health")
        if response.status_code == 200:
            successful_requests += 1

    end_time = time.time()
    total_time = end_time - start_time

    # Calculer le débit
    throughput = successful_requests / total_time if total_time > 0 else 0

    print("\n📊 Test de débit système:")
    print(f"  Requêtes: {successful_requests}/{num_requests}")
    print(f"  Temps total: {total_time:.2f}s")
    print(f"  Débit: {throughput:.2f} req/s")

    # Objectif: au moins 5 req/s
    assert throughput >= 5.0, f"Débit trop faible: {throughput:.2f} req/s"
    assert successful_requests == num_requests, "Toutes les requêtes devraient réussir"

    print("✅ Débit système acceptable")


if __name__ == "__main__":
    print("🔧 Exécution des tests d'intégration système...")

    # Créer une instance de test
    test_instance = TestSystemIntegration()
    test_instance.setup_method()

    # Exécuter les tests
    test_instance.test_full_user_journey_mocked()
    test_instance.test_api_metrics_endpoint()
    test_instance.test_api_documentation()
    test_instance.test_cors_headers()
    test_instance.test_error_handling_system()
    test_instance.test_concurrent_api_requests()
    test_instance.test_api_response_times()
    test_instance.test_system_health_endpoints()
    test_instance.test_jsonrpc_protocol_compliance()

    # Exécuter le test de débit
    test_system_throughput()

    print("\n✅ Tous les tests d'intégration système passés avec succès!")
