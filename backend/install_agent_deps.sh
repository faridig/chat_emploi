#!/bin/bash
# Script d'installation des dépendances pour les agents LangGraph

echo "🔧 Installation des dépendances pour les agents LangGraph..."

# Activer l'environnement virtuel si présent
if [ -d ".venv" ]; then
    echo "📦 Activation de l'environnement virtuel..."
    source .venv/bin/activate
fi

# Installer les dépendances manquantes
echo "📥 Installation de langchain-google-genai..."
pip install langchain-google-genai

echo "📥 Installation de langgraph..."
pip install langgraph

echo "📥 Installation de crewai..."
pip install crewai

echo "📥 Installation de llama-index..."
pip install llama-index

echo "📥 Installation de chromadb..."
pip install chromadb

echo "✅ Toutes les dépendances sont installées !"
echo ""
echo "📋 Liste des packages installés :"
pip list | grep -E "(langchain|langgraph|crewai|llama|chroma)"

# Vérifier les imports
echo ""
echo "🔍 Vérification des imports..."
python -c "
try:
    import langchain_google_genai
    print('✅ langchain-google-genai importé avec succès')
except ImportError as e:
    print(f'❌ Erreur: {e}')

try:
    import langgraph
    print('✅ langgraph importé avec succès')
except ImportError as e:
    print(f'❌ Erreur: {e}')

try:
    import crewai
    print('✅ crewai importé avec succès')
except ImportError as e:
    print(f'❌ Erreur: {e}')
"
