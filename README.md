# Chat Emploi

> Votre coach emploi empathique

Une application de bureau intelligente basée sur une architecture multi-agents (LangGraph, CrewAI) qui accompagne les demandeurs d'emploi dans leur recherche.

## 🎯 Vision

"Transformer la recherche d'emploi, processus solitaire et décourageant, en une expérience conversationnelle intelligente et empathique, où chaque demandeur d'emploi bénéficie d'un agent de carrière personnel, disponible 24h/24."

## 🏗️ Architecture Technique

### Stack utilisée

- **Frontend Desktop** : Tauri 2.0 + Next.js 15 (App Router) + TypeScript + Tailwind CSS
- **Backend Python** : FastAPI + LangGraph + CrewAI + LlamaIndex + ChromaDB
- **Base de données** : SQLite (données structurées) + ChromaDB (vecteurs)
- **Communication** : JSON-RPC over IPC (Tauri ↔ Python)
- **Monitoring** : Prometheus + Grafana (local)

### Structure du projet

```
chat_emploi/
├── frontend/          # Tauri + Next.js
├── backend/           # Python FastAPI + Agents
├── shared/            # Types partagés TypeScript/Python
├── scripts/           # Utilitaires build/dev
├── docs/              # Documentation
└── infrastructure/    # CI/CD, monitoring
```

## 🚀 Démarrage rapide

### Prérequis

- Node.js 20+
- Python 3.11+
- Rust (optionnel, Tauri l'installera si besoin)

### Installation

1. **Cloner le projet**
   ```bash
   git clone <repository>
   cd chat_emploi
   ```

2. **Setup automatique**
   ```bash
   ./scripts/dev/setup.sh
   ```

3. **Démarrer en développement**
   ```bash
   ./scripts/dev/start.sh
   ```

4. **Lancer Tauri en mode dev** (dans un autre terminal)
   ```bash
   cd frontend
   npm run tauri dev
   ```

### Accès aux services

- **Application Tauri** : S'ouvre automatiquement
- **Frontend Next.js** : http://localhost:3000
- **Backend FastAPI** : http://localhost:8000
- **Documentation API** : http://localhost:8000/docs
- **Monitoring Grafana** : http://localhost:3001 (après configuration)

## 📁 Structure des dossiers

### Frontend (`frontend/`)
- `src/app/` - Next.js App Router pages et layouts
- `src/components/` - Composants React réutilisables
- `src/lib/` - Utilities, hooks personnalisés
- `src-tauri/` - Code Rust pour Tauri (IPC, sidecar management)

### Backend (`backend/`)
- `src/api/` - Endpoints FastAPI et JSON-RPC
- `src/agents/` - Orchestration LangGraph/CrewAI
- `src/services/` - Logique métier (CV, offres, lettres)
- `src/database/` - Modèles SQLAlchemy, migrations
- `src/rag/` - Système RAG avec LlamaIndex + ChromaDB
- `src/monitoring/` - Métriques Prometheus, logs structurés

## 🧪 Tests

### Backend Python
```bash
cd backend
source .venv/bin/activate
pytest tests/ -v
```

### Frontend
```bash
cd frontend
npm test
```

### Tests E2E (Playwright)
```bash
cd frontend
npm run test:e2e
```

## 🔧 Configuration

### Variables d'environnement

Copier le fichier `.env.example` et configurer les clés API :

```bash
cd backend
cp .env.example .env
# Éditer .env avec vos clés API
```

### Clés API requises

1. **Google Gemini API** : Pour les modèles LLM et embeddings
2. **France Travail API** : Pour la recherche d'offres d'emploi
3. **SerpAPI** (optionnel) : Pour la recherche web complémentaire

## 📊 Monitoring & Observability

L'application inclut un dashboard Grafana local pour monitorer :

- **Performance** : Latence API, temps de génération
- **Usage** : CV traités, lettres générées, offres recherchées
- **Qualité** : Scores de matching, feedback utilisateurs
- **Système** : CPU, mémoire, disque, uptime

```bash
# Démarrer le monitoring (post-MVP)
docker-compose -f infrastructure/monitoring/docker-compose.yml up
```

## 🤝 Contribution

### Workflow de développement

1. **Phase 0** : Fondations & Outillage (CI/CD, linters, monitoring)
2. **Phase 1** : Cœur du système - Backend Python
3. **Phase 2** : Agents IA & RAG System
4. **Phase 3** : Frontend Tauri + Next.js
5. **Phase 4** : Intégration & Validation MVP

### Standards de code

- **Python** : Black + Ruff + Mypy (via pre-commit hooks)
- **TypeScript** : ESLint + Prettier
- **Rust** : rustfmt + clippy
- **Git** : Conventional Commits

### Qualité & Tests

- **Coverage minimum** : 85% backend, 75% frontend
- **TDD** pour les composants critiques
- **CI/CD** avec quality gates automatisés
- **Monitoring** intégré dès le début

## 📄 Documentation

- [PRD.md](./PRD.md) - Product Requirements Document
- [TECH_SPECS.md](./TECH_SPECS.md) - Spécifications techniques
- [DESIGN.md](./DESIGN.md) - Guidelines UX/UI
- [PLANNING.md](./PLANNING.md) - Roadmap & stratégie de test

## 📞 Support & Contact

- **Problèmes techniques** : Ouvrir une issue GitHub
- **Suggestions fonctionnelles** : Voir PRD.md pour la roadmap
- **Sécurité** : security@chatemploi.fr (pour les vulnérabilités)

## 📝 Licence

Propriétaire - Usage interne uniquement

---

*"La qualité n'est jamais un accident ; c'est toujours le résultat d'un effort intelligent." - John Ruskin*