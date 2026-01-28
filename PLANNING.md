# PLANNING.md - Chat Emploi
## Roadmap & Stratégie de Test "Zero Debt"
### Version 2.0 - Stratégie Validée
**Date** : 28 janvier 2026
**Project Manager** : Senior Technical PM & QA Lead
**Statut** : ✅ Stratégie "Zero Debt" validée

---

## 1. PHILOSOPHIE DE DÉVELOPPEMENT

### 1.1 Règles d'Or "Zero Debt"
1. **Pas de merge sans tests verts** : 100% des tests doivent passer
2. **Code coverage > 80%** pour le backend, > 70% pour le frontend
3. **TDD pour les composants critiques** : Écrire le test AVANT le code
4. **CI/CD comme gardien qualité** : Pipeline automatisée sur chaque push
5. **Monitoring intégré** : Métriques de performance et qualité en temps réel
6. **Clean Code immédiat** : Pas de "je nettoierai plus tard"

### 1.2 Stratégie de Test Validée
- **Backend Python** : TDD strict (pytest) + mocks des APIs externes
- **Frontend React** : Tests unitaires (Vitest) + composants (Testing Library)
- **Intégration** : Tests API (FastAPI) + flux métier complets
- **E2E** : Playwright pour les 4 flux utilisateurs critiques
- **CI/CD** : GitHub Actions avec quality gates automatisés

### 1.3 Contexte d'Équipe
- **Développeur** : 1 personne (Farid)
- **Agent IA** : Compétent frontend/backend/IA (accélération significative)
- **Deadline** : Aucune contrainte → priorité qualité/stabilité
- **Objectif** : MVP robuste, extensible, sans dette technique

---

## 2. PHASE 0 : FONDATIONS & OUTILLAGE (LA PRIORITÉ)
**Durée estimée** : 3-4 jours
**Objectif** : Mettre en place l'écosystème de développement "Zero Debt"
**Règle** : Aucune fonctionnalité métier avant que la Phase 0 soit terminée à 100%

### 2.1 Structure du Projet (Jour 1)
*Feature* : Initialiser la structure du projet conforme aux TECH_SPECS
*Test Plan* :
  - Validation de la structure avec script de vérification
  - Vérification des dépendances cross-platform
*Dev* :
  ```bash
  # Structure finale attendue
  chat_emploi/
  ├── frontend/                    # Tauri + Next.js
  ├── backend/                     # Python FastAPI + Agents
  ├── shared/                      # Types partagés
  ├── scripts/                     # Utilitaires build/dev
  ├── docs/                        # Documentation
  └── infrastructure/              # CI/CD, monitoring
  ```
 *Validation* :
  - ✅ Structure créée avec tous les dossiers
  - ✅ README.md avec instructions setup
  - ✅ .gitignore complet pour Python/Node/Rust
  *Statut* : ✅ Terminé le 28 janvier 2026

 ### 2.2 Linter/Formatter & Pre-commit Hooks (Jour 1)
*Feature* : Configuration qualité de code automatique
*Test Plan* : Script vérifiant que le formatter s'exécute correctement
*Dev* :
  ```bash
  # Backend Python
  - ruff (linter) + black (formatter) + mypy (type checking)
  - pre-commit hooks avec auto-fix

  # Frontend
  - ESLint + Prettier + TypeScript strict mode
  - Husky pour pre-commit hooks

  # Rust (Tauri)
  - rustfmt + clippy
  ```
 *Validation* :
  - ✅ `pre-commit install` fonctionne
  - ✅ Formatage automatique sur `git commit`
  - ✅ Tous les linters passent sur code vierge
  *Statut* : ✅ Terminé le 28 janvier 2026

### 2.3 CI/CD Pipeline (Jour 2-3) ⭐ CRITIQUE ⭐ ✅
*Feature* : GitHub Actions avec quality gates complets
*Test Plan* : Test manuel du workflow sur branche feature
*Dev* :
  ```yaml
  # Workflows à implémenter :
  1. build-and-test.yml (sur chaque push)
     - Lint backend/frontend/rust
     - Tests unitaires backend (pytest)
     - Tests unitaires frontend (Vitest)
     - Build Tauri (vérification compilation)
     - Upload coverage reports

  2. e2e-tests.yml (sur PR vers main)
     - Tests Playwright (4 scénarios critiques)
     - Rapport vidéo/screenshot sur échec

  3. release.yml (sur tag v*)
     - Build cross-platform (Windows, macOS, Linux)
     - Création release GitHub avec artefacts
  ```
 *Validation* :
  - ✅ Pipeline exécute tous les jobs sur push test
  - ✅ Quality gates bloquent les PR avec échecs
  - ✅ Build cross-platform fonctionne localement
  - ✅ Tests Python passent (black, ruff, mypy, pytest)
