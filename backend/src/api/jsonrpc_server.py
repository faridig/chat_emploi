"""Serveur JSON-RPC 2.0 pour communication IPC avec Tauri."""

import json
import sys
import traceback
from collections.abc import Callable
from typing import Any

import structlog

logger = structlog.get_logger(__name__)


class JSONRPCError(Exception):
    """Erreur JSON-RPC personnalisée."""

    def __init__(self, code: int, message: str, data: dict[str, Any] | None = None):
        self.code = code
        self.message = message
        self.data = data
        super().__init__(f"JSON-RPC Error {code}: {message}")

    def to_dict(self) -> dict[str, Any]:
        """Convertit l'erreur en dictionnaire JSON-RPC."""
        result = {"code": self.code, "message": self.message}
        if self.data is not None:
            result["data"] = self.data
        return result


class JSONRPCServer:
    """Serveur JSON-RPC 2.0 avec support stdin/stdout."""

    # Codes d'erreur JSON-RPC standard
    PARSE_ERROR = -32700
    INVALID_REQUEST = -32600
    METHOD_NOT_FOUND = -32601
    INVALID_PARAMS = -32602
    INTERNAL_ERROR = -32603

    # Codes d'erreur applicatifs (à partir de -32000)
    APPLICATION_ERROR = -32000

    def __init__(self):
        """Initialise le serveur JSON-RPC."""
        self.methods: dict[str, Callable] = {}
        self.running = False
        logger.info("jsonrpc_server_initialized")

    def register_method(self, name: str, method: Callable) -> None:
        """Enregistre une méthode JSON-RPC.

        Args:
            name: Nom de la méthode (ex: "cv.process_and_analyze")
            method: Fonction qui prend un dict de paramètres et retourne un résultat

        Raises:
            ValueError: Si la méthode est déjà enregistrée
        """
        if name in self.methods:
            raise ValueError(f"Method already registered: {name}")

        self.methods[name] = method
        logger.debug("method_registered", method=name)

    def unregister_method(self, name: str) -> None:
        """Supprime une méthode enregistrée."""
        if name in self.methods:
            del self.methods[name]
            logger.debug("method_unregistered", method=name)

    def _parse_request(self, request_str: str) -> dict | list | None:
        """Parse une requête JSON-RPC.

        Returns:
            La requête parsée ou None si JSON invalide
        """
        try:
            return json.loads(request_str)
        except json.JSONDecodeError as e:
            logger.error("json_parse_error", error=str(e), input=request_str)
            return None

    def _validate_request(self, request: dict[str, Any]) -> JSONRPCError | None:
        """Valide une requête JSON-RPC.

        Returns:
            Erreur JSON-RPC si la requête est invalide, None sinon
        """
        # Vérifier la version JSON-RPC
        if request.get("jsonrpc") != "2.0":
            return JSONRPCError(
                code=self.INVALID_REQUEST,
                message="Invalid Request: 'jsonrpc' must be '2.0'",
            )

        # Vérifier la méthode
        if "method" not in request:
            return JSONRPCError(
                code=self.INVALID_REQUEST,
                message="Invalid Request: 'method' is required",
            )

        # Vérifier que method est une string
        if not isinstance(request["method"], str):
            return JSONRPCError(
                code=self.INVALID_REQUEST,
                message="Invalid Request: 'method' must be a string",
            )

        # Vérifier les params (optionnels mais doivent être array ou object s'ils existent)
        if "params" in request:
            params = request["params"]
            if not isinstance(params, list | dict):
                return JSONRPCError(
                    code=self.INVALID_REQUEST,
                    message="Invalid Request: 'params' must be an array or object",
                )

        return None

    def _execute_method(
        self, method_name: str, params: Any, request_id: Any
    ) -> dict[str, Any]:
        """Exécute une méthode JSON-RPC.

        Returns:
            Réponse JSON-RPC avec result ou error
        """
        # Vérifier si la méthode existe
        if method_name not in self.methods:
            logger.warning("method_not_found", method=method_name)
            return self._create_error_response(
                request_id=request_id,
                code=self.METHOD_NOT_FOUND,
                message="Method not found",
                data={"method": method_name},
            )

        method = self.methods[method_name]

        try:
            # Exécuter la méthode
            logger.debug("executing_method", method=method_name, params=params)
            result = method(params if params is not None else {})

            # Créer la réponse de succès
            return self._create_success_response(request_id, result)

        except JSONRPCError as e:
            # Erreur JSON-RPC connue
            logger.error("jsonrpc_error", method=method_name, error=e.to_dict())
            return self._create_error_response(
                request_id=request_id, code=e.code, message=e.message, data=e.data
            )

        except Exception as e:
            # Erreur interne
            error_trace = traceback.format_exc()
            logger.exception("internal_error", method=method_name, error=str(e))

            return self._create_error_response(
                request_id=request_id,
                code=self.INTERNAL_ERROR,
                message="Internal error",
                data={
                    "exception": str(e),
                    "traceback": error_trace,
                    "method": method_name,
                },
            )

    def _create_success_response(self, request_id: Any, result: Any) -> dict[str, Any]:
        """Crée une réponse JSON-RPC de succès."""
        response = {"jsonrpc": "2.0", "result": result}

        # Ajouter l'ID seulement si ce n'est pas une notification
        if request_id is not None:
            response["id"] = request_id

        return response

    def _create_error_response(
        self,
        request_id: Any,
        code: int,
        message: str,
        data: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Crée une réponse JSON-RPC d'erreur."""
        error = {"code": code, "message": message}

        if data is not None:
            error["data"] = data

        response = {"jsonrpc": "2.0", "error": error}

        # Ajouter l'ID seulement si ce n'est pas une notification
        if request_id is not None:
            response["id"] = request_id

        return response

    def handle_single_request(self, request: dict[str, Any]) -> dict[str, Any] | None:
        """Traite une requête JSON-RPC unique.

        Returns:
            Réponse JSON-RPC ou None pour les notifications
        """
        # Valider la requête
        validation_error = self._validate_request(request)
        if validation_error:
            return self._create_error_response(
                request_id=request.get("id"),
                code=validation_error.code,
                message=validation_error.message,
                data=validation_error.data,
            )

        # Extraire les informations de la requête
        method_name = request["method"]
        params = request.get("params")
        request_id = request.get("id")  # Peut être None pour les notifications

        # Exécuter la méthode
        response = self._execute_method(method_name, params, request_id)

        # Pour les notifications (sans id), on ne retourne pas de réponse
        if request_id is None:
            logger.debug("notification_processed", method=method_name)
            return None

        return response

    def handle_batch_request(
        self, requests: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        """Traite un batch de requêtes JSON-RPC.

        Returns:
            Liste de réponses (les notifications sont exclues)
        """
        responses = []

        for request in requests:
            response = self.handle_single_request(request)
            if response is not None:
                responses.append(response)

        return responses

    def handle_request(self, request_str: str) -> str:
        """Point d'entrée principal pour traiter une requête JSON-RPC.

        Args:
            request_str: Chaîne JSON de la requête

        Returns:
            Chaîne JSON de la réponse (vide pour les notifications)
        """
        # Parser la requête
        parsed = self._parse_request(request_str)

        # Erreur de parsing
        if parsed is None:
            error_response = self._create_error_response(
                request_id=None,
                code=self.PARSE_ERROR,
                message="Parse error: Invalid JSON",
            )
            return json.dumps(error_response)

        # Traiter la requête (simple ou batch)
        if isinstance(parsed, list):
            # Requête batch
            if not parsed:
                # Batch vide -> erreur
                error_response = self._create_error_response(
                    request_id=None,
                    code=self.INVALID_REQUEST,
                    message="Invalid Request: Empty batch",
                )
                return json.dumps(error_response)

            responses = self.handle_batch_request(parsed)
            if responses:
                return json.dumps(responses)
            else:
                # Toutes les requêtes étaient des notifications
                return ""
        else:
            # Requête simple
            response = self.handle_single_request(parsed)
            if response is not None:
                return json.dumps(response)
            else:
                # Notification
                return ""

    def run(self, max_iterations: int | None = None) -> None:
        """Boucle principale du serveur lisant depuis stdin et écrivant vers stdout.

        Args:
            max_iterations: Nombre maximum d'itérations (pour les tests)
        """
        self.running = True
        iteration = 0

        logger.info("jsonrpc_server_started", stdin="sys.stdin", stdout="sys.stdout")

        try:
            while self.running:
                # Gestion du nombre maximum d'itérations (pour les tests)
                iteration += 1
                if max_iterations is not None and iteration > max_iterations:
                    logger.info("max_iterations_reached", iterations=iteration)
                    break

                # Lire une ligne depuis stdin
                line = sys.stdin.readline()

                # Fin de fichier ou ligne vide
                if not line:
                    if not sys.stdin.closed:
                        continue  # Attendre plus de données
                    else:
                        logger.info("stdin_closed")
                        break

                line = line.strip()
                if not line:
                    continue  # Ignorer les lignes vides

                # Traiter la requête
                logger.debug(
                    "received_request", request=line[:100]
                )  # Log les 100 premiers caractères
                response = self.handle_request(line)

                # Écrire la réponse vers stdout si elle n'est pas vide
                if response:
                    sys.stdout.write(response + "\n")
                    sys.stdout.flush()
                    logger.debug(
                        "sent_response", response=response[:100]
                    )  # Log les 100 premiers caractères

        except KeyboardInterrupt:
            logger.info("keyboard_interrupt")
        except Exception as e:
            logger.exception("unexpected_error", error=str(e))
        finally:
            self.running = False
            logger.info("jsonrpc_server_stopped")

    def stop(self) -> None:
        """Arrête le serveur."""
        self.running = False
        logger.info("jsonrpc_server_stopping")
