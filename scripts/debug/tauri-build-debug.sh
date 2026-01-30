#!/bin/bash
# Script de debug pour le build Tauri

set -e

echo "=== DEBUG TAURI BUILD ==="
echo "Date: $(date)"
echo ""

# Vérifier la structure du projet
echo "1. Structure du projet:"
ls -la frontend/
echo ""

# Vérifier package.json
echo "2. Package.json:"
cat frontend/package.json | grep -A5 -B5 "tauri"
echo ""

# Vérifier les dépendances
echo "3. Dépendances installées:"
cd frontend && npm list @tauri-apps/cli @tauri-apps/api 2>/dev/null || echo "Dépendances non trouvées"
cd ..
echo ""

# Vérifier la configuration Tauri
echo "4. Configuration Tauri:"
ls -la frontend/src-tauri/
echo ""

# Vérifier tauri.conf.json
echo "5. tauri.conf.json:"
cat frontend/src-tauri/tauri.conf.json | head -50
echo ""

# Tenter un build local
echo "6. Tentative de build local:"
cd frontend && npm run tauri build -- --verbose 2>&1 | tail -50 || echo "Build échoué"
cd ..
echo ""

echo "=== FIN DU DEBUG ==="
