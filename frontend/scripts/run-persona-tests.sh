#!/bin/bash

# Script pour exécuter les tests utilisateur réels (personas)
# Module 12: Tests Utilisateur Réels

set -e

echo "========================================="
echo "Tests Utilisateur Réels - Personas PRD"
echo "Module 12: Validation scénarios personas"
echo "========================================="

# Vérifier que le backend Python est en cours d'exécution
echo "🔍 Vérification du backend Python..."
if ! curl -s http://localhost:8000/health > /dev/null; then
    echo "❌ Le backend Python n'est pas accessible sur http://localhost:8000"
    echo "   Lancez-le avec: cd backend && python -m src.api.main"
    exit 1
fi
echo "✅ Backend Python accessible"

# Vérifier que le frontend est en cours d'exécution
echo "🔍 Vérification du frontend..."
if ! curl -s http://localhost:3000 > /dev/null; then
    echo "❌ Le frontend n'est pas accessible sur http://localhost:3000"
    echo "   Lancez-le avec: cd frontend && npm run dev"
    exit 1
fi
echo "✅ Frontend accessible"

# Créer le dossier pour les rapports
mkdir -p test-reports/personas

echo ""
echo "🚀 Lancement des tests personas..."

# Exécuter les tests pour chaque persona
echo ""
echo "🧪 Test 1/3: Julien (reconversion commercial → tech)"
npx playwright test --project=persona-julien --reporter=html,list --timeout=120000

echo ""
echo "🧪 Test 2/3: Sophie (cadre senior avec expérience longue)"
npx playwright test --project=persona-sophie --reporter=html,list --timeout=120000

echo ""
echo "🧪 Test 3/3: Léa (jeune diplômée avec peu d'expérience)"
npx playwright test --project=persona-lea --reporter=html,list --timeout=120000

echo ""
echo "📊 Génération du rapport consolidé..."

# Vérifier si les rapports existent et les consolider
if [ -f "test-reports/persona-tests-report.md" ]; then
    echo "✅ Rapport généré: test-reports/persona-tests-report.md"

    # Afficher un résumé
    echo ""
    echo "📋 Résumé des tests:"
    echo "-------------------"
    grep -A5 "## Résumé" test-reports/persona-tests-report.md | tail -n 5

    echo ""
    echo "📈 Métriques de performance:"
    echo "---------------------------"
    grep -A10 "## Métriques Globales" test-reports/persona-tests-report.md | grep -E "(Temps|Score|Lettres)" | head -n 6

    echo ""
    echo "✅ Tests personas complétés!"
    echo "   Rapport détaillé: test-reports/persona-tests-report.md"
    echo "   Rapport HTML: playwright-report/index.html"
else
    echo "⚠️  Aucun rapport généré. Vérifiez l'exécution des tests."
fi

echo ""
echo "========================================="
echo "Tests Utilisateur Réels - TERMINÉ"
echo "========================================="