*Statut* : ✅ Terminé le 28 janvier 2026 (workflows validés, CI opérationnel)

### 2.4 Monitoring & Métriques (Jour 3-4)
*Feature* : Dashboard local Prometheus/Grafana + métriques qualité
*Test Plan* : Vérification que les métriques sont exposées et collectées
*Dev* :
  ```python
  # backend/src/monitoring/metrics.py
  - Métriques performance : latence API, temps génération
  - Métriques qualité : scores matching, feedback utilisateurs
  - Métriques système : CPU, mémoire, disque
  - Logs structurés avec structlog

  # Dashboard Grafana (localhost:3001)
  - Panels performance, qualité, usage, système
  - Alertes locales (ex: latence > 5s, mémoire > 80%)
  ```
*Validation* :
  - ✅ Endpoint `/metrics` expose les métriques Prometheus
  - ✅ Tests unitaires pour toutes les métriques (coverage > 50%)
  - ✅ Tests d'intégration vérifiant l'endpoint /metrics
  - ✅ Configuration Prometheus pour scraping (fichier YAML)
  - ✅ Template dashboard Grafana (JSON) créé
  *Statut* : ✅ Terminé le 28 janvier 2026 (métriques de base implémentées, Grafana à configurer en runtime)

 ### 2.5 Environnement de Dev "Zero Configuration" (Jour 4)
*Feature* : Scripts setup automatique pour nouveaux contributeurs
*Test Plan* : Test sur environnement vierge (Docker ou VM)
*Dev* :
  ```bash
  # scripts/dev/setup.sh
  - Installation automatique Python/Node/Rust
  - Configuration venv + dépendances
  - Setup pre-commit hooks
  - Vérification APIs externes (Gemini, France Travail)

  # scripts/dev/start.sh
  - Lancement backend Python
  - Lancement frontend Tauri en dev
  - Ouverture dashboard monitoring
  ```
  *Validation* :
  - ✅ `./scripts/dev/setup.sh` fonctionne sur Ubuntu (backend Python)
  - ✅ `./scripts/dev/start.sh` lance backend Python
  - ✅ Pre-commit hooks configurés et fonctionnels
  *Statut* : ✅ Terminé le 28 janvier 2026 (scripts backend fonctionnels, frontend à configurer)

---

## 3. PHASE 1 : CŒUR DU SYSTÈME - BACKEND PYTHON
**Durée estimée** : 7-10 jours
**Objectif** : Implémenter le backend Python avec tests complets
**Approche** : TDD strict, module par module

### 3.1 Module 1 : Models & Database (2 jours)
*Feature* : Modèles SQLAlchemy + migrations SQLite
*Test Plan* : Tests CRUD complets avec factory fixtures
*Dev* :
  ```python
  # backend/src/database/models.py
  - Users, AnonymizedProfiles, JobOffers, Applications
  - ConversationHistory, Feedback (conformément TECH_SPECS)

  # backend/src/database/migrations.py
  - Système de migrations versionnées
  - Scripts rollback/forward
  ```
*Validation* :
  - ✅ Tests CRUD passent à 100%
  - ✅ Migrations appliquées sans erreur
  - ✅ Relations foreign key fonctionnelles

### 3.2 Module 2 : Services de Base (3 jours)
*Feature* : Services métier de base avec tests unitaires
*Test Plan* : TDD - écrire tests avant implémentation
*Dev* :
  ```python
  # 1. CV Service (analyse, anonymisation)
  - test_cv_processing.py (TDD)
  - test_anonymization.py

  # 2. Embedding Service (Gemini text-embedding-004)
  - test_embedding_service.py avec mocks

  # 3. Vector Store Service (ChromaDB)
  - test_vector_store.py avec base de test

  # 4. Cache Service (Redis pour offres France Travail)
  - test_cache_service.py
  ```
*Validation* :
  - ✅ Coverage > 85% pour chaque service
  - ✅ Mocks des APIs externes fonctionnels
  - ✅ Tests isolés (pas de dépendances externes)

### 3.3 Module 3 : API FastAPI + JSON-RPC (2 jours)
*Feature* : Endpoints FastAPI + communication JSON-RPC avec Tauri
*Test Plan* : Tests d'intégration API avec TestClient
*Dev* :
  ```python
  # backend/src/api/rpc_server.py
  - JSON-RPC 2.0 over stdin/stdout
  - Gestion sessions, erreurs, logging

  # backend/src/api/endpoints.py
  - FastAPI endpoints (health, metrics, debug)
  - Documentation OpenAPI automatique

  # Tests d'intégration
  - test_api_integration.py (flux complets)
  - test_jsonrpc_protocol.py
  ```
*Validation* :
  - ✅ API docs accessibles sur `/docs`
  - ✅ JSON-RPC communication testée avec mock Tauri
  - ✅ Tests d'intégration couvrent les flux principaux

### 3.4 Cool Down & Refactoring (1 jour)
*Feature* : Revue de code, refactoring, amélioration tests
*Test Plan* : Exécuter tous les tests + benchmarks performance
*Dev* :
  ```bash
  # Activités
  - Revue coverage reports (identifier faiblesses)
  - Refactoring code smells identifiés
  - Optimisation requêtes DB
  - Ajout tests manquants

  # Métriques
  - Mesurer temps d'exécution tests
  - Vérifier performances benchmarks
  ```
*Validation* :
  - ✅ Coverage backend > 85%
  - ✅ Temps d'exécution tests < 2 minutes
  - ✅ Aucun code smell majeur (analyse SonarQube locale)

---

## 4. PHASE 2 : AGENTS IA & RAG SYSTEM
**Durée estimée** : 7-10 jours
**Objectif** : Implémenter les agents LangGraph/CrewAI + système RAG
**Approche** : Tests avec mocks LLM, validation qualité matching

### 4.1 Module 4 : RAG avec LlamaIndex (3 jours)
*Feature* : Système RAG complet pour matching CV/offres
*Test Plan* : Tests qualité matching avec dataset de test
*Dev* :
  ```python
  # backend/src/rag/core.py
  - Initialisation ChromaDB + embeddings
  - Indexation offres France Travail
  - Recherche similarité cosinus

  # Tests qualité
  - test_rag_quality.py (dataset annoté manuellement)
  - Vérification scores matching > 0.7 pour vrais matchs
  - Test re-ranking avec LLM mocké
  ```
*Validation* :
  - ✅ Matching retourne offres pertinentes (test manuel)
  - ✅ Scores calculés correctement (tests unitaires)
  - ✅ Performance < 3s pour 100 offres (benchmark)

### 4.2 Module 5 : Agents LangGraph (4 jours)
*Feature* : Orchestration multi-agents avec état session
*Test Plan* : Tests workflows complets avec mocks LLM
*Dev* :
  ```python
  # backend/src/agents/orchestrator.py
  - StateGraph avec UserSessionState
  - Agents : coach, researcher, writer, interviewer

  # Tests workflow
  - test_agent_workflows.py (scénarios complets)
  - Validation transitions d'état
  - Tests timeouts et erreurs
  ```
*Validation* :
  - ✅ Workflow complet exécuté sans erreur
  - ✅ États persistés correctement
  - ✅ Gestion erreurs robuste (API failures)

### 4.3 Module 6 : Génération Contenu (3 jours)
*Feature* : Génération lettres de motivation + briefings entretien
*Test Plan* : Tests qualité génération avec prompts validation
*Dev* :
  ```python
  # backend/src/services/letter_generator.py
  - Template engine avec variables
  - Personnalisation ton/longueur
  - Validation longueur (300-500 mots)

  # Tests qualité
  - test_letter_quality.py (vérification contenu)
  - Test cohérence avec profil/offre
  - Test formatage HTML/PDF
  ```
*Validation* :
  - ✅ Lettres générées en < 10s
  - ✅ Qualité satisfaisante (revue manuelle échantillon)
  - ✅ Formats multiples supportés (HTML, PDF, markdown)

### 4.4 Cool Down & Amélioration Matching (1 jour)
*Feature* : Fine-tuning embedding + optimisation prompts
*Test Plan* : A/B testing prompts avec dataset de validation
*Dev* :
  ```python
  # Optimisations
  - Fine-tuning prompts agents (coach, writer)
  - Optimisation embedding queries
  - Cache stratégique embeddings

  # Validation
  - Comparaison qualité avant/après
  - Benchmark performance
  ```
*Validation* :
  - ✅ Amélioration scores matching mesurable
  - ✅ Réduction latence génération
  - ✅ Prompts optimisés validés

