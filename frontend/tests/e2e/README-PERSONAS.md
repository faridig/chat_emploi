# Tests Utilisateur Réels - Personas PRD

## Module 12: Validation des scénarios personas

Ce module implémente les tests utilisateur réels automatisés pour valider les 3 personas du PRD:

### Personas Testées

1. **Julien** (28 ans) - Reconversion commercial → tech
   - Ancien commercial souhaitant devenir développeur web
   - CV avec compétences commerciales à transposer vers la tech
   - Recherche: postes junior avec formation/accompagnement

2. **Sophie** (45 ans) - Cadre senior avec 20 ans d'expérience
   - Expérience longue en gestion de projet
   - Recherche: postes de direction/management
   - Enjeu: mise en valeur de l'expérience sans paraître surqualifiée

3. **Léa** (22 ans) - Jeune diplômée en marketing
   - Peu d'expérience professionnelle
   - Recherche: premier emploi, programmes jeunes diplômés
   - Enjeu: construction d'un profil attractif malgré le manque d'expérience

## Structure des Tests

### Fichiers Principaux

- `personas.ts` - Définition des personas, données de test, métriques
- `persona-tests.spec.ts` - Tests Playwright pour chaque persona
- `mocks/` - CVs mockés pour les tests
  - `julien_reconversion_commercial_dev.txt`
  - `sophie_cadre_senior_gestion_projet.txt`
  - `lea_jeune_diplomee_marketing.txt`

### Scénarios Testés

Pour chaque persona, le test valide:

1. **Import CV** - Upload et prévisualisation
2. **Anonymisation** - Protection des données sensibles
3. **Conversation avec agent** - Dialogue contextuel adapté au persona
4. **Recherche d'offres** - Matching RAG avec filtres appropriés
5. **Validation matching** - Scores de pertinence attendus
6. **Génération lettre** - Personnalisation selon le persona
7. **Dashboard** - Suivi de la candidature

### Métriques Collectées

- **Temps total** par session
- **Nombre d'offres** trouvées
- **Score matching moyen**
- **Lettre générée** (oui/non)
- **Étapes complétées**
- **Erreurs rencontrées**

## Exécution des Tests

### Pré-requis

1. Backend Python en cours d'exécution (`http://localhost:8000`)
2. Frontend Next.js en cours d'exécution (`http://localhost:3000`)
3. Playwright installé (`npm run test:e2e:install`)

### Commandes Disponibles

```bash
# Tous les tests personas (script complet)
npm run test:personas

# Tests individuels
npm run test:personas:julien
npm run test:personas:sophie
npm run test:personas:lea

# Tous les tests E2E (incluant personas)
npm run test:e2e

# Mode UI pour debug
npm run test:e2e:ui

# Générer des tests avec codegen
npm run test:e2e:codegen
```

### Script d'exécution complet

```bash
./scripts/run-persona-tests.sh
```

Ce script:
1. Vérifie que backend et frontend sont accessibles
2. Exécute les tests pour chaque persona
3. Génère un rapport consolidé Markdown
4. Affiche un résumé des résultats

## Rapports Générés

### Rapport Markdown
`test-reports/persona-tests-report.md`
- Résumé global
- Détails par persona
- Métriques de performance
- Recommandations d'amélioration
- Validation des personas

### Rapport HTML Playwright
`playwright-report/index.html`
- Screenshots sur échec
- Traces détaillées
- Vidéos des sessions
- Logs d'exécution

## Critères de Succès

### Performance
- **Temps par session**: < 25 minutes (1500 secondes)
- **Temps de réponse agent**: < 3 secondes
- **Temps de génération lettre**: < 15 secondes

### Qualité
- **Score matching**: > 70% pour chaque persona
- **Pertinence offres**: Offres adaptées au profil
- **Personnalisation**: Lettres adaptées au ton souhaité

### Complétude
- **100% des étapes** complétées sans erreur
- **Lettre générée** pour chaque test réussi
- **Dashboard mis à jour** avec la candidature

## Personnalisation des Tests

### Ajouter une nouvelle persona

1. Ajouter la définition dans `personas.ts`:
```typescript
export const personas: Record<string, Persona> = {
  // ... personas existantes
  nouvelle: {
    id: 'nouvelle',
    name: 'Nom',
    description: 'Description',
    cvFile: 'fichier_cv.txt',
    // ... configuration
  }
};
```

2. Créer le fichier CV dans `mocks/`
3. Ajouter un test dans `persona-tests.spec.ts`

### Modifier les critères de validation

Les métriques attendues sont configurables dans chaque persona:
```typescript
metrics: {
  expectedSessionTime: 25, // minutes
  expectedMatchRate: 0.7,  // 0-1
  expectedLetterQuality: 0.8
}
```

## Intégration CI/CD

Les tests personas sont intégrés dans:
- `playwright.config.ts` - Projets séparés pour chaque persona
- Scripts npm pour exécution individuelle ou groupée
- Génération automatique de rapports

## Dépannage

### Problèmes courants

1. **Backend inaccessible**
   ```bash
   cd backend
   python -m src.api.main
   ```

2. **Frontend inaccessible**
   ```bash
   cd frontend
   npm run dev
   ```

3. **Playwright non installé**
   ```bash
   npm run test:e2e:install
   ```

4. **Tests trop lents**
   - Vérifier la connexion internet (API Gemini)
   - Augmenter les timeouts dans `testConfig`
   - Utiliser `slowMo` pour ralentir les actions

### Debug détaillé

```bash
# Mode debug avec timeouts étendus
npm run test:personas:julien -- --timeout=180000 --debug

# Avec traces détaillées
npm run test:personas:julien -- --trace=on

# Afficher le rapport HTML
npm run test:e2e:report
```

## Validation Business

Ces tests valident que:

✅ **L'application comprend** les différents profils utilisateurs
✅ **Le matching RAG** fonctionne pour tous les types de profils
✅ **La personnalisation** est adaptée à chaque situation
✅ **L'expérience utilisateur** est fluide et empathique
✅ **Les métriques qualité** sont dans les cibles définies

---

*Documentation mise à jour le 29 janvier 2026*
*Module 12: Tests Utilisateur Réels - MVP v1.0*
