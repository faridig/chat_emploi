# PLANNING.md - Chat Emploi
## Roadmap & Stratégie de Test "Zero Debt"
### Version 1.0 - Planning de Développement
**Date** : 27 janvier 2026  
**Project Manager** : QA Lead  
**Statut** : Plan Validé  

---

## 1. PHILOSOPHIE DE DÉVELOPPEMENT

### 1.1 Règles d'Or "Clean Code"
- **Pas de merge sans tests verts** : CI/CD bloque toute PR avec tests échoués
- **Code coverage > 85%** : Minimum pour backend Python, 80% pour frontend TypeScript
- **TDD obligatoire** : Écrire le test AVANT le code pour toute logique métier
- **Review systématique** : Toute PR revue par l'agent IA + validation humaine
- **Documentation vivante** : Les tests servent de spécifications exécutables

### 1.2 Stratégie "Zero Regression"
1. **Tests unitaires** : Couvrent chaque fonction/logique métier (TDD)
2. **Tests intégration** : Vérifient les interactions entre composants
3. **Tests E2E** : Simulent les flux utilisateur complets (Playwright)
4. **Tests performance** : Garantissent les SLA (matching < 5s, génération < 10s)
5. **Tests sécurité** : Scan automatique dépendances + code

### 1.3 Workflow de Développement
```
1. Plan → 2. Test → 3. Dev → 4. Review → 5. Merge → 6. Monitor
   ↓          ↓         ↓         ↓         ↓         ↓
  PLANNING   TDD     Code     CI/CD    Déploy   Dashboard
   .md       Red    Green    Pass     Prod     Quality
```

---

## 2. PHASE 0 : FONDATIONS & OUTILLAGE (SEMAINES 1-2)

**Objectif** : Mettre en place l'infrastructure solide pour garantir la qualité dès la première ligne de code.

### 2.1 Mise en Place du Repo & Structure
- **Task** : Initialiser la structure du projet selon TECH_SPECS
- **Test Plan** : Vérifier que la structure correspond au diagramme d'architecture
- **Dev** : 
  ```bash
  # Structure du projet
  mkdir -p frontend/{src/{app,components,lib,styles,hooks},src-tauri/src,public}
  mkdir -p backend/{src/{api,agents,services,database,rag,monitoring},tests}
  mkdir -p shared/{types,schemas,protocol}
  mkdir -p scripts/{build,deploy,dev} docs/{api,architecture,user} infrastructure/{github,grafana,prometheus}
  ```
- **Validation** : `tree -L 3` montre la structure correcte

### 2.2 Configuration CI/CD (GitHub Actions)
- **Task** : Mise en place pipeline complète avec qualité code
- **Test Plan** : Vérifier que les workflows déclenchent sur push/PR
- **Dev** : 
  - `.github/workflows/build-test.yml` : Tests + build cross-platform
  - `.github/workflows/release.yml` : Release automatisée sur tags
  - `.github/workflows/codeql.yml` : Analyse sécurité
  - `pre-commit-config.yaml` : Hooks qualité code
- **Validation** : 
  - ✅ Pipeline passe sur PR dummy
  - ✅ Couverture code > 0% (même si vide)
  - ✅ Build Tauri réussi (hello world)

### 2.3 Configuration Linter/Formatter
- **Task** : Standardiser le code sur 3 langages (Rust, Python, TypeScript)
- **Test Plan** : Vérifier que le linting échoue sur code mal formaté
- **Dev** :
  ```yaml
  # Backend Python
  ruff check --fix
  black .
  mypy src/
  
  # Frontend TypeScript  
  eslint --fix
  prettier --write
  tsc --noEmit
  
  # Rust (Tauri)
  cargo fmt
  cargo clippy
  ```
- **Validation** : Commits rejetés si linting échoue

### 2.4 Setup Environnement de Test
- **Task** : Configurer la stack de testing complète
- **Test Plan** : Vérifier que tous les types de tests peuvent s'exécuter
- **Dev** :
  ```bash
  # Backend: pytest avec coverage
  pytest tests/unit/ -v --cov=src --cov-report=html
  
  # Frontend: Vitest + Playwright
  npm test -- --coverage
  npm run test:e2e
  
  # Monitoring tests
  prometheus.yml + grafana dashboards
  ```
