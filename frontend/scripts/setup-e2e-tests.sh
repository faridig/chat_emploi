#!/bin/bash

# Script de setup pour les tests E2E Playwright
# Conforme au PLANNING.md - Module 10 : Tests E2E Critiques

set -e

echo "🔧 Configuration des tests E2E Playwright pour Chat Emploi"
echo "=========================================================="

# Vérifier que nous sommes dans le bon répertoire
if [ ! -f "package.json" ]; then
    echo "❌ Erreur: Ce script doit être exécuté depuis le dossier frontend/"
    exit 1
fi

echo "📦 Installation des dépendances Playwright..."
npm install

echo "🖥️  Installation des navigateurs Playwright..."
npx playwright install --with-deps chromium

echo "🔍 Vérification de l'installation..."
npx playwright --version

echo "✅ Configuration terminée !"
echo ""
echo "Commandes disponibles :"
echo "  npm run test:e2e           # Exécuter tous les tests E2E"
echo "  npm run test:e2e:ui        # Exécuter avec l'interface UI"
echo "  npm run test:e2e:debug     # Exécuter en mode debug"
echo "  npm run test:e2e:codegen   # Générer des tests avec codegen"
echo "  npm run test:e2e:report    # Afficher le rapport HTML"

echo ""
echo "📝 Pour exécuter les tests :"
echo "1. Démarrer l'application en développement : npm run dev"
echo "2. Dans un autre terminal : npm run test:e2e"