---

## 5. PHASE 3 : FRONTEND TAURI + NEXT.JS
**Durée estimée** : 10-14 jours
**Objectif** : Interface desktop avec tests composants + E2E
**Approche** : Composants testés individuellement, puis intégration

### 5.1 Module 7 : Design System & Composants de Base (3 jours)
*Feature* : Implémentation design system conforme DESIGN.md
*Test Plan* : Tests snapshot + interactions composants
*Dev* :
  ```typescript
  // frontend/src/components/ui/ (shadcn/ui adapté)
  - Button, Card, Input, Dialog, etc.
  - TimelineProgress (composant critique)
  - ChatMessage (bulles conversation)

  // Tests
  - Tests snapshot avec Vitest
  - Tests interactions avec Testing Library
  - Tests accessibilité (axe-core)
  ```
*Validation* :
  - ✅ Tous les composants rendent correctement
  - ✅ Accessibilité conforme (contraste, aria-labels)
  - ✅ Tests snapshot à jour

### 5.2 Module 8 : Écrans Principaux (4 jours)
*Feature* : Implémentation des 5 écrans clés
*Test Plan* : Tests composants + intégration avec mocks API
*Dev* :
  ```typescript
  // 1. Écran Accueil (CV import)
  - Drag & drop avec preview
  - Anonymization canvas

  // 2. Écran Conversation
  - Chat interface temps réel
  - Typing indicators

  // 3. Écran Recherche Offres
  - Liste cartes avec filtres
  - Pagination infinite scroll

  // 4. Écran Génération Lettre
  - Éditeur deux colonnes
  - Prévisualisation PDF

  // 5. Dashboard
  - Kanban drag & drop
  - Graphiques statistiques
  ```
*Validation* :
  - ✅ Chaque écran fonctionne avec mocks
  - ✅ Navigation entre écrans fluide
  - ✅ États loading/error/success gérés

### 5.3 Module 9 : Intégration Tauri (3 jours)
*Feature* : Communication backend/frontend via Tauri commands
*Test Plan* : Tests E2E avec Playwright + mocks Tauri
*Dev* :
  ```rust
  // frontend/src-tauri/src/lib.rs
  - Tauri commands pour chaque opération
  - Gestion sidecar Python
  - IPC sécurisé

  // Tests intégration
  - test_tauri_commands.rs
  - Mock sidecar pour tests
  ```
*Validation* :
  - ✅ Communication Tauri-Python fonctionnelle
  - ✅ Gestion erreurs cross-process
  - ✅ Performance IPC acceptable (< 100ms)

### 5.4 Module 10 : Tests E2E Critiques (2 jours)
*Feature* : Automatisation des 4 flux utilisateurs critiques
*Test Plan* : Scénarios Playwright avec screenshots/vidéos
*Dev* :
  ```typescript
  // frontend/tests/e2e/critical-flows.spec.ts
  1. Import CV → Analyse → Conversation
  2. Recherche → Matching → Sélection offre
  3. Génération lettre → Personnalisation → Export
  4. Dashboard → Suivi → Mise à jour statut

  // Configuration
  - Base de données test isolée
  - Mocks APIs externes
  - Videos sur échec
  ```
*Validation* :
  - ✅ 4 flux E2E passent à 100%
  - ✅ Tests isolés (pas de side effects)
  - ✅ Rapport HTML généré automatiquement

### 5.5 Cool Down & Polish (2 jours)
*Feature* : Améliorations UX, animations, performances
*Test Plan* : Tests performance Lighthouse + UX review
*Dev* :
  ```bash
  # Activités
  - Optimisation bundle size (analyzer)
  - Ajout micro-animations (Framer Motion)
  - Amélioration temps de chargement
  - Fix bugs mineurs UX

  # Tests
  - Lighthouse audits
  - Tests performance (Web Vitals)
  ```
*Validation* :
  - ✅ Performance score > 90 (Lighthouse)
  - ✅ Bundle size < 5MB (gzipped)
  - ✅ UX smooth (60 FPS stable)

---

## 6. PHASE 4 : INTÉGRATION & VALIDATION MVP
**Durée estimée** : 5-7 jours
**Objectif** : Intégration complète + validation MVP
**Approche** : Tests end-to-end réels, préparation release