- **Validation** : 
  - ✅ Tests unitaires exécutables (même vides)
  - ✅ Coverage reports générés
  - ✅ Dashboard Grafana accessible localhost:3001

### 2.5 Template de Progression (PROGRESS_TRACKER.md)
- **Task** : Créer le système de tracking pour l'agent IA
- **Test Plan** : Vérifier que le tracker peut être mis à jour automatiquement
- **Dev** :
  ```markdown
  # PROGRESS_TRACKER.md
  ## Règles
  - [x] Tâche terminée
  - [ ] Tâche en cours [IN_PROGRESS - Commit: abc123]
  - [ ] Tâche à faire
  - [!] Tâche bloquée (raison)
  
  ## Template par tâche
  ### [ID] Nom Tâche
  - **État**: [STATUS]
  - **Commit actuel**: abc123 (lien)
  - **Prochain step**: Description
  - **Tests passants**: [x] Unit [ ] Integration [ ] E2E
  - **Blockers**: Aucun
  ```
- **Validation** : Fichier créé et versionné, format valide

---

## 3. PHASE 1 : CORE INFRASTRUCTURE (SEMAINES 3-4)

**Objectif** : Implémenter l'architecture de base Tauri + Python sidecar avec communication IPC.

### 3.1 Setup Tauri Application Basique
- **Feature** : Application desktop minimale avec fenêtre principale
- **Test Plan** :
  - Test E2E : Application démarre sans erreur
  - Test unitaire : IPC Rust functions
  - Test performance : Startup < 5s
- **Dev** :
  - `frontend/package.json` : Dépendances Tauri 2.0 + Next.js 15
  - `frontend/src-tauri/` : Configuration Rust + build
  - Fenêtre principale avec layout basique (header, content, footer)
- **Validation** : 
  - ✅ `npm run tauri dev` lance l'app
  - ✅ Build réussit sur OS courant
  - ✅ Fenêtre répond aux interactions basiques

### 3.2 Python Backend Sidecar Process
- **Feature** : Processus Python qui communique avec Tauri via stdin/stdout
- **Test Plan** :
  - Test intégration : Envoi/réception messages JSON-RPC
  - Test unitaire : Gestion processus (start/stop/restart)
  - Test sécurité : Isolation filesystem/network
- **Dev** :
  - `backend/src/api/server.py` : FastAPI minimal
  - `backend/src/ipc/handler.py` : JSON-RPC 2.0 over stdio
  - Gestion cycle de vie (start, health checks, graceful shutdown)
- **Validation** :
  - ✅ Processus Python démarre avec Tauri
  - ✅ Communication bidirectionnelle fonctionnelle
  - ✅ Messages JSON-RPC parsés correctement

### 3.3 Protocol JSON-RPC 2.0
- **Feature** : Définition du protocol de communication Tauri ↔ Python
- **Test Plan** :
  - Test contrat : Schémas Pydantic valident messages
  - Test erreur : Gestion erreurs protocol (malformed, timeout)
  - Test performance : Latence < 100ms pour appels simples
- **Dev** :
  - `shared/protocol/rpc_schema.py` : Types TypeScript + Python
  - Méthodes basiques : `ping`, `echo`, `get_version`
  - Error handling standardisé
- **Validation** :
  - ✅ 100% des messages valident les schémas
  - ✅ Erreurs remontées avec stack trace
  - ✅ Documentation OpenAPI générée automatiquement

### 3.4 Base de Données SQLite + Modèles
- **Feature** : Schéma de base SQLite avec SQLAlchemy 2.0
- **Test Plan** :
  - Test unitaire : CRUD operations pour chaque modèle
  - Test migration : Scripts de migration forward/backward
  - Test performance : Requêtes < 50ms pour datasets de test
- **Dev** :
  - `backend/src/database/models.py` : Users, Profiles, Offers, Applications
  - `backend/src/database/migrations/` : Alembic migrations
  - Chiffrement AES-256 pour données sensibles
- **Validation** :
  - ✅ Schéma correspond à TECH_SPECS section 3.1
  - ✅ Migrations réversibles
  - ✅ Données chiffrées au repos

