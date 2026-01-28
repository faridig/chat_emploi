#!/bin/bash
# Script de setup pour Chat Emploi
# Usage: ./scripts/dev/setup.sh

set -e

echo "🔧 Setup de Chat Emploi"
echo "========================"

# Vérification des prérequis
echo "📋 Vérification des prérequis..."

check_command() {
    if ! command -v $1 &> /dev/null; then
        echo "❌ $1 n'est pas installé"
        return 1
    fi
    echo "✅ $1"
}

check_command node
check_command npm
check_command python3
check_command cargo || echo "⚠️  Rust/Cargo n'est pas installé, Tauri tentera de l'installer"

# Setup frontend
echo ""
echo "🖥️  Setup frontend..."
cd frontend
npm install
cd ..

# Setup backend
echo ""
echo "🐍 Setup backend..."
cd backend
if [ ! -d ".venv" ]; then
    python3 -m venv .venv
fi
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements-dev.txt

# Installer spaCy model français
python -m spacy download fr_core_news_lg

cd ..

# Setup pre-commit hooks
echo ""
echo "🔗 Setup pre-commit hooks..."
cd backend
pre-commit install
cd ..

echo ""
echo "✅ Setup terminé !"
echo ""
echo "Pour démarrer l'application en développement :"
echo "  ./scripts/dev/start.sh"