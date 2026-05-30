# Chat Emploi

Agent IA de carrière personnalisé — une application desktop qui transforme la recherche d'emploi en expérience conversationnelle. Chaque utilisateur dispose d'un assistant disponible 24h/24 pour trouver des offres, adapter son CV et se préparer aux entretiens.

> **Statut : en développement** — architecture et spécifications complètes, implémentation en cours.

## Vision

Les algorithmes actuels de recherche d'emploi sont froids et impersonnels. Chat Emploi agit comme un **agent de carrière personnel** qui :

1. Comprend le profil du candidat via conversation naturelle
2. Recherche activement les offres pertinentes (API France Travail + web)
3. Adapte le CV à chaque annonce
4. Rédige les lettres de motivation
5. Simule des entretiens et fournit des briefings personnalisés

## Architecture

```
┌─────────────────────────────────────┐
│   Application Desktop (Tauri 2.0)   │
│   Next.js 15 · TypeScript · shadcn  │
└──────────────┬──────────────────────┘
               │ IPC (msgpack-rpc)
┌──────────────▼──────────────────────┐
│        Backend Python (FastAPI)      │
│                                      │
│  ┌─────────────┐  ┌──────────────┐  │
│  │  LangGraph  │  │   CrewAI     │  │
│  │  (workflow) │  │  (agents)    │  │
│  └──────┬──────┘  └──────┬───────┘  │
│         └────────┬────────┘         │
│              LlamaIndex              │
│           (RAG sur CV/offres)        │
│                                      │
│  Gemini Pro · spaCy NER · SQLite    │
│  Redis (cache) · Chroma DB          │
└──────────────────────────────────────┘
```

## Stack

| Couche | Technologie |
|--------|-------------|
| Desktop | Tauri 2.0 + Next.js 15 |
| UI | TypeScript · shadcn/ui · Tailwind 4 |
| Orchestration IA | LangGraph + CrewAI |
| RAG | LlamaIndex + Chroma DB |
| LLM | Gemini Pro 1.5 |
| NER / Anonymisation | spaCy `fr_core_news_lg` |
| Embeddings | Gemini text-embedding-004 |
| API Offres d'emploi | France Travail (Pôle Emploi) |
| Cache | Redis Stack |
| Stockage | SQLite + système de fichiers local |
| Monitoring | Prometheus + Grafana |
| CI/CD | GitHub Actions |

## Fonctionnalités prévues

- [ ] Onboarding conversationnel (profil, objectifs, contraintes)
- [ ] Recherche d'offres multi-sources (France Travail + web)
- [ ] Analyse et adaptation du CV par offre
- [ ] Génération de lettres de motivation personnalisées
- [ ] Simulation d'entretien avec feedback
- [ ] Dashboard Kanban de suivi des candidatures
- [ ] Anonymisation automatique des données sensibles (NER)

## Docs

- [`PRD.md`](PRD.md) — Product Requirements Document
- [`TECH_SPECS.md`](TECH_SPECS.md) — Spécifications techniques complètes
- [`DESIGN.md`](DESIGN.md) — Design et UX
