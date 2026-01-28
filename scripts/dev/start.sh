#!/bin/bash
# Script de démarrage pour Chat Emploi
# Usage: ./scripts/dev/start.sh

set -e

echo "🚀 Démarrage de Chat Emploi"
echo "============================"

# Démarrer le backend Python
echo "🐍 Démarrage du backend..."
cd backend
source .venv/bin/activate

# Lancer le backend en arrière-plan
uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

cd ..

# Démarrer le frontend
echo "🖥️  Démarrage du frontend..."
cd frontend

# Démarrer Next.js en arrière-plan
npm run dev &
FRONTEND_PID=$!

# Attendre un peu pour que les serveurs démarrent
sleep 3

echo ""
echo "✅ Services démarrés !"
echo ""
echo "📊 Accès aux services :"
echo "  Frontend (Next.js): http://localhost:3000"
echo "  Backend (FastAPI):  http://localhost:8000"
echo "  API Docs:           http://localhost:8000/docs"
echo "  Métriques:          http://localhost:8000/metrics"
echo "  Test logs:          http://localhost:8000/api/test/logs"
echo ""
echo "📝 Pour démarrer Tauri en mode dev :"
echo "  cd frontend && npm run tauri dev"
echo ""
echo "📊 Pour démarrer le monitoring (Prometheus/Grafana) :"
echo "  ./scripts/dev/start-monitoring.sh"
echo ""
echo "🛑 Pour arrêter tous les services : Ctrl+C"

# Attendre Ctrl+C
trap 'kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; echo "Services arrêtés"; exit' INT
wait