---

## 4. PHASE 2 : CV PROCESSING PIPELINE (SEMAINES 5-6)

**Objectif** : Implémenter l'import, anonymisation et analyse intelligente des CV.

### 4.1 Interface Import CV (Frontend)
- **Feature** : Drag & drop PDF/DOCX avec prévisualisation
- **Test Plan** :
  - Test E2E : Upload fichier → affichage preview
  - Test unitaire : Validation formats (PDF, DOCX, TXT)
  - Test accessibilité : Navigation clavier, screen readers
- **Dev** :
  - Composant `CVUploader` avec react-dropzone
  - Prévisualisation PDF via react-pdf
  - Interface de sélection zones sensibles (canvas drawing)
- **Validation** :
  - ✅ Support 3 formats principaux
  - ✅ Prévisualisation fidèle
  - ✅ Sélection zones rectangulaires fonctionnelle

### 4.2 Anonymisation Visuelle Client-side
- **Feature** : Application de masques noirs sur zones sensibles
- **Test Plan** :
  - Test unitaire : Conversion PDF → canvas → pixels noirs
  - Test sécurité : Original supprimé de la mémoire
  - Test qualité : Zones anonymisées illisibles mais structure préservée
- **Dev** :
  - Pipeline PDF.js → Canvas → pixel manipulation
  - Export PDF anonymisé (pdf-lib)
  - Secure delete des buffers temporaires
- **Validation** :
  - ✅ PDF anonymisé ne contient pas de texte dans les zones
  - ✅ Performances : < 3s pour CV 5 pages
  - ✅ Confidentialité : Aucune trace des données originales

### 4.3 Analyse CV avec Gemini API
- **Feature** : Extraction structurée des compétences/expériences
- **Test Plan** :
  - Test intégration : Appel Gemini API avec retry logic
  - Test unitaire : Parsing réponse JSON → modèle Python
  - Test qualité : Extraction précise sur CVs de test
- **Dev** :
  - Service `CVAnalyzer` avec prompt engineering
  - Structuration : skills, experiences, education, languages
  - Cache résultats (24h) pour éviter coûts inutiles
- **Validation** :
  - ✅ Extraction > 90% précise sur dataset test
  - ✅ Gestion erreurs API (rate limiting, downtime)
  - ✅ Coût contrôlé < $0.10 par CV analysé

### 4.4 Embedding & Vector Storage
- **Feature** : Création embeddings Gemini et stockage ChromaDB
- **Test Plan** :
  - Test unitaire : Similarité cosinus entre embeddings
  - Test performance : Indexation < 2s par CV
  - Test intégration : Recherche vectorielle retourne résultats pertinents
- **Dev** :
  - Service `EmbeddingService` avec Gemini `text-embedding-004`
  - ChromaDB collections : `user_profiles`, `job_offers`
  - Métriques qualité embedding (dimension reduction visualization)
- **Validation** :
  - ✅ Embeddings dimension 768 comme attendu
  - ✅ Recherche similarité retourne CVs similaires
  - ✅ Persistance ChromaDB survive restart

---

## 5. PHASE 3 : JOB MARKET INTEGRATION (SEMAINES 7-8)

**Objectif** : Intégration API France Travail et système de matching RAG.

### 5.1 Client API France Travail
- **Feature** : Recherche offres avec filtres (localisation, contrat, métier)
- **Test Plan** :
  - Test intégration : Appel API réel avec credentials mock
  - Test unitaire : Parsing réponse JSON normalisée
  - Test cache : Redis TTL 24h fonctionnel
- **Dev** :
  - Client API avec httpx (async)
  - Normalisation data modèle `JobOffer`
  - Cache Redis Stack avec invalidation smart
- **Validation** :
  - ✅ Récupération 50+ offres pour différents filtres
  - ✅ Cache réduit appels API de 90%+
  - ✅ Gestion pagination (range 0-149)

### 5.2 Embedding des Offres d'Emploi
- **Feature** : Création embeddings pour chaque offre récupérée
- **Test Plan** :
  - Test performance : Batch embedding 100 offres < 30s
  - Test qualité : Similarité sémantique offre-CV cohérente
  - Test unitaire : Dédoublonnement offres identiques