### 6.1 Module 11 : Intégration Totale (2 jours)
*Feature* : Assemblage tous les modules + tests intégration
*Test Plan* : Tests système complets avec environnement réaliste
*Dev* :
  ```bash
  # Scripts d'intégration
  - scripts/integration/test-full-system.sh
  - Base de données test + données réalistes
  - Mocks Gemini API (pour tests)

  # Tests
  - Scénarios utilisateur complets
  - Tests performance système
  - Tests robustesse (erreurs API)
  ```
*Validation* :
  - ✅ Système complet fonctionne localement
  - ✅ Tous les tests intégration passent
  - ✅ Performance cibles atteintes (TECH_SPECS)

### 6.2 Module 12 : Tests Utilisateur Réels (2 jours)
*Feature* : Validation avec scénarios personas du PRD
*Test Plan* : Exécution manuelle scénarios Julien/Sophie/Léa
*Dev* :
  ```bash
  # Scénarios test
  1. Julien (reconversion) : CV commercial → offres tech
  2. Sophie (cadre senior) : CV long → mise en valeur expérience
  3. Léa (jeune diplômée) : CV léger → construction profil

  # Collecte métriques
  - Taux matching pertinent
  - Satisfaction utilisateur (simulée)
  - Temps par étape
  ```
*Validation* :
  - ✅ Scénarios exécutés sans blocage
  - ✅ Matching pertinent pour chaque persona
  - ✅ Feedback positif sur expérience

### 6.3 Module 13 : Préparation Release (2 jours)
*Feature* : Finalisation packaging, docs, monitoring production
*Test Plan* : Tests installation sur environnements vierges
*Dev* :
  ```bash
  # Packaging
  - Build Windows (.msi), macOS (.dmg), Linux (.AppImage)
  - Code signing (optionnel MVP)
  - Auto-updater configuration

  # Documentation
  - Guide utilisateur (PDF + inline)
  - Guide dépannage
  - README release notes

  # Monitoring production
  - Configuration alerts seuils
  - Logs rotation
  - Backup données utilisateur
  ```
*Validation* :
  - ✅ Build cross-platform fonctionnel
  - ✅ Installation réussie sur OS cibles
  - ✅ Documentation complète et claire

### 6.4 Module 14 : Release Candidate & Bug Bash (1 jour)
*Feature* : Dernière validation avant v1.0
*Test Plan* : Bug bash intensif + tests exploratoires
*Dev* :
  ```bash
  # Activités
  - Bug bash : tester toutes les fonctionnalités
  - Tests exploratoires UX
  - Tests charge (simulation usage intensif)
  - Revue sécurité (audit manuel)

  # Critères release
  - Aucun bug critique (blocker)
  - < 5 bugs majeurs (high)
  - Performance cibles atteintes
  ```
*Validation* :
  - ✅ Checklist release complétée
  - ✅ Aucun blocker bug
  - ✅ Approval pour v1.0.0

---

## 7. GESTION DE LA DETTE & REFACTORING

### 7.1 Cool Down Réguliers
**Après chaque Phase** : 1 jour dédié à
- Revue coverage tests
- Refactoring code smells
- Optimisation performance
- Documentation technique

### 7.2 Revue de Code Automatisée
- **Chaque commit** : pre-commit hooks (format, lint, tests unitaires)
- **Chaque PR** : CI/CD quality gates (tests, coverage, build)
- **Hebdomadaire** : Revue manuelle design/code (même solo)

### 7.3 Métriques Qualité Suivies
| Métrique | Cible | Mesure |
|----------|-------|---------|
| **Test Coverage Backend** | > 85% | pytest --cov |
| **Test Coverage Frontend** | > 75% | vitest --coverage |
| **Build Success Rate** | 100% | CI/CD history |
| **E2E Test Pass Rate** | 100% | Playwright reports |
| **Performance Targets** | Voir TECH_SPECS | Benchmarks réguliers |
| **Code Smells** | < 10 majeurs | SonarQube local |

### 7.4 Plan d'Amélioration Continue
1. **Post-MVP** : Fine-tuning modèles sur feedback réel
2. **Phase 2** : Intégration nouvelles sources offres
3. **Phase 3** : Version mobile + collaboration
4. **Évolution architecture** : Revue trimestrielle

---

## 8. CALENDRIER ESTIMÉ & MILESTONES

### 8.1 Timeline Globale (Approximation)
- **Phase 0** : J1-J4 → Fondations & CI/CD
- **Phase 1** : J5-J15 → Backend Python (core)
- **Phase 2** : J16-J26 → Agents IA & RAG
- **Phase 3** : J27-J40 → Frontend Tauri + Next.js
- **Phase 4** : J41-J47 → Intégration & Release
- **Buffer** : J48-J60 → Contingence + améliorations

