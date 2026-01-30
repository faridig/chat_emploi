"""Tests d'intégration pour l'API FastAPI."""

import time

from api.main import app
from fastapi.testclient import TestClient


class TestAPIIntegration:
    """Tests d'intégration pour l'API FastAPI."""

    def setup_method(self):
        """Initialisation avant chaque test."""
        self.client = TestClient(app)

    def test_root_endpoint(self):
        """Test de l'endpoint racine."""
        response = self.client.get("/")

        assert response.status_code == 200
        data = response.json()

        assert "message" in data
        assert "version" in data
        assert data["message"] == "Chat Emploi Backend API"

    def test_health_endpoint(self):
        """Test de l'endpoint de santé."""
        response = self.client.get("/health")

        assert response.status_code == 200
        data = response.json()

        assert data["status"] == "healthy"

    def test_api_status_endpoint(self):
        """Test de l'endpoint de statut de l'API."""
        response = self.client.get("/api/status")

        assert response.status_code == 200
        data = response.json()

        assert data["status"] == "operational"
        assert data["version"] == "0.1.0"
        assert "services" in data
        assert "timestamp" in data

        services = data["services"]
        assert services["api"] == "running"
        assert services["monitoring"] == "enabled"

    def test_test_logs_endpoint(self):
        """Test de l'endpoint de test des logs."""
        response = self.client.get("/api/test/logs")

        assert response.status_code == 200
        data = response.json()

        assert data["status"] == "logs_generated"
        assert "Check application logs" in data["message"]

    def test_debug_metrics_endpoint(self):
        """Test de l'endpoint de debug des métriques."""
        response = self.client.get("/api/debug/metrics")

        assert response.status_code == 200
        data = response.json()

        assert data["metrics_available"] is True
        assert "endpoints" in data

        endpoints = data["endpoints"]
        assert "/metrics" in endpoints["prometheus"]
        assert "/health" in endpoints["health"]
        assert "/api/status" in endpoints["status"]

    def test_api_docs_redirect(self):
        """Test de la redirection vers la documentation."""
        response = self.client.get("/api/docs", follow_redirects=False)

        # Devrait rediriger vers /docs
        assert response.status_code == 307  # Temporary Redirect
        assert response.headers["location"] == "/docs"

    def test_openapi_docs_available(self):
        """Test que la documentation OpenAPI est disponible."""
        response = self.client.get("/docs")

        # La documentation devrait être disponible
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]
        assert "Swagger UI" in response.text or "ReDoc" in response.text

    def test_openapi_json_schema(self):
        """Test que le schéma OpenAPI JSON est disponible."""
        response = self.client.get("/openapi.json")

        assert response.status_code == 200
        schema = response.json()

        # Vérifier la structure de base du schéma OpenAPI
        assert "openapi" in schema
        assert "info" in schema
        assert "paths" in schema

        info = schema["info"]
        assert info["title"] == "Chat Emploi Backend"
        assert info["version"] == "0.1.0"

    def test_prometheus_metrics_endpoint(self):
        """Test de l'endpoint Prometheus /metrics."""
        response = self.client.get("/metrics")

        assert response.status_code == 200
        assert "text/plain" in response.headers["content-type"]

        # Vérifier que certaines métriques de base sont présentes
        metrics_text = response.text
        assert "python_gc_" in metrics_text  # Garbage collector metrics
        assert "process_" in metrics_text  # Process metrics

    def test_cors_headers(self):
        """Test que les headers CORS sont présents."""
        # Tester avec une route qui existe (GET /health)
        response = self.client.get(
            "/health", headers={"Origin": "http://localhost:3000"}
        )

        # Vérifier les headers CORS
        assert "access-control-allow-origin" in response.headers
        assert response.headers["access-control-allow-origin"] == "*"
        # Les autres headers CORS peuvent être ajoutés par le middleware

    def test_jsonrpc_test_endpoint_valid_request(self):
        """Test de l'endpoint de test JSON-RPC avec requête valide."""
        # Test avec méthode ping
        request = {"jsonrpc": "2.0", "method": "test.ping", "params": {}, "id": 1}

        response = self.client.post("/api/test/jsonrpc", json=request)

        assert response.status_code == 200
        data = response.json()

        assert data["jsonrpc"] == "2.0"
        assert data["id"] == 1
        assert "result" in data
        assert data["result"]["status"] == "pong"
        assert "timestamp" in data["result"]

    def test_jsonrpc_test_endpoint_echo_request(self):
        """Test de l'endpoint de test JSON-RPC avec méthode echo."""
        request = {
            "jsonrpc": "2.0",
            "method": "test.echo",
            "params": {"text": "Hello World"},
            "id": 2,
        }

        response = self.client.post("/api/test/jsonrpc", json=request)

        assert response.status_code == 200
        data = response.json()

        assert data["jsonrpc"] == "2.0"
        assert data["id"] == 2
        assert "result" in data
        assert data["result"]["echo"]["text"] == "Hello World"

    def test_jsonrpc_test_endpoint_method_not_found(self):
        """Test de l'endpoint de test JSON-RPC avec méthode inconnue."""
        request = {"jsonrpc": "2.0", "method": "unknown.method", "params": {}, "id": 3}

        response = self.client.post("/api/test/jsonrpc", json=request)

        # Devrait retourner une erreur 400 avec l'erreur JSON-RPC
        assert response.status_code == 400
        data = response.json()

        # L'erreur est dans data["error"]["message"] comme string Python
        assert "error" in data
        error_message = data["error"]["message"]

        # Le message contient la réponse JSON-RPC en string Python
        # On peut vérifier qu'il contient les informations attendues
        assert "Method not found" in error_message
        assert "'id': 3" in error_message or '"id": 3' in error_message
        assert (
            "'jsonrpc': '2.0'" in error_message or '"jsonrpc": "2.0"' in error_message
        )

    def test_error_handling_http_exception(self):
        """Test du handler d'erreurs HTTP."""
        # Tester avec une route qui n'existe pas (404)
        response = self.client.get("/nonexistent/route")

        assert response.status_code == 404
        data = response.json()

        # Vérifier le format d'erreur standard
        assert "error" in data or "detail" in data

    def test_error_handling_generic_exception(self):
        """Test du handler d'exceptions génériques."""
        # Tester avec une requête invalide vers l'endpoint JSON-RPC
        response = self.client.post("/api/test/jsonrpc", json={"invalid": "request"})

        # Devrait retourner une erreur 400
        assert response.status_code == 400
        data = response.json()

        # Vérifier qu'une erreur est retournée
        assert "error" in data or "detail" in data

    def test_metrics_middleware_latency(self):
        """Test que le middleware de métriques enregistre la latence."""
        # Faire une requête
        start_time = time.time()
        response = self.client.get("/health")
        end_time = time.time()

        assert response.status_code == 200

        # Vérifier que la métrique a été enregistrée
        # (Dans un vrai test, on vérifierait les métriques Prometheus)
        # Pour l'instant, on vérifie juste que la requête fonctionne
        latency = end_time - start_time
        assert latency < 1.0  # La requête devrait être rapide

    def test_concurrent_requests(self):
        """Test de requêtes concurrentes."""
        import concurrent.futures

        def make_request():
            response = self.client.get("/health")
            return response.status_code

        # Faire 10 requêtes concurrentes
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(make_request) for _ in range(10)]
            results = [
                future.result() for future in concurrent.futures.as_completed(futures)
            ]

        # Toutes les requêtes devraient réussir
        assert all(status == 200 for status in results)

    def test_request_body_validation(self):
        """Test de validation du corps de la requête pour JSON-RPC."""
        # Requête JSON-RPC invalide (sans jsonrpc)
        invalid_request = {"method": "test.ping", "params": {}, "id": 1}

        response = self.client.post("/api/test/jsonrpc", json=invalid_request)

        # L'API ajoute automatiquement jsonrpc: '2.0' si absent
        # et traite la requête normalement
        assert response.status_code == 200
        data = response.json()

        # Devrait contenir une réponse valide
        assert "jsonrpc" in data
        assert data["jsonrpc"] == "2.0"
        assert "result" in data
        assert data["result"]["status"] == "pong"

    def test_api_version_header(self):
        """Test du header de version de l'API."""
        response = self.client.get("/", headers={"X-API-Version": "1.0"})

        # L'API devrait accepter le header (même si pas encore utilisé)
        assert response.status_code == 200

    def test_large_request_body(self):
        """Test avec un corps de requête volumineux."""
        # Créer une grande payload
        large_params = {"data": "x" * 10000}  # 10KB de données

        request = {
            "jsonrpc": "2.0",
            "method": "test.echo",
            "params": large_params,
            "id": 1,
        }

        response = self.client.post("/api/test/jsonrpc", json=request)

        # Devrait gérer la grande payload
        assert response.status_code == 200
        data = response.json()
        assert data["result"]["echo"]["data"] == large_params["data"]