- **Dev** :
  - Pipeline async batch processing
  - Dédoublonnement par hash contenu
  - Mise à jour incrémentale (nouvelles offres seulement)
- **Validation** :
  - ✅ Base vectorielle > 1000 offres embeddings
  - ✅ Dédoublonnement efficace (offres dupliquées supprimées)
  - ✅ Mise à jour quotidienne automatique

### 5.3 RAG Matching System
- **Feature** : Recherche similarité cosinus + re-ranking LLM
- **Test Plan** :
  - Test unitaire : Calcul similarité vectorielle
  - Test intégration : Pipeline complet CV → embedding → matching
  - Test qualité : Top 5 offres pertinentes (validation manuelle)
- **Dev** :
  - Service `RAGMatcher` avec LlamaIndex
  - Similarité cosinus + filtrage géographique
  - Re-ranking avec Gemini Pro pour pertinence sémantique
- **Validation** :
  - ✅ Matching < 5s comme spécifié dans PRD
  - ✅ Score pertinence > 70% pour matching "bon"
  - ✅ Explication matching générée (pourquoi cette offre)

### 5.4 Cache & Performance Optimization
- **Feature** : Système de cache multi-niveaux pour performances
- **Test Plan** :
  - Test performance : Latence réduite de 50%+ avec cache
  - Test unitaire : Invalidation cache sur données obsolètes
  - Test charge : 100 requêtes concurrentes < 10s
- **Dev** :
  - Redis cache : offres, embeddings, résultats matching
  - Memory cache : sessions utilisateur, états conversation
  - CDN-like : pré-calcul résultats pour filtres communs
- **Validation** :
  - ✅ 95% cache hit rate après warmup
  - ✅ Latence moyenne < 2s pour recherche
  - ✅ Memory usage < 500MB pour cache

---

## 6. PHASE 4 : AGENT CONVERSATIONNEL (SEMAINES 9-10)

**Objectif** : Implémenter l'agent coach conversationnel avec LangGraph/CrewAI.

### 6.1 Architecture Multi-Agents
- **Feature** : Orchestration LangGraph avec 4 agents spécialisés
- **Test Plan** :
  - Test unitaire : Chaque agent répond correctement à son rôle
  - Test intégration : Collaboration agents (handoff)
  - Test performance : Temps réponse < 3s par agent
- **Dev** :
  - Agents : Coach, Researcher, Writer, InterviewCoach
  - Workflow LangGraph avec state management
  - Memory conversation (10 derniers messages)
- **Validation** :
  - ✅ Chaque agent respecte son backstory/role
  - ✅ Handoff fluide entre agents
  - ✅ Memory conserve le contexte

### 6.2 Agent Coach (Conversation Principal)
- **Feature** : Dialogue empathique avec compréhension contexte
- **Test Plan** :
  - Test qualité : Ton "coach bienveillant" vérifié par humain
  - Test unitaire : Réponses contextuelles (référence au CV)
  - Test intégration : Suggestions proactives basées sur profil
- **Dev** :
  - Prompt engineering avec personnalité définie
  - System prompt : "Vous êtes Alex, coach emploi empathique..."
  - Template responses pour scénarios communs
- **Validation** :
  - ✅ Score empathie > 4/5 par évaluateurs humains
  - ✅ Référence aux données CV dans 80%+ des réponses
  - ✅ Suggestions pertinentes (formations, compétences à développer)

### 6.3 Interface Chat Frontend
- **Feature** : Interface conversationnelle type WhatsApp/Telegram
- **Test Plan** :
  - Test E2E : Envoi message → réponse agent
  - Test unitaire : Composant MessageBubble, ChatInput
  - Test performance : 60 FPS pendant scroll historique
- **Dev** :
  - Composants React : ChatContainer, MessageList, InputArea
  - Indicateur "Agent écrit..." avec animation
  - Historique conversation (session + persistant)
- **Validation** :
  - ✅ UX fluide comme messaging app moderne
  - ✅ Indicateur typing visible
  - ✅ Historique restauré après restart

### 6.4 WebSocket Communication
- **Feature** : Communication temps réel frontend ↔ backend agents
- **Test Plan** :
  - Test intégration : Connection WS stable + reconnection
  - Test unitaire : Messages sérialisation/désérialisation
  - Test charge : 100 connections simultanées stables
