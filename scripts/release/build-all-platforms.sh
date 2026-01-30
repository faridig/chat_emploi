#!/bin/bash
# scripts/release/build-all-platforms.sh

# Ce script lance le processus de build Tauri pour toutes les plateformes cibles.
# Il est conçu pour être utilisé en local afin de vérifier que les builds fonctionnent
# avant de pousser vers la CI/CD.

# Assurez-vous que les dépendances sont installées
echo "--- Ensuring frontend dependencies are installed ---"
npm install --prefix frontend

# Lancez le build Tauri
echo "--- Starting Tauri build for all configured platforms (DMG, AppImage, MSI) ---"
npm run tauri build -- --bundles dmg appimage msi --prefix frontend

echo "--- Build process finished ---"
echo "Check the 'frontend/src-tauri/target/release/bundle/' directory for artifacts."
