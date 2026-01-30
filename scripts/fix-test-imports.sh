#!/bin/bash

echo "🔧 Correction des imports dans les fichiers de test"
echo "=================================================="

cd frontend

# Liste des fichiers de test
TEST_FILES=$(find src -name "*.test.tsx" -o -name "*.test.ts")

for file in $TEST_FILES; do
    echo "Traitement de $file"

    # Vérifier si le fichier importe depuis vitest
    if grep -q "from 'vitest'" "$file" || grep -q 'from "vitest"' "$file"; then
        echo "  - Suppression des imports vitest..."

        # Supprimer les imports de vitest
        sed -i "/import.*from ['\"]vitest['\"]/d" "$file"

        # Ajouter l'import de Mock si nécessaire
        if grep -q "as Mock" "$file" && ! grep -q "import type { Mock }" "$file"; then
            echo "  - Ajout de l'import Mock..."
            sed -i '1s/^/import type { Mock } from "vitest";\n/' "$file"
        fi
    fi

    # Vérifier si le fichier utilise vi sans import
    if grep -q "vi\." "$file" && ! grep -q "import.*vi" "$file"; then
        echo "  - Utilise vi (global) ✓"
    fi
done

echo ""
echo "✅ Correction terminée"
echo ""
echo "Vérification TypeScript..."
npx tsc --noEmit 2>&1 | grep -E "(error|warning)" | head -20
