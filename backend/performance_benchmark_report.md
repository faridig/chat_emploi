# Rapport de Performance - Chat Emploi

**Date**: 2026-01-30T11:40:27.353627

## 📊 Résumé Exécutif

- **Endpoints testés**: 5
- **Temps de réponse moyen**: 2.00 ms
- **Endpoint le plus rapide**: `/api/test/jsonrpc`
- **Endpoint le plus lent**: `/metrics`
- **Santé du système**: 100.0%
- **Débit concurrent**: 723.4 req/s

## 📈 Détails par Endpoint

| Endpoint | Méthode | Moyenne (ms) | Min (ms) | Max (ms) | Std Dev |
|----------|---------|--------------|----------|----------|---------|
| `/health` | GET | 1.53 | 1.35 | 1.86 | 0.14 |
| `/api/status` | GET | 1.52 | 1.41 | 1.71 | 0.10 |
| `/metrics` | GET | 3.93 | 2.87 | 5.39 | 0.89 |
| `/api/test/jsonrpc` | POST | 1.66 | 1.22 | 2.13 | 0.30 |
| `/api/test/jsonrpc` | POST | 1.35 | 1.00 | 2.31 | 0.39 |

## 🩺 Santé du Système

- **Endpoints testés**: 5
- **Endpoints sains**: 5
- **Taux de santé**: 100.0%

### Détails:
- ✅ `/health` (GET): 8.19 ms - HTTP 200
- ✅ `/api/status` (GET): 1.66 ms - HTTP 200
- ✅ `/metrics` (GET): 3.30 ms - HTTP 200
- ✅ `/docs` (GET): 1.27 ms - HTTP 200
- ✅ `/openapi.json` (GET): 4.54 ms - HTTP 200

## ⚡ Performance Concurrente

- **Requêtes concurrentes**: 10
- **Temps total**: 13.82 ms
- **Débit**: 723.4 req/s
- **Taux de succès**: 100.0%

## 🎯 Recommandations

1. ✅ **Temps de réponse** - Excellentes performances (< 100 ms)
2. ✅ **Santé du système** - Excellente disponibilité (≥ 95%)
3. ✅ **Débit concurrent** - Excellente capacité (≥ 100 req/s)

---
*Rapport généré automatiquement par le script de benchmark*
