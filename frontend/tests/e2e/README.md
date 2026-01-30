# Tests End-to-End (E2E) - Chat Emploi

## 📋 Vue d'ensemble

Ce dossier contient les tests E2E pour l'application Chat Emploi, conformément au **Module 10** du PLANNING.md.

## 🎯 Objectifs

Les tests E2E couvrent les **4 flux utilisateurs critiques** définis dans le PLANNING.md :

1. **Import CV → Analyse → Conversation**
2. **Recherche → Matching → Sélection offre**
3. **Génération lettre → Personnalisation → Export**
4. **Dashboard → Suivi → Mise à jour statut**

## 🛠️ Configuration

### Pré-requis

- Node.js 20+
- npm 10+
- Application Next.js en cours d'exécution (port 3000)

### Installation

```bash
# Depuis le dossier frontend/
./scripts/setup-e2e-tests.sh
```

Ou manuellement :

```bash
npm install
npx playwright install --with-deps chromium
```

## 🧪 Exécution des tests

### Commandes disponibles

```bash
# Exécuter tous les tests E2E
npm run test:e2e

# Exécuter avec l'interface UI
npm run test:e2e:ui

# Exécuter en mode debug
npm run test:e2e:debug

# Générer des tests avec codegen
npm run test:e2e:codegen

# Afficher le rapport HTML
npm run test:e2e:report
```

### Exécution en local

1. Démarrer l'application de développement :
```bash
npm run dev
```

2. Dans un autre terminal, exécuter les tests :
```bash
npm run test:e2e
```

## 📁 Structure des fichiers

```
tests/e2e/
├── basic-navigation.spec.ts      # Tests de navigation de base
├── critical-flows.spec.ts        # 4 flux utilisateurs critiques
├── mocks/                        # Données mockées pour les tests
│   └── sample-cv.pdf            # CV mock pour les tests d'upload
└── README.md                    # Cette documentation
```

## 🔍 Stratégie de test

### Sélecteurs recommandés

Utiliser les `data-testid` pour une sélection robuste :

```typescript
// ✅ Bon
await page.locator('[data-testid="offer-card"]').first().click();

// ❌ À éviter (fragile)
await page.locator('div.card:first-child').click();
```

### Data-testid disponibles

| Composant | data-testid | Description |
|-----------|-------------|-------------|
| JobOfferCard | `offer-card` | Carte d'offre d'emploi |
| DndZone input | `file-input` | Input pour upload de CV |
| LetterPreview | `letter-preview` | Prévisualisation de lettre |
| LetterControls | `customization-panel` | Panneau de personnalisation |
| ChatPanel | `chat-panel` | Panneau de conversation |
| Tone slider | `tone-slider` | Slider pour le ton de la lettre |
| Highlight checklist | `highlight-checklist` | Checklist des points à mettre en avant |

### Bonnes pratiques

1. **Isolation** : Chaque test doit être indépendant
2. **Attentes explicites** : Utiliser `await expect()` pour toutes les assertions
3. **Timeout appropriés** : Adapter les timeouts selon les opérations
4. **Données mockées** : Utiliser les fichiers dans `mocks/` pour les tests d'upload

## 🚀 Intégration CI/CD

Les tests E2E sont intégrés dans le pipeline CI/CD via GitHub Actions. Voir `infrastructure/github/workflows/build-and-test.yml`.

### Configuration CI

- **OS supportés** : Ubuntu, Windows, macOS
- **Navigateurs** : Chromium (par défaut)
- **Mode headless** : Activé en CI
- **Rapports** : HTML et JSON générés automatiquement

## 🐛 Dépannage

### Problèmes courants

1. **Tests échouent avec "Target closed"**
   - Vérifier que l'application est en cours d'exécution sur le port 3000
   - Augmenter les timeouts si nécessaire

2. **Impossible de trouver les éléments**
   - Vérifier que les `data-testid` sont correctement définis dans les composants
   - Utiliser `page.pause()` pour déboguer

3. **Problèmes d'upload de fichiers**
   - Vérifier que le fichier mock existe dans `tests/e2e/mocks/`
   - S'assurer que le chemin est correct

### Commandes de débogage

```bash
# Générer un trace pour les tests échoués
npx playwright test --trace on

# Exécuter un test spécifique
npx playwright test basic-navigation.spec.ts

# Ouvrir le rapport HTML
npx playwright show-report
```

## 📈 Métriques de qualité

- **Couverture des flux** : 4/4 flux critiques testés
- **Stabilité** : Taux de succès > 95%
- **Performance** : Temps d'exécution total < 2 minutes
- **Maintenabilité** : Utilisation de sélecteurs robustes (data-testid)

## 🔄 Maintenance

### Ajouter un nouveau test

1. Créer un fichier `.spec.ts` dans `tests/e2e/`
2. Importer `{ test, expect }` de `@playwright/test`
3. Utiliser les `data-testid` existants ou en ajouter de nouveaux
4. Exécuter les tests localement pour vérifier

### Mettre à jour les sélecteurs

Si la structure HTML change :
1. Mettre à jour les `data-testid` dans les composants React
2. Mettre à jour les tests correspondants
3. Exécuter les tests pour vérifier

## 📚 Références

- [Documentation Playwright](https://playwright.dev/docs/intro)
- [PLANNING.md - Module 10](../PLANNING.md)
- [Best Practices Playwright](https://playwright.dev/docs/best-practices)

---

*Dernière mise à jour : 29 janvier 2026*
*Conforme au PLANNING.md - Module 10 : Tests E2E Critiques*
