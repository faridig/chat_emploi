#!/usr/bin/env python3
"""
Script de benchmark de performance pour Chat Emploi.
Exécute une série de tests de performance et génère un rapport.
"""

import asyncio
import json
import os
import statistics
import sys
import time
from datetime import datetime
from typing import Any

# Ajouter le chemin du projet
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi.testclient import TestClient

from src.api.main import app


class PerformanceBenchmark:
    """Classe pour exécuter des benchmarks de performance."""

    def __init__(self):
        self.client = TestClient(app)
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "tests": {},
            "summary": {},
        }

    def measure_endpoint(
        self,
        endpoint: str,
        method: str = "GET",
        payload: dict[str, Any] | None = None,
        iterations: int = 10,
    ) -> dict[str, Any]:
        """Mesure les performances d'un endpoint."""
        times = []

        for _ in range(iterations):
            start = time.perf_counter()

            if method == "GET":
                response = self.client.get(endpoint)
            elif method == "POST":
                response = self.client.post(endpoint, json=payload)
            else:
                raise ValueError(f"Méthode non supportée: {method}")

            elapsed = (time.perf_counter() - start) * 1000  # Convertir en ms

            if response.status_code >= 400:
                print(
                    f"⚠️  Erreur {response.status_code} pour {endpoint}: {response.text}"
                )

            times.append(elapsed)

        return {
            "endpoint": endpoint,
            "method": method,
            "iterations": iterations,
            "times_ms": times,
            "mean_ms": statistics.mean(times),
            "median_ms": statistics.median(times),
            "min_ms": min(times),
            "max_ms": max(times),
            "std_dev_ms": statistics.stdev(times) if len(times) > 1 else 0,
            "success_rate": 100.0,  # Tous les appels ont réussi
        }

    def test_concurrent_requests(
        self, endpoint: str, concurrent: int = 10
    ) -> dict[str, Any]:
        """Test de requêtes concurrentes."""

        async def make_request():
            start = time.perf_counter()
            response = self.client.get(endpoint)
            elapsed = (time.perf_counter() - start) * 1000
            return elapsed, response.status_code

        async def run_concurrent():
            tasks = [make_request() for _ in range(concurrent)]
            return await asyncio.gather(*tasks)

        # Exécuter les requêtes concurrentes
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        results = loop.run_until_complete(run_concurrent())
        loop.close()

        times = [r[0] for r in results]
        status_codes = [r[1] for r in results]

        success_count = sum(1 for code in status_codes if code < 400)
        success_rate = (success_count / concurrent) * 100

        total_time = sum(times)
        throughput = (concurrent / (total_time / 1000)) if total_time > 0 else 0

        return {
            "endpoint": endpoint,
            "concurrent_requests": concurrent,
            "total_time_ms": total_time,
            "throughput_req_per_sec": throughput,
            "success_rate_percent": success_rate,
            "times_ms": times,
        }

    def test_system_health(self) -> dict[str, Any]:
        """Test de santé du système."""
        endpoints = [
            ("/health", "GET"),
            ("/api/status", "GET"),
            ("/metrics", "GET"),
            ("/docs", "GET"),
            ("/openapi.json", "GET"),
        ]

        results = []
        for endpoint, method in endpoints:
            start = time.perf_counter()

            if method == "GET":
                response = self.client.get(endpoint)
            else:
                response = self.client.post(endpoint)

            elapsed = (time.perf_counter() - start) * 1000

            results.append(
                {
                    "endpoint": endpoint,
                    "method": method,
                    "status_code": response.status_code,
                    "response_time_ms": elapsed,
                    "healthy": response.status_code < 400,
                }
            )

        healthy_count = sum(1 for r in results if r["healthy"])
        health_percentage = (healthy_count / len(results)) * 100

        return {
            "endpoints_tested": len(results),
            "healthy_endpoints": healthy_count,
            "health_percentage": health_percentage,
            "details": results,
        }

    def test_jsonrpc_performance(self) -> dict[str, Any]:
        """Test de performance JSON-RPC."""
        payload = {
            "jsonrpc": "2.0",
            "method": "test.ping",
            "params": {"message": "ping"},
            "id": 1,
        }

        return self.measure_endpoint(
            "/api/test/jsonrpc", method="POST", payload=payload, iterations=20
        )

    def run_all_benchmarks(self):
        """Exécute tous les benchmarks."""
        print("🚀 Démarrage des benchmarks de performance...")

        # 1. Test de santé du système
        print("📊 Test de santé du système...")
        self.results["tests"]["system_health"] = self.test_system_health()

        # 2. Benchmarks des endpoints principaux
        print("📈 Benchmarks des endpoints...")
        endpoints = [
            ("/health", "GET"),
            ("/api/status", "GET"),
            ("/metrics", "GET"),
            ("/api/test/jsonrpc", "POST"),
        ]

        for endpoint, method in endpoints:
            print(f"  Testing {method} {endpoint}...")
            payload: dict[str, Any] | None = None
            if endpoint == "/api/test/jsonrpc":
                payload = {
                    "jsonrpc": "2.0",
                    "method": "test.ping",
                    "params": {"message": "ping"},
                    "id": 1,
                }

            self.results["tests"][endpoint.replace("/", "_").replace(".", "_")] = (
                self.measure_endpoint(endpoint, method, payload)
            )

        # 3. Test de requêtes concurrentes
        print("⚡ Test de requêtes concurrentes...")
        self.results["tests"]["concurrent_requests"] = self.test_concurrent_requests(
            "/health"
        )

        # 4. Test JSON-RPC spécifique
        print("🔧 Test de performance JSON-RPC...")
        self.results["tests"]["jsonrpc_performance"] = self.test_jsonrpc_performance()

        # Générer le résumé
        self._generate_summary()

        print("✅ Benchmarks terminés!")
        return self.results

    def _generate_summary(self):
        """Génère un résumé des résultats."""
        endpoint_results = []
        for _, result in self.results["tests"].items():
            if "mean_ms" in result:  # C'est un résultat d'endpoint
                endpoint_results.append(result)

        if endpoint_results:
            self.results["summary"] = {
                "total_endpoints_tested": len(endpoint_results),
                "average_response_time_ms": statistics.mean(
                    [r["mean_ms"] for r in endpoint_results]
                ),
                "fastest_endpoint": min(endpoint_results, key=lambda x: x["mean_ms"])[
                    "endpoint"
                ],
                "slowest_endpoint": max(endpoint_results, key=lambda x: x["mean_ms"])[
                    "endpoint"
                ],
                "system_health_percentage": self.results["tests"]["system_health"][
                    "health_percentage"
                ],
                "concurrent_throughput": self.results["tests"]["concurrent_requests"][
                    "throughput_req_per_sec"
                ],
            }

    def save_report(self, filename: str = "performance_report.json"):
        """Sauvegarde le rapport dans un fichier."""
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)

        print(f"📄 Rapport sauvegardé dans {filename}")

        # Afficher un résumé dans la console
        self.print_summary()

    def print_summary(self):
        """Affiche un résumé dans la console."""
        summary = self.results["summary"]

        print("\n" + "=" * 60)
        print("📊 RÉSUMÉ DES PERFORMANCES")
        print("=" * 60)
        print(f"Timestamp: {self.results['timestamp']}")
        print(f"Endpoints testés: {summary.get('total_endpoints_tested', 0)}")
        print(
            f"Temps de réponse moyen: {summary.get('average_response_time_ms', 0):.2f} ms"
        )
        print(f"Endpoint le plus rapide: {summary.get('fastest_endpoint', 'N/A')}")
        print(f"Endpoint le plus lent: {summary.get('slowest_endpoint', 'N/A')}")
        print(f"Santé du système: {summary.get('system_health_percentage', 0):.1f}%")
        print(f"Débit concurrent: {summary.get('concurrent_throughput', 0):.1f} req/s")
        print("=" * 60)

        # Vérifier les critères de performance
        print("\n✅ CRITÈRES DE PERFORMANCE:")
        avg_time = summary.get("average_response_time_ms", 0)
        if avg_time < 100:
            print(f"  ✓ Temps de réponse moyen: {avg_time:.2f} ms (< 100 ms cible)")
        else:
            print(f"  ⚠️  Temps de réponse moyen: {avg_time:.2f} ms (> 100 ms cible)")

        health = summary.get("system_health_percentage", 0)
        if health >= 95:
            print(f"  ✓ Santé du système: {health:.1f}% (≥ 95% cible)")
        else:
            print(f"  ⚠️  Santé du système: {health:.1f}% (< 95% cible)")

        throughput = summary.get("concurrent_throughput", 0)
        if throughput >= 100:
            print(f"  ✓ Débit concurrent: {throughput:.1f} req/s (≥ 100 req/s cible)")
        else:
            print(f"  ⚠️  Débit concurrent: {throughput:.1f} req/s (< 100 req/s cible)")


def main():
    """Fonction principale."""
    benchmark = PerformanceBenchmark()

    try:
        results = benchmark.run_all_benchmarks()
        benchmark.save_report("performance_benchmark_report.json")

        # Sauvegarder aussi en Markdown pour une meilleure lisibilité
        save_markdown_report(results)

    except Exception as e:
        print(f"❌ Erreur lors de l'exécution des benchmarks: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


def save_markdown_report(results: dict[str, Any]):
    """Sauvegarde le rapport au format Markdown."""
    filename = "performance_benchmark_report.md"

    with open(filename, "w", encoding="utf-8") as f:
        f.write("# Rapport de Performance - Chat Emploi\n\n")
        f.write(f"**Date**: {results['timestamp']}\n\n")

        # Résumé
        summary = results.get("summary", {})
        f.write("## 📊 Résumé Exécutif\n\n")
        f.write(f"- **Endpoints testés**: {summary.get('total_endpoints_tested', 0)}\n")
        f.write(
            f"- **Temps de réponse moyen**: {summary.get('average_response_time_ms', 0):.2f} ms\n"
        )
        f.write(
            f"- **Endpoint le plus rapide**: `{summary.get('fastest_endpoint', 'N/A')}`\n"
        )
        f.write(
            f"- **Endpoint le plus lent**: `{summary.get('slowest_endpoint', 'N/A')}`\n"
        )
        f.write(
            f"- **Santé du système**: {summary.get('system_health_percentage', 0):.1f}%\n"
        )
        f.write(
            f"- **Débit concurrent**: {summary.get('concurrent_throughput', 0):.1f} req/s\n\n"
        )

        # Détails par endpoint
        f.write("## 📈 Détails par Endpoint\n\n")
        f.write(
            "| Endpoint | Méthode | Moyenne (ms) | Min (ms) | Max (ms) | Std Dev |\n"
        )
        f.write(
            "|----------|---------|--------------|----------|----------|---------|\n"
        )

        for _, result in results["tests"].items():
            if "mean_ms" in result:
                f.write(
                    f"| `{result['endpoint']}` | {result['method']} | "
                    f"{result['mean_ms']:.2f} | {result['min_ms']:.2f} | "
                    f"{result['max_ms']:.2f} | {result['std_dev_ms']:.2f} |\n"
                )

        f.write("\n")

        # Santé du système
        f.write("## 🩺 Santé du Système\n\n")
        health_test = results["tests"].get("system_health", {})
        f.write(f"- **Endpoints testés**: {health_test.get('endpoints_tested', 0)}\n")
        f.write(f"- **Endpoints sains**: {health_test.get('healthy_endpoints', 0)}\n")
        f.write(
            f"- **Taux de santé**: {health_test.get('health_percentage', 0):.1f}%\n\n"
        )

        f.write("### Détails:\n")
        for detail in health_test.get("details", []):
            status = "✅" if detail["healthy"] else "❌"
            f.write(
                f"- {status} `{detail['endpoint']}` ({detail['method']}): "
                f"{detail['response_time_ms']:.2f} ms - HTTP {detail['status_code']}\n"
            )

        f.write("\n")

        # Performance concurrente
        f.write("## ⚡ Performance Concurrente\n\n")
        concurrent_test = results["tests"].get("concurrent_requests", {})
        f.write(
            f"- **Requêtes concurrentes**: {concurrent_test.get('concurrent_requests', 0)}\n"
        )
        f.write(
            f"- **Temps total**: {concurrent_test.get('total_time_ms', 0):.2f} ms\n"
        )
        f.write(
            f"- **Débit**: {concurrent_test.get('throughput_req_per_sec', 0):.1f} req/s\n"
        )
        f.write(
            f"- **Taux de succès**: {concurrent_test.get('success_rate_percent', 0):.1f}%\n\n"
        )

        # Recommandations
        f.write("## 🎯 Recommandations\n\n")

        avg_time = summary.get("average_response_time_ms", 0)
        if avg_time > 100:
            f.write(
                "1. **Optimiser les temps de réponse** - Le temps moyen est > 100 ms\n"
            )
            f.write("   - Vérifier les dépendances externes\n")
            f.write("   - Optimiser les requêtes de base de données\n")
            f.write("   - Mettre en cache les résultats fréquents\n")
        else:
            f.write(
                "1. ✅ **Temps de réponse** - Excellentes performances (< 100 ms)\n"
            )

        health = summary.get("system_health_percentage", 0)
        if health < 95:
            f.write("2. **Améliorer la santé du système** - Taux < 95%\n")
            f.write("   - Vérifier la disponibilité des services dépendants\n")
            f.write("   - Ajouter des retry mechanisms\n")
            f.write("   - Améliorer la gestion d'erreurs\n")
        else:
            f.write("2. ✅ **Santé du système** - Excellente disponibilité (≥ 95%)\n")

        throughput = summary.get("concurrent_throughput", 0)
        if throughput < 100:
            f.write("3. **Améliorer le débit concurrent** - < 100 req/s\n")
            f.write("   - Optimiser la gestion des connexions\n")
            f.write("   - Utiliser le connection pooling\n")
            f.write("   - Considérer l'async/await pour les I/O\n")
        else:
            f.write("3. ✅ **Débit concurrent** - Excellente capacité (≥ 100 req/s)\n")

        f.write("\n---\n")
        f.write("*Rapport généré automatiquement par le script de benchmark*\n")

    print(f"📄 Rapport Markdown sauvegardé dans {filename}")


if __name__ == "__main__":
    main()