- **Dev** :
  - FastAPI WebSocket endpoint
  - Client WebSocket React avec reconnection logic
  - Heartbeat/ping pour détection déconnexion
- **Validation** :
  - ✅ Latence < 100ms pour messages
  - ✅ Reconnection automatique après perte réseau
  - ✅ Gestion graceful des déconnexions

---

## 7. PHASE 5 : GENERATION DOCUMENTS (SEMAINES 11-12)

**Objectif** : Génération de lettres de motivation personnalisées et préparation entretien.

### 7.1 Generation Lettre de Motivation
- **Feature** : Lettre sur-mesure basée CV + offre spécifique
- **Test Plan** :
  - Test qualité : Lettre pertinente (évaluation humaine)
  - Test unitaire : Template engine avec variables
  - Test performance : Génération < 15s
- **Dev** :
  - Agent Writer avec prompt structuré
  - Template système avec sections variables
  - Post-processing : validation longueur, correction format
- **Validation** :
  - ✅ Lettre 300-500 mots comme spécifié
  - ✅ Intègre éléments CV pertinents pour l'offre
  - ✅ Ton adaptatif (startup vs grand groupe)

### 7.2 Personnalisation & Édition
- **Feature** : Interface de personnalisation (ton, points forts)
- **Test Plan** :
  - Test E2E : Sélection options → regénération lettre
  - Test unitaire : Slider ton (amical → professionnel)
  - Test intégration : Options sauvegardées dans session
- **Dev** :
  - Composant `LetterCustomizer` avec sliders/checkboxes
  - Prévisualisation live des changements
  - Versioning : garder plusieurs versions générées
- **Validation** :
  - ✅ Changements reflétés immédiatement dans preview
  - ✅ Regénération avec nouveaux paramètres < 10s
  - ✅ Historique des versions accessible

### 7.3 Export PDF Professionnel
- **Feature** : Export lettre en PDF avec mise en page pro
- **Test Plan** :
  - Test unitaire : Génération PDF fidèle au HTML
  - Test intégration : Sauvegarde locale + chemin retourné
  - Test qualité : PDF passe validation Adobe Acrobat
- **Dev** :
  - WeasyPrint ou ReportLab pour génération PDF
  - Template CSS professionnel (marges, polices, header/footer)
  - Métadonnées PDF (auteur, titre, keywords)
- **Validation** :
  - ✅ PDF ouvrable dans tous viewers standards
  - ✅ Mise en page A4 correcte (marges 2.5cm)
  - ✅ Qualité impression haute résolution

### 7.4 Préparation Entretien (Agent InterviewCoach)
- **Feature** : Simulation entretien avec feedback personnalisé
- **Test Plan** :
  - Test qualité : Questions adaptées au poste/entreprise
  - Test unitaire : Génération questions types + réponses modèles
  - Test intégration : Analyse réponse utilisateur → feedback
- **Dev** :
  - Agent InterviewCoach avec base de questions par métier
  - Analyse sémantique réponse + suggestions amélioration
  - Mode "préparation intensive" (< 48h avant entretien)
- **Validation** :
  - ✅ Questions pertinentes pour le poste spécifique
  - ✅ Feedback constructif avec exemples concrets
  - ✅ Briefing entreprise (extraction site web)

---

## 8. PHASE 6 : DASHBOARD & MONITORING (SEMAINES 13-14)

**Objectif** : Tableau de bord de suivi candidatures et monitoring complet.

### 8.1 Dashboard Kanban
- **Feature** : Vue drag & drop des candidatures par statut
- **Test Plan** :
  - Test E2E : Drag carte entre colonnes → statut mis à jour
  - Test unitaire : Composant KanbanColumn, KanbanCard
  - Test performance : 100+ cartes affichées fluides
- **Dev** :
  - `@dnd-kit` pour drag & drop
  - Colonnes : Postulées, En cours, Entretiens, Refusées, Acceptées
  - Synchro automatique avec backend SQLite
- **Validation** :
  - ✅ Drag & drop fluide avec animation
  - ✅ Statut mis à jour en temps réel
  - ✅ UI/UX conforme DESIGN.md section 4.5

