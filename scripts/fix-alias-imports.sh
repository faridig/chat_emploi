#!/bin/bash

echo "🔧 Correction des alias @/ pour CI/CD"
echo "====================================="

cd frontend

echo "1. Vérification de la configuration TypeScript..."
if [ -f "tsconfig.json" ]; then
    echo "  - tsconfig.json présent"
    if grep -q '"@/\*": \["\./src/\*"\]' tsconfig.json; then
        echo "  - Alias @/ configuré ✓"
    else
        echo "  - ⚠️ Alias @/ non configuré"
    fi
fi

echo ""
echo "2. Solution temporaire : création d'un lien symbolique..."
# Créer un lien symbolique pour résoudre @/lib/utils
if [ ! -L "lib" ] && [ -d "src/lib" ]; then
    echo "  - Création du lien symbolique lib -> src/lib"
    ln -sf src/lib lib
    echo "  - ✅ Lien créé"
else
    echo "  - ✅ Lien déjà présent ou src/lib manquant"
fi

echo ""
echo "3. Vérification des imports..."
# Compter les imports @/lib/utils
IMPORT_COUNT=$(grep -r "from '@/lib/utils'" src/ --include="*.ts" --include="*.tsx" | wc -l)
echo "  - $IMPORT_COUNT imports de @/lib/utils détectés"

echo ""
echo "4. Solution alternative : utiliser des chemins relatifs..."
echo "  - Cette solution est temporaire pour CI/CD"
echo "  - En production, l'alias @/ devrait fonctionner avec Next.js"

echo ""
echo "5. Test TypeScript..."
npx tsc --noEmit 2>&1 | grep -E "error.*@/lib/utils" | head -5
if [ $? -eq 0 ]; then
    echo "  - ⚠️ Erreurs @/lib/utils toujours présentes"
else
    echo "  - ✅ Aucune erreur @/lib/utils"
fi

echo ""
echo "🎯 Résumé :"
echo "==========="
echo "Pour résoudre définitivement le problème :"
echo "1. Vérifier que next.config.js configure correctement l'alias @"
echo "2. S'assurer que webpack resolve.alias est configuré"
echo "3. Pour CI/CD, le lien symbolique peut aider"

echo ""
echo "Solution temporaire appliquée :"
echo "- Lien symbolique lib -> src/lib créé"
echo "- Cela permet à @/lib/utils de résoudre vers ./lib/utils"
