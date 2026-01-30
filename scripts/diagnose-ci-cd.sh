#!/bin/bash

echo "🔍 Diagnostic CI/CD - Chat Emploi"
echo "=================================="

# Couleurs
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Fonction de vérification
check_status() {
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓${NC} $1"
    else
        echo -e "${RED}✗${NC} $1"
    fi
}

echo ""
echo "📦 Vérification des dépendances..."
echo "----------------------------------"

# Backend Python
echo -n "Vérification Python backend... "
cd backend && source .venv/bin/activate 2>/dev/null && python -c "import fastapi, pydantic, sqlalchemy" >/dev/null 2>&1
check_status "Dépendances Python backend"

# Frontend Node.js
echo -n "Vérification Node.js... "
cd ../frontend && node --version >/dev/null 2>&1
check_status "Node.js installé"

echo -n "Vérification npm... "
npm --version >/dev/null 2>&1
check_status "npm installé"

# Tauri
echo -n "Vérification Tauri CLI... "
npx tauri --version >/dev/null 2>&1
check_status "Tauri CLI"

echo ""
echo "🔧 Vérification des configurations..."
echo "-------------------------------------"

# ESLint v9
echo -n "Vérification ESLint configuration... "
if [ -f ".eslintrc.json" ] && [ ! -f "eslint.config.js" ]; then
    echo -e "${YELLOW}⚠${NC} Configuration ESLint v8 (obsolète pour v9)"
else
    echo -e "${GREEN}✓${NC} Configuration ESLint compatible"
fi

# TypeScript
echo -n "Vérification TypeScript config... "
if [ -f "tsconfig.json" ]; then
    echo -e "${GREEN}✓${NC} tsconfig.json présent"
else
    echo -e "${RED}✗${NC} tsconfig.json manquant"
fi

# Next.js
echo -n "Vérification Next.js config... "
if [ -f "next.config.js" ]; then
    echo -e "${GREEN}✓${NC} next.config.js présent"
else
    echo -e "${RED}✗${NC} next.config.js manquant"
fi

echo ""
echo "🧪 Tests des workflows CI/CD..."
echo "-------------------------------"

# Test backend
echo "Test backend Python..."
cd ../backend
source .venv/bin/activate
echo -n "  - Linters (ruff)... "
ruff check src --output-format=concise >/dev/null 2>&1
check_status "Ruff lint"

echo -n "  - Formatage (black)... "
black --check src >/dev/null 2>&1
check_status "Black format"

echo -n "  - Tests unitaires... "
pytest tests/unit/ -q --tb=no >/dev/null 2>&1
check_status "Tests unitaires"

# Test frontend
echo "Test frontend..."
cd ../frontend
echo -n "  - TypeScript check... "
npx tsc --noEmit >/dev/null 2>&1
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓${NC} TypeScript OK"
else
    echo -e "${RED}✗${NC} Erreurs TypeScript (exécutez: npx tsc --noEmit pour détails)"
fi

echo -n "  - Build Next.js... "
npm run build >/dev/null 2>&1
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓${NC} Build réussi"
else
    echo -e "${RED}✗${NC} Échec du build (exécutez: npm run build pour détails)"
fi

# Test Tauri
echo "Test Tauri..."
echo -n "  - Build Tauri (dev)... "
npm run tauri build >/dev/null 2>&1
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓${NC} Build Tauri réussi"
else
    echo -e "${RED}✗${NC} Échec build Tauri (peut nécessiter des dépendances système)"
fi

echo ""
echo "📊 Résumé des problèmes CI/CD..."
echo "--------------------------------"

echo "1. ${YELLOW}ESLint v9${NC}: Migration nécessaire de .eslintrc.json vers eslint.config.js"
echo "2. ${YELLOW}TypeScript${NC}: Types Vitest manquants (@types/vitest ou vitest/globals)"
echo "3. ${YELLOW}Dépendances${NC}: Certaines dépendances marquées comme 'extraneous'"
echo "4. ${YELLOW}Next.js lint${NC}: Commande 'next lint' ne fonctionne pas avec ESLint v9"

echo ""
echo "🔧 Solutions recommandées :"
echo "1. Migrer ESLint vers v9: créer eslint.config.js"
echo "2. Ajouter types Vitest: npm install -D @types/vitest"
echo "3. Nettoyer dépendances: npm prune"
echo "4. Mettre à jour package.json scripts pour utiliser ESLint directement"

echo ""
echo "Pour exécuter les corrections automatiquement :"
echo "  ./scripts/fix-ci-cd-issues.sh"

cd ..