### 8.2 Statistiques Personnelles
- **Feature** : Graphiques et métriques de recherche d'emploi
- **Test Plan** :
  - Test unitaire : Calculs statistiques (taux réponse, délai moyen)
  - Test intégration : Données réelles → graphiques Recharts
  - Test qualité : Visualisations claires et actionnables
- **Dev** :
  - Composants Recharts : bar charts, line charts, pie charts
  - Métriques : candidatures/semaine, taux réponse, secteur actif
  - Insights automatiques : "Vous avez 90% de succès dans la Tech"
- **Validation** :
  - ✅ Graphiques interactifs (hover details)
  - ✅ Données à jour en temps réel
  - ✅ Insights pertinents détectés

### 8.3 Notes & Rappels
- **Feature** : Système de notes privées + rappels automatiques
- **Test Plan** :
  - Test E2E : Création note → notification rappel
  - Test unitaire : Format date/heure rappels
  - Test intégration : Notifications système (Tauri)
- **Dev** :
  - Éditeur markdown simple pour notes
  - Système de rappels (cron-like)
  - Notifications desktop via Tauri API
- **Validation** :
  - ✅ Rappels déclenchés au bon moment
  - ✅ Notifications visibles même app minimisée
  - ✅ Notes formatées correctement (markdown)

### 8.4 Monitoring Local Prometheus/Grafana
- **Feature** : Dashboard monitoring technique intégré
- **Test Plan** :
  - Test intégration : Métriques exposées sur localhost:9090
  - Test unitaire : Collecteurs Prometheus Python
  - Test qualité : Dashboard Grafana pré-configuré
- **Dev** :
  - Prometheus Python client pour métriques app
  - Dashboard Grafana : performance, usage, qualité
  - Alerting local (desktop notifications)
- **Validation** :
  - ✅ Dashboard accessible http://localhost:3001
  - ✅ Métriques mises à jour en temps réel
  - ✅ Alertes déclenchées sur seuils (ex: latency > 5s)

---

## 9. GESTION DE LA DETTE & REFACTORING

### 9.1 Cool Down Periods
**Après chaque Phase majeure (2 semaines) :**
- **Refactoring** : 2 jours dédiés à améliorer le code
- **Documentation** : 1 jour pour mettre à jour docs/readme
- **Tests maintenance** : 1 jour pour améliorer coverage/performance
- **Bug triage** : 1 jour pour adresser les issues accumulées

### 9.2 Cycle de Refactoring
```
Phase N terminée
    ↓
Cool Down (5 jours)
    ├── Code Review Retrospective
    ├── Performance Profiling
    ├── Security Audit
    ├── Documentation Update
    └── Test Suite Enhancement
    ↓
Phase N+1 commence
```

### 9.3 Métriques de Dette Technique
- **Complexité cyclomatique** : Alerte si > 15 par fonction
- **Code duplication** : Alerte si > 5% duplication
- **Test coverage gaps** : Revue manuelle si < 85%
- **Dependency vulnerabilities** : Patch immédiat si CVE critique

### 9.4 Automatisation Qualité
- **Daily** : Run tests unitaires + linting
- **Weekly** : Run tests E2E complets + security scan
- **Post-Phase** : Performance benchmark + load testing
- **Pre-Release** : Audit sécurité complet + penetration test

---

## 10. SUIVI DE PROGRESSION & ADAPTATION

### 10.1 PROGRESS_TRACKER.md
- **Mise à jour quotidienne** : Automatique via commit hooks
- **État visuel** : [x] Done, [ ] TODO, [!] Blocked, [~] In Progress
- **Lien vers code** : Commit hash + PR number
- **Critères de succès** : Liste checkboxes par tâche

### 10.2 Adaptation du Planning
**Triggers pour réévaluer le planning :**
1. **Vélocité < 70%** attendue pendant 2 semaines
2. **Découverte risque technique** majeur non anticipé
3. **Changement requirements** business (nouveau MUST HAVE)
4. **Feedback utilisateur** early testing indique pivot nécessaire

**Processus d'adaptation :**
1. Pause développement courant
2. Analyse root cause
3. Ajustement planning (reprioritisation)
4. Communication changement + nouvelle estimation
5. Reprise avec nouvelle direction

