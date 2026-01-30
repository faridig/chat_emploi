"""Tests de performance pour le système Chat Emploi."""

import statistics
import time

from fastapi.testclient import TestClient

from src.api.main import app


def test_api_response_time():
    """Test que les endpoints API répondent en moins de 500ms."""
    client = TestClient(app)

    endpoints = [
        ("GET", "/health"),
        ("GET", "/api/status"),
        ("GET", "/metrics"),
        ("POST", "/api/test/jsonrpc"),
    ]

    results = []

    for method, endpoint in endpoints:
        start_time = time.time()

        if method == "POST":
            response = client.post(
                endpoint,
                json={"jsonrpc": "2.0", "method": "test.ping", "params": {}, "id": 1},
            )
        else:
            response = client.get(endpoint)

        end_time = time.time()
        response_time = (end_time - start_time) * 1000  # Convertir en ms

        results.append((endpoint, response_time))

        # Vérifier que la réponse est valide
        assert response.status_code in [
            200,
            307,
        ], f"Endpoint {endpoint} a retourné {response.status_code}"

        # Vérifier le temps de réponse
        max_response_time = 500  # 500ms
        assert (
            response_time < max_response_time
        ), f"Endpoint {endpoint} trop lent: {response_time:.2f}ms (max: {max_response_time}ms)"

    print("\n📊 Performances des endpoints API:")
    for endpoint, response_time in results:
        print(f"  {endpoint}: {response_time:.2f}ms")

    # Calculer les statistiques
    response_times = [rt for _, rt in results]
    avg_time = statistics.mean(response_times)
    max_time = max(response_times)

    print("\n📈 Statistiques:")
    print(f"  Moyenne: {avg_time:.2f}ms")
    print(f"  Maximum: {max_time:.2f}ms")
    print(f"  Nombre d'endpoints testés: {len(endpoints)}")


def test_concurrent_requests_performance():
    """Test de performance avec requêtes concurrentes."""
    import concurrent.futures

    client = TestClient(app)

    def make_request():
        response = client.get("/health")
        return response.status_code, time.time()

    # Faire 20 requêtes concurrentes
    num_requests = 20
    start_time = time.time()

    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(make_request) for _ in range(num_requests)]
        results = [
            future.result() for future in concurrent.futures.as_completed(futures)
        ]

    end_time = time.time()
    total_time = end_time - start_time

    # Vérifier que toutes les requêtes ont réussi
    status_codes = [status for status, _ in results]
    assert all(
        status == 200 for status in status_codes
    ), "Certaines requêtes ont échoué"

    # Calculer le débit (requêtes par seconde)
    throughput = num_requests / total_time

    print("\n🚀 Test de requêtes concurrentes:")
    print(f"  Requêtes: {num_requests}")
    print(f"  Temps total: {total_time:.2f}s")
    print(f"  Débit: {throughput:.2f} req/s")

    # Objectif: au moins 10 req/s
    min_throughput = 10
    assert (
        throughput >= min_throughput
    ), f"Débit trop faible: {throughput:.2f} req/s (min: {min_throughput} req/s)"


if __name__ == "__main__":
    print("🔧 Exécution des tests de performance...")

    # Exécuter les tests
    test_api_response_time()
    test_concurrent_requests_performance()

    print("\n✅ Tous les tests de performance passés avec succès!")
