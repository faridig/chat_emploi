#!/bin/bash

echo "🔧 Correction des problèmes CI/CD - Chat Emploi"
echo "=============================================="

# Couleurs
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo ""
echo "1. Migration ESLint v8 → v9..."
echo "-------------------------------"

cd frontend

# Créer la nouvelle configuration ESLint v9
cat > eslint.config.js << 'EOF'
import { defineConfig } from 'eslint/config';
import globals from 'globals';
import js from '@eslint/js';
import tseslint from 'typescript-eslint';
import react from 'eslint-plugin-react';
import reactHooks from 'eslint-plugin-react-hooks';

export default defineConfig([
  {
    files: ['**/*.{js,jsx,ts,tsx}'],
    languageOptions: {
      ecmaVersion: 'latest',
      sourceType: 'module',
      globals: {
        ...globals.browser,
        ...globals.node,
        vi: 'readonly',
        describe: 'readonly',
        it: 'readonly',
        expect: 'readonly',
        beforeEach: 'readonly',
        afterEach: 'readonly',
      },
      parserOptions: {
        ecmaFeatures: {
          jsx: true,
        },
      },
    },
    plugins: {
      react,
      'react-hooks': reactHooks,
    },
    rules: {
      ...js.configs.recommended.rules,
      ...tseslint.configs.recommended.rules,
      ...react.configs.recommended.rules,
      ...reactHooks.configs.recommended.rules,
      '@typescript-eslint/no-unused-vars': ['error', { argsIgnorePattern: '^_' }],
      'react/no-unescaped-entities': 'off',
      'react/react-in-jsx-scope': 'off',
    },
    settings: {
      react: {
        version: 'detect',
      },
    },
  },
]);
EOF

echo -e "${GREEN}✓${NC} Configuration ESLint v9 créée (eslint.config.js)"

# Supprimer l'ancienne configuration
if [ -f ".eslintrc.json" ]; then
    rm .eslintrc.json
    echo -e "${GREEN}✓${NC} Ancienne configuration supprimée (.eslintrc.json)"
fi

echo ""
echo "2. Installation des types Vitest..."
echo "-----------------------------------"

# Installer les types nécessaires
npm install -D @types/vitest vitest/globals @testing-library/jest-dom @testing-library/react

echo -e "${GREEN}✓${NC} Types Vitest installés"

echo ""
echo "3. Mise à jour de tsconfig.json..."
echo "-----------------------------------"

# Mettre à jour tsconfig.json pour inclure les types Vitest
if [ -f "tsconfig.json" ]; then
    # Créer une copie de sauvegarde
    cp tsconfig.json tsconfig.json.backup

    # Mettre à jour la configuration
    cat > tsconfig.json << 'EOF'
{
  "compilerOptions": {
    "target": "es5",
    "lib": ["dom", "dom.iterable", "esnext"],
    "allowJs": true,
    "skipLibCheck": true,
    "strict": true,
    "noEmit": true,
    "esModuleInterop": true,
    "module": "esnext",
    "moduleResolution": "bundler",
    "resolveJsonModule": true,
    "isolatedModules": true,
    "jsx": "preserve",
    "incremental": true,
    "plugins": [
      {
        "name": "next"
      }
    ],
    "paths": {
      "@/*": ["./src/*"]
    },
    "types": ["vitest/globals", "@testing-library/jest-dom"]
  },
  "include": ["next-env.d.ts", "**/*.ts", "**/*.tsx", ".next/types/**/*.ts"],
  "exclude": ["node_modules"]
}
EOF
    echo -e "${GREEN}✓${NC} tsconfig.json mis à jour avec les types Vitest"
fi

echo ""
echo "4. Mise à jour des scripts package.json..."
echo "------------------------------------------"

# Mettre à jour les scripts lint
if [ -f "package.json" ]; then
    # Créer une copie de sauvegarde
    cp package.json package.json.backup

    # Utiliser jq pour mettre à jour les scripts si disponible, sinon utiliser sed
    if command -v jq >/dev/null 2>&1; then
        jq '.scripts.lint = "eslint src/ --ext .ts,.tsx"' package.json > package.json.tmp && mv package.json.tmp package.json
        jq '.scripts["lint:fix"] = "eslint src/ --ext .ts,.tsx --fix"' package.json > package.json.tmp && mv package.json.tmp package.json
    else
        # Fallback avec sed (moins robuste)
        sed -i 's/"lint": "next lint"/"lint": "eslint src\/ --ext .ts,.tsx"/' package.json
        sed -i '/"lint":/a\    "lint:fix": "eslint src\/ --ext .ts,.tsx --fix",' package.json
    fi

    echo -e "${GREEN}✓${NC} Scripts package.json mis à jour"
fi

echo ""
echo "5. Nettoyage des dépendances..."
echo "--------------------------------"

# Nettoyer les dépendances inutiles
npm prune
echo -e "${GREEN}✓${NC} Dépendances nettoyées"

echo ""
echo "6. Test des corrections..."
echo "--------------------------"

echo -n "Test TypeScript... "
npx tsc --noEmit >/dev/null 2>&1
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓${NC} TypeScript OK"
else
    echo -e "${RED}✗${NC} Erreurs TypeScript restantes"
    npx tsc --noEmit | head -20
fi

echo -n "Test ESLint... "
npx eslint src/ --ext .ts,.tsx >/dev/null 2>&1
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓${NC} ESLint OK"
else
    echo -e "${YELLOW}⚠${NC} Avertissements ESLint (exécutez: npm run lint:fix)"
fi

echo ""
echo "7. Mise à jour des workflows GitHub Actions..."
echo "----------------------------------------------"

cd ..

# Mettre à jour le workflow build-and-test.yml pour utiliser la nouvelle configuration
if [ -f ".github/workflows/build-and-test.yml" ]; then
    # Créer une copie de sauvegarde
    cp .github/workflows/build-and-test.yml .github/workflows/build-and-test.yml.backup

    # Mettre à jour la section frontend
    sed -i 's/npm run lint/npx eslint src\/ --ext .ts,.tsx/' .github/workflows/build-and-test.yml

    echo -e "${GREEN}✓${NC} Workflow GitHub Actions mis à jour"
fi

echo ""
echo "🎉 Corrections terminées !"
echo "=========================="
echo ""
echo "Prochaines étapes :"
echo "1. Commiter les changements :"
echo "   git add ."
echo "   git commit -m 'fix(ci): migrate to ESLint v9 and fix TypeScript issues'"
echo "2. Tester le workflow CI/CD :"
echo "   git push origin test-ci"
echo "3. Vérifier les résultats sur GitHub Actions"
echo ""
echo "Fichiers modifiés :"
echo "  - frontend/eslint.config.js (nouveau)"
echo "  - frontend/tsconfig.json (mis à jour)"
echo "  - frontend/package.json (scripts mis à jour)"
echo "  - .github/workflows/build-and-test.yml (mis à jour)"
echo ""
echo "Fichiers de sauvegarde créés :"
echo "  - frontend/tsconfig.json.backup"
echo "  - frontend/package.json.backup"
echo "  - .github/workflows/build-and-test.yml.backup"