### 10.3 Critères de Succès Phase par Phase
```
PHASE 0 : ✅ CI/CD opérationnel, tests passants, structure valide
PHASE 1 : ✅ App démarre, IPC fonctionne, DB opérationnelle  
PHASE 2 : ✅ CV import + anonymisation + analyse fonctionnels
PHASE 3 : ✅ Recherche offres + matching RAG opérationnel
PHASE 4 : ✅ Agent conversationnel répond + interface chat
PHASE 5 : ✅ Génération lettre + préparation entretien
PHASE 6 : ✅ Dashboard + monitoring + notifications
MVP COMPLET : ✅ Tous MUST HAVE du PRD implémentés et testés
```

---

## 11. LIVRABLES ATTENDUS

### 11.1 À la fin de chaque Phase
- **Code** : Merge dans main avec tests passants
- **Documentation** : README mise à jour + architecture diagrams
- **Tests** : Coverage report + performance benchmarks
- **Build** : Artifact fonctionnel pour la plateforme courante

### 11.2 À la fin du MVP
- **Application** : Builds Windows (.msi), macOS (.dmg), Linux (.AppImage)
- **Documentation** : 
  - Guide utilisateur complet
  - Guide développeur (setup, architecture, contribution)
  - API documentation (OpenAPI)
- **Qualité** :
  - Test coverage > 85% backend, > 80% frontend
  - Performance SLA respectés (matching < 5s, etc.)
  - Security audit passed (OWASP ASVS Level 1)
- **Monitoring** :
  - Dashboard Grafana avec métriques production
  - Alerting système configuré
  - Logs structurés avec rotation

### 11.3 Pré-requis pour Release v1.0.0
1. ✅ Tous MUST HAVE du PRD implémentés
2. ✅ Tests E2E couvrent tous les flux utilisateur
3. ✅ Performance benchmarks dans les SLA
4. ✅ Security scan clean (snyk, trivy)
5. ✅ Documentation complète utilisateur + développeur
6. ✅ Build cross-platform réussit sur CI
7. ✅ 3 utilisateurs beta testent pendant 1 semaine
8. ✅ Feedback positif (NPS > 4/5)

---

## 12. RISQUES IDENTIFIÉS & MITIGATION

### 12.1 Risques Techniques
| Risque | Probabilité | Impact | Mitigation |
|--------|-------------|--------|------------|
| API France Travail changes | Medium | High | Abstraction layer + mocks complets |
| Gemini API costs exceed budget | Medium | Medium | Cache agressif + monitoring coûts |
| Tauri 2.0 stability issues | Low | High | Fallback to Tauri 1.x si nécessaire |
| ChromaDB performance degradation | Low | Medium | Regular index optimization + monitoring |
| Cross-platform build complexities | High | Medium | CI/CD early + test sur toutes plateformes |

### 12.2 Risques de Planning
| Risque | Probabilité | Impact | Mitigation |
|--------|-------------|--------|------------|
| Underestimation AI complexity | High | High | Phase 2 (CV processing) buffer + 50% |
| Agent conversationnel quality issues | Medium | High | Early testing avec vrais utilisateurs |
| Performance SLA difficult to meet | Medium | High | Performance testing dès Phase 1 |
| Dependency conflicts (Python/Rust/Node) | Medium | Medium | Lock versions + regular updates |

### 12.3 Plan de Contingence
**Si retard > 2 semaines sur une Phase :**
1. Réévaluer scope : déplacer SHOULD HAVE à post-MVP
2. Augmenter focus : pause autres activités pour catch up
3. Simplifier : Version simplifiée de la feature problématique
4. Externaliser : Si compétence manquante, trouver expert ponctuel

---

*Planning créé le 27 janvier 2026 - Révision hebdomadaire recommandée*  
*Basé sur PRD v1.0, DESIGN v1.0, TECH_SPECS v1.0*  
*© Chat Emploi - Usage interne développement*

**Prochaines étapes :** 
1. Commiter ce planning dans le repo
2. Créer le fichier `PROGRESS_TRACKER.md` 
3. Démarrer Phase 0 : Fondations & Outillage