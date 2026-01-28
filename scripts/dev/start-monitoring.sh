#!/bin/bash
# Script de démarrage du monitoring pour Chat Emploi
# Usage: ./scripts/dev/start-monitoring.sh

set -e

echo "📊 Démarrage du monitoring Chat Emploi"
echo "======================================"

# Vérifier si Docker est disponible
if command -v docker &> /dev/null; then
    echo "🐳 Docker détecté - démarrage avec Docker Compose..."

    # Créer docker-compose.yml si non existant
    if [ ! -f "infrastructure/monitoring/docker-compose.yml" ]; then
        echo "⚠️  docker-compose.yml non trouvé, création..."
        cat > infrastructure/monitoring/docker-compose.yml << 'EOF'
version: '3.8'

services:
  prometheus:
    image: prom/prometheus:latest
    container_name: chat-emploi-prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
      - ./alerts.yml:/etc/prometheus/alerts.yml
      - prometheus_data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--web.console.libraries=/etc/prometheus/console_libraries'
      - '--web.console.templates=/etc/prometheus/consoles'
      - '--storage.tsdb.retention.time=200h'
      - '--web.enable-lifecycle'
    restart: unless-stopped

  grafana:
    image: grafana/grafana:latest
    container_name: chat-emploi-grafana
    ports:
      - "3001:3000"
    volumes:
      - grafana_data:/var/lib/grafana
      - ./grafana-dashboard.json:/etc/grafana/provisioning/dashboards/chat-emploi.json
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
      - GF_INSTALL_PLUGINS=grafana-piechart-panel
    restart: unless-stopped
    depends_on:
      - prometheus

volumes:
  prometheus_data:
  grafana_data:
EOF
    fi

    # Démarrer les services
    cd infrastructure/monitoring
    docker-compose up -d
    cd ../..

    echo ""
    echo "✅ Monitoring démarré avec Docker !"
    echo ""
    echo "📊 Accès aux services :"
    echo "  Prometheus:  http://localhost:9090"
    echo "  Grafana:     http://localhost:3001 (admin/admin)"
    echo ""
    echo "🛑 Pour arrêter : docker-compose down (dans infrastructure/monitoring/)"

else
    echo "⚠️  Docker non disponible - démarrage manuel requis"
    echo ""
    echo "📋 Instructions manuelles :"
    echo ""
    echo "1. Télécharger Prometheus :"
    echo "   wget https://github.com/prometheus/prometheus/releases/download/v2.51.0/prometheus-2.51.0.linux-amd64.tar.gz"
    echo "   tar xvfz prometheus-*.tar.gz"
    echo "   cd prometheus-*"
    echo "   ./prometheus --config.file=../infrastructure/monitoring/prometheus.yml"
    echo ""
    echo "2. Télécharger Grafana :"
    echo "   wget https://dl.grafana.com/oss/release/grafana-10.4.1.linux-amd64.tar.gz"
    echo "   tar xvfz grafana-*.tar.gz"
    echo "   cd grafana-*/bin"
    echo "   ./grafana-server"
    echo ""
    echo "3. Importer le dashboard dans Grafana :"
    echo "   - Aller sur http://localhost:3001"
    echo "   - Admin/Admin"
    echo "   - Configuration → Data Sources → Add Prometheus"
    echo "   - URL: http://localhost:9090"
    echo "   - Dashboards → Import → Upload JSON"
    echo "   - Sélectionner infrastructure/monitoring/grafana-dashboard.json"
fi

echo ""
echo "📝 Pour démarrer l'application : ./scripts/dev/start.sh"
echo "📝 Pour tout démarrer : ./scripts/dev/start.sh & ./scripts/dev/start-monitoring.sh"