**Total estimé** : 8-12 semaines pour MVP complet

### 8.2 Milestones Clés
1. **M1** (J4) : CI/CD opérationnel + qualité automatisée
2. **M2** (J15) : Backend Python 100% testé + coverage > 85%
3. **M3** (J26) : Agents IA fonctionnels + matching qualité validé
4. **M4** (J40) : Frontend complet + tests E2E passants
5. **M5** (J47) : MVP v1.0.0 prêt pour release

### 8.3 Critères de Succès Phase par Phase
- **Phase 0** : Pipeline CI/CD bloque les PR avec échecs
- **Phase 1** : Backend coverage > 85%, tous tests verts
- **Phase 2** : Matching qualité > 70% pertinence (tests)
- **Phase 3** : 4 flux E2E critiques automatisés + passants
- **Phase 4** : Aucun blocker bug, performance cibles atteintes

---

## 9. RISQUES & MITIGATIONS

### 9.1 Risques Techniques
| Risque | Probabilité | Impact | Mitigation |
|--------|-------------|---------|------------|
| **API France Travail indisponible** | Moyenne | Élevé | Cache Redis 24h + fallback web search |
| **Gemini API costs/limits** | Faible | Moyen | Monitoring usage + alertes seuils |
| **Performance matching RAG** | Moyenne | Moyen | Optimisation embeddings + cache stratégique |
| **Cross-platform build issues** | Faible | Élevé | CI/CD early + test réguliers |

### 9.2 Risques Qualité
| Risque | Probabilité | Impact | Mitigation |
|--------|-------------|---------|------------|
| **Dette technique accumulation** | Faible | Élevé | Cool Down obligatoires + métriques |
| **Tests flaky (E2E)** | Moyenne | Moyen | Tests isolés + retry mechanism |
| **UX complexe pour utilisateurs** | Faible | Élevé | Tests utilisateur Phase 4 + itérations |

### 9.3 Plan de Contingence
- **Buffer intégré** : 20% temps supplémentaire prévu
- **Feature trimming** : Liste claire des "could have" à retirer si nécessaire
- **Rollback simple** : Système migrations database versionné

---

## 10. SUIVI & REPORTING

### 10.1 Outils de Suivi
- **GitHub Projects** : Board Kanban avec colonnes (TODO, In Progress, Done)
- **CI/CD Dashboard** : GitHub Actions status + coverage trends
- **Monitoring Local** : Grafana dashboard métriques qualité
- **Test Reports** : Playwright HTML reports + videos

### 10.2 Rituels Quotidiens
1. **Morning check** : CI/CD status + tests overnight
2. **Work session** : Focus sur 1 module avec TDD
3. **Evening commit** : Push avec tests + vérification pipeline
4. **Weekly review** : Avancement vs planning + ajustements

### 10.3 Livrables par Phase
- **Phase 0** : Repo structuré + CI/CD + monitoring
- **Phase 1** : Backend Python avec tests complets
- **Phase 2** : Système RAG + agents avec validation qualité
- **Phase 3** : Application desktop fonctionnelle + tests E2E
- **Phase 4** : MVP v1.0.0 prêt pour distribution

---

## 11. ANNEXES

### 11.1 Références
- **PRD.md** : Exigences fonctionnelles, user stories, KPIs
- **TECH_SPECS.md** : Stack technique, architecture, APIs
- **DESIGN.md** : Guidelines UX/UI, composants, interactions

### 11.2 Checklist Démarrage
- [ ] Lire et comprendre les 3 documents de référence
- [ ] Cloner repo + vérifier environnement dev
- [ ] Exécuter `./scripts/dev/setup.sh` (après création)
- [ ] Vérifier accès APIs (Gemini, France Travail)
- [ ] Configurer secrets locaux (API keys)

### 11.3 Contacts & Support
- **Project Manager** : QA Lead (via cette conversation)
- **Agent IA** : Assistant développement (toujours disponible)
- **Documentation** : README.md + comments in code

---

**DOCUMENT VALIDÉ LE 28 JANVIER 2026**
*Ce planning est le contrat qualité pour le développement de Chat Emploi. Toute déviation doit être documentée et justifiée.*

*"La qualité n'est jamais un accident ; c'est toujours le résultat d'un effort intelligent." - John Ruskin*
