"""Tests unitaires pour le serveur JSON-RPC."""

import json
import sys
from io import StringIO
from unittest.mock import patch

import pytest

from src.api.jsonrpc_server import JSONRPCError, JSONRPCServer


class TestJSONRPCServer:
    """Tests pour le serveur JSON-RPC."""

    def setup_method(self):
        """Initialisation avant chaque test."""
        self.server = JSONRPCServer()

        # Méthodes de test
        self.server.register_method("test.echo", self._echo_method)
        self.server.register_method("test.add", self._add_method)
        self.server.register_method("test.error", self._error_method)

    def _echo_method(self, params):
        """Méthode de test echo."""
        return {"echo": params.get("text", "")}

    def _add_method(self, params):
        """Méthode de test addition."""
        # Gérer les paramètres positionnels (liste) ou nommés (dict)
        if isinstance(params, list):
            x = params[0] if len(params) > 0 else 0
            y = params[1] if len(params) > 1 else 0
        else:
            x = params.get("x", 0)
            y = params.get("y", 0)
        return {"result": x + y}

    def _error_method(self, params):
        """Méthode de test qui génère une erreur."""
        raise JSONRPCError(
            code=-32000, message="Test error", data={"details": "This is a test error"}
        )

    def test_handle_single_request_valid(self):
        """Test de traitement d'une requête JSON-RPC valide."""
        request = {
            "jsonrpc": "2.0",
            "method": "test.echo",
            "params": {"text": "Hello World"},
            "id": 1,
        }

        response = self.server.handle_request(json.dumps(request))
        result = json.loads(response)

        assert result["jsonrpc"] == "2.0"
        assert result["id"] == 1
        assert "result" in result
        assert result["result"]["echo"] == "Hello World"
        assert "error" not in result

    def test_handle_single_request_with_positional_params(self):
        """Test avec paramètres positionnels."""
        request = {"jsonrpc": "2.0", "method": "test.add", "params": [5, 3], "id": 2}

        response = self.server.handle_request(json.dumps(request))
        result = json.loads(response)

        assert result["result"]["result"] == 8

    def test_handle_single_request_with_named_params(self):
        """Test avec paramètres nommés."""
        request = {
            "jsonrpc": "2.0",
            "method": "test.add",
            "params": {"x": 10, "y": 20},
            "id": 3,
        }

        response = self.server.handle_request(json.dumps(request))
        result = json.loads(response)

        assert result["result"]["result"] == 30

    def test_handle_single_request_error(self):
        """Test de traitement d'une requête avec erreur."""
        request = {"jsonrpc": "2.0", "method": "test.error", "params": {}, "id": 4}

        response = self.server.handle_request(json.dumps(request))
        result = json.loads(response)

        assert result["jsonrpc"] == "2.0"
        assert result["id"] == 4
        assert "error" in result
        assert result["error"]["code"] == -32000
        assert result["error"]["message"] == "Test error"
        assert "result" not in result

    def test_handle_single_request_method_not_found(self):
        """Test avec méthode non trouvée."""
        request = {"jsonrpc": "2.0", "method": "unknown.method", "params": {}, "id": 5}

        response = self.server.handle_request(json.dumps(request))
        result = json.loads(response)

        assert "error" in result
        assert result["error"]["code"] == -32601  # Method not found
        assert result["error"]["message"] == "Method not found"

    def test_handle_single_request_invalid_json(self):
        """Test avec JSON invalide."""
        response = self.server.handle_request("invalid json")
        result = json.loads(response)

        assert "error" in result
        assert result["error"]["code"] == -32700  # Parse error
        assert "Invalid JSON" in result["error"]["message"]

    def test_handle_single_request_invalid_request(self):
        """Test avec requête invalide (sans jsonrpc)."""
        request = {"method": "test.echo", "params": {}, "id": 6}

        response = self.server.handle_request(json.dumps(request))
        result = json.loads(response)

        assert "error" in result
        assert result["error"]["code"] == -32600  # Invalid Request

    def test_handle_batch_request(self):
        """Test de traitement d'un batch de requêtes."""
        batch = [
            {
                "jsonrpc": "2.0",
                "method": "test.echo",
                "params": {"text": "First"},
                "id": 1,
            },
            {
                "jsonrpc": "2.0",
                "method": "test.add",
                "params": {"x": 2, "y": 3},
                "id": 2,
            },
            {
                "jsonrpc": "2.0",
                "method": "test.echo",
                "params": {"text": "Third"},
                "id": 3,
            },
        ]

        response = self.server.handle_request(json.dumps(batch))
        results = json.loads(response)

        assert isinstance(results, list)
        assert len(results) == 3

        # Vérifier chaque réponse
        assert results[0]["id"] == 1
        assert results[0]["result"]["echo"] == "First"

        assert results[1]["id"] == 2
        assert results[1]["result"]["result"] == 5

        assert results[2]["id"] == 3
        assert results[2]["result"]["echo"] == "Third"

    def test_handle_batch_with_notification(self):
        """Test batch avec notification (sans id)."""
        batch = [
            {
                "jsonrpc": "2.0",
                "method": "test.echo",
                "params": {"text": "Notification"},
            },
            {
                "jsonrpc": "2.0",
                "method": "test.add",
                "params": {"x": 1, "y": 2},
                "id": 1,
            },
        ]

        response = self.server.handle_request(json.dumps(batch))
        results = json.loads(response)

        # Seule la requête avec id devrait avoir une réponse
        assert isinstance(results, list)
        assert len(results) == 1
        assert results[0]["id"] == 1
        assert results[0]["result"]["result"] == 3

    def test_handle_notification(self):
        """Test d'une notification (sans id)."""
        request = {
            "jsonrpc": "2.0",
            "method": "test.echo",
            "params": {"text": "Notification"},
        }

        response = self.server.handle_request(json.dumps(request))

        # Les notifications ne devraient pas avoir de réponse
        assert response == ""

    def test_register_method_duplicate(self):
        """Test d'enregistrement de méthode en double."""
        # La méthode est déjà enregistrée dans setup_method
        with pytest.raises(ValueError, match="Method already registered"):
            self.server.register_method("test.echo", lambda p: p)

    def test_jsonrpc_error_creation(self):
        """Test de création d'erreur JSON-RPC."""
        error = JSONRPCError(code=-32000, message="Test error", data={"extra": "info"})

        error_dict = error.to_dict()

        assert error_dict["code"] == -32000
        assert error_dict["message"] == "Test error"
        assert error_dict["data"] == {"extra": "info"}

    def test_stdin_stdout_loop(self):
        """Test de la boucle stdin/stdout."""
        test_input = [
            json.dumps(
                {
                    "jsonrpc": "2.0",
                    "method": "test.echo",
                    "params": {"text": "Test"},
                    "id": 1,
                }
            ),
            json.dumps(
                {
                    "jsonrpc": "2.0",
                    "method": "test.add",
                    "params": {"x": 10, "y": 20},
                    "id": 2,
                }
            ),
        ]

        # Simuler stdin avec nos données de test
        stdin_mock = StringIO("\n".join(test_input))
        stdout_mock = StringIO()

        with (
            patch.object(sys, "stdin", stdin_mock),
            patch.object(sys, "stdout", stdout_mock),
        ):
            # Lancer le serveur avec un nombre limité d'itérations
            self.server.run(max_iterations=2)

            # Récupérer toutes les lignes de sortie
            all_output = stdout_mock.getvalue().strip().split("\n")

            # Filtrer pour ne garder que les réponses JSON (qui commencent par {)
            json_responses = [
                line for line in all_output if line.strip().startswith("{")
            ]

            # Vérifier qu'on a bien 2 réponses JSON
            assert len(json_responses) == 2

            # Vérifier chaque réponse
            response1 = json.loads(json_responses[0])
            response2 = json.loads(json_responses[1])

            assert response1["id"] == 1
            assert response1["result"]["echo"] == "Test"

            assert response2["id"] == 2
            assert response2["result"]["result"] == 30

    def test_stdin_stdout_with_empty_line(self):
        """Test avec ligne vide dans stdin."""
        test_input = [
            json.dumps(
                {
                    "jsonrpc": "2.0",
                    "method": "test.echo",
                    "params": {"text": "Test"},
                    "id": 1,
                }
            ),
            "",  # Ligne vide
            json.dumps(
                {
                    "jsonrpc": "2.0",
                    "method": "test.add",
                    "params": {"x": 5, "y": 5},
                    "id": 2,
                }
            ),
        ]

        stdin_mock = StringIO("\n".join(test_input))
        stdout_mock = StringIO()

        with (
            patch.object(sys, "stdin", stdin_mock),
            patch.object(sys, "stdout", stdout_mock),
        ):
            self.server.run(max_iterations=3)

            all_output = stdout_mock.getvalue().strip().split("\n")

            # Filtrer pour ne garder que les réponses JSON (qui commencent par {)
            json_responses = [
                line for line in all_output if line.strip().startswith("{")
            ]

            # Devrait avoir 2 réponses JSON (ignorer la ligne vide et les logs)
            assert len(json_responses) == 2

            response1 = json.loads(json_responses[0])
            response2 = json.loads(json_responses[1])

            assert response1["id"] == 1
            assert response2["id"] == 2
            assert response2["result"]["result"] == 10
