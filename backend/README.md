# Backend Chat Emploi

Backend Python pour l'application Chat Emploi.

## Structure

- `src/api/` - Endpoints FastAPI
- `src/agents/` - Agents LangGraph/CrewAI
- `src/services/` - Services métier
- `src/database/` - Modèles SQLAlchemy et migrations
- `src/rag/` - Système RAG avec LlamaIndex
- `src/monitoring/` - Métriques Prometheus et logs

## Installation

1. Activer l'environnement virtuel :
   ```bash
   source .venv/bin/activate
   ```

2. Installer les dépendances :
   ```bash
   pip install -r requirements-dev.txt
   ```

3. Configurer les variables d'environnement :
   ```bash
   cp .env.example .env
   # Éditer .env avec vos clés API
   ```

4. Lancer le serveur de développement :
   ```bash
   uvicorn src.api.main:app --reload
   ```

## Tests

```bash
pytest tests/ -v
```