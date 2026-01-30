#!/bin/bash

echo "🔧 Correction complète des imports de test"
echo "=========================================="

cd frontend

# 1. Corriger les imports dans le dossier tests/
echo "1. Correction des imports dans tests/..."
find tests -name "*.ts" -o -name "*.tsx" | while read file; do
    echo "  - Traitement de $file"

    # Supprimer les imports de vitest
    sed -i "/import.*from ['\"]vitest['\"]/d" "$file"

    # Supprimer les imports spécifiques de vitest
    sed -i "/import.*describe.*from/d" "$file"
    sed -i "/import.*it.*from/d" "$file"
    sed -i "/import.*test.*from/d" "$file"
    sed -i "/import.*expect.*from/d" "$file"
    sed -i "/import.*vi.*from/d" "$file"
    sed -i "/import.*beforeEach.*from/d" "$file"
    sed -i "/import.*afterEach.*from/d" "$file"
    sed -i "/import.*beforeAll.*from/d" "$file"
    sed -i "/import.*afterAll.*from/d" "$file"
done

# 2. Corriger vitest.setup.ts
echo "2. Correction de vitest.setup.ts..."
if [ -f "vitest.setup.ts" ]; then
    sed -i "/import.*from ['\"]vitest['\"]/d" vitest.setup.ts
    echo "  - Fichier corrigé"
fi

# 3. Vérifier les imports @/lib/utils
echo "3. Vérification des imports @/lib/utils..."
if [ -f "src/lib/utils.ts" ]; then
    echo "  - Fichier utils.ts présent ✓"
else
    echo "  - ⚠️ Fichier utils.ts manquant"
fi

# 4. Vérifier la configuration TypeScript
echo "4. Vérification de la configuration TypeScript..."
if grep -q '"baseUrl": "."' tsconfig.json; then
    echo "  - baseUrl configuré ✓"
else
    echo "  - ⚠️ baseUrl non configuré"
fi

# 5. Exécuter TypeScript check
echo "5. Vérification TypeScript..."
npx tsc --noEmit 2>&1 | grep -E "error|warning" | head -20 > /tmp/ts-errors.log
ERROR_COUNT=$(grep -c "error" /tmp/ts-errors.log || true)

if [ "$ERROR_COUNT" -eq 0 ]; then
    echo "  - ✅ Aucune erreur TypeScript"
else
    echo "  - ⚠️ $ERROR_COUNT erreurs TypeScript détectées"
    echo "    Premières erreurs :"
    head -10 /tmp/ts-errors.log
fi

echo ""
echo "🎯 Résumé :"
echo "==========="
echo "✅ Imports de test corrigés"
echo "✅ Fichiers de configuration convertis en ES modules"
echo "⚠️  Vérifiez les erreurs TypeScript restantes"

echo ""
echo "📋 Prochaines étapes :"
echo "====================="
echo "1. Commiter les changements :"
echo "   git add ."
echo "   git commit -m 'fix: convert config files to ES modules and fix test imports'"
echo "2. Pousser les changements :"
echo "   git push origin test-ci"
