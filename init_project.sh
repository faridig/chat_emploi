#!/bin/bash
# Script d'initialisation du projet Chat Emploi - Phase 0
# Conforme à TECH_SPECS.md et PLANNING.md
# Usage: ./init_project.sh

set -e  # Exit on error
set -o pipefail

echo "🚀 Initialisation du projet Chat Emploi"
echo "========================================"

# ------------------------------------------------------------
# 1. VÉRIFICATIONS PRÉALABLES
# ------------------------------------------------------------

echo "📋 Vérification des prérequis..."

# Vérifier Node.js
if ! command -v node &> /dev/null; then
    echo "❌ Node.js n'est pas installé. Veuillez installer Node.js 20+"
    exit 1
fi

# Vérifier npm
if ! command -v npm &> /dev/null; then
    echo "❌ npm n'est pas installé"
    exit 1
fi

# Vérifier Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 n'est pas installé"
    exit 1
fi

# Vérifier Rust (optionnel pour le moment, Tauri l'installera si besoin)
if ! command -v cargo &> /dev/null; then
    echo "⚠️  Rust/Cargo n'est pas installé. Tauri tentera de l'installer automatiquement."
fi

echo "✅ Prérequis vérifiés"
echo ""

# ------------------------------------------------------------
# 2. MISE À JOUR DU .gitignore
# ------------------------------------------------------------

echo "📁 Mise à jour du .gitignore..."

# Ajouter les patterns manquants pour Node.js, Rust, Tauri, Next.js
cat >> .gitignore << 'EOF'

### Node.js ###
# Dependencies
node_modules/
.pnpm-store/

# Build outputs
dist/
build/
.next/
out/

# Runtime data
.npm
.pnpm-debug.log*
.yarn-integrity

# Environment variables
.env*.local

# IDE
.vscode/
.idea/

# OS files
.DS_Store
Thumbs.db

### Rust/Tauri ###
# Rust build artifacts
target/
**/*.rs.bk

# Tauri
src-tauri/target/
src-tauri/Cargo.lock

### Next.js ###
.next/
out/

### Testing ###
coverage/
.nyc_output/

### Logs ###
*.log
logs/

### Misc ###
*.swp
*.swo
*~

### Project Specific ###
# Données utilisateur locales (seront stockées ailleurs)
.data/
.cache/
chroma_db/
redis-data/

# Fichiers de configuration locaux
config.local.json
secrets.local.json

# Fichiers temporaires
tmp/
temp/
EOF

echo "✅ .gitignore mis à jour"
echo ""

# ------------------------------------------------------------
# 3. CRÉATION DE L'ARBORESCENCE DES DOSSIERS
# ------------------------------------------------------------

echo "📂 Création de l'arborescence des dossiers..."

# Frontend structure
mkdir -p frontend/src/{app,components,lib,styles,hooks}
mkdir -p frontend/public
mkdir -p frontend/src-tauri/src

# Backend structure
mkdir -p backend/src/{api,agents,services,database,rag,monitoring}
mkdir -p backend/tests

# Shared structure
mkdir -p shared/{types,schemas,protocol}

# Scripts structure
mkdir -p scripts/{build,deploy,dev}

# Docs structure
mkdir -p docs/{api,architecture,user}

# Infrastructure structure
mkdir -p infrastructure/{github,grafana,prometheus}

echo "✅ Arborescence créée"
echo ""

# ------------------------------------------------------------
# 4. INITIALISATION DU FRONTEND (Tauri + Next.js)
# ------------------------------------------------------------

echo "🖥️  Initialisation du frontend..."

cd frontend

# Vérifier si le projet Next.js est déjà initialisé
if [ ! -f "package.json" ]; then
    echo "📦 Création du projet Next.js 15 avec TypeScript et App Router..."
    
    # Créer un package.json minimal pour éviter les conflits
    cat > package.json << 'EOF'
{
  "name": "chat-emploi-frontend",
  "version": "0.1.0",
  "private": true,
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "start": "next start",
    "lint": "next lint",
    "tauri": "tauri"
  }
}
EOF
    
    # Installer les dépendances Next.js de base
    echo "📥 Installation des dépendances Next.js..."
    npm install next@latest react@latest react-dom@latest @types/react @types/react-dom typescript @types/node tailwindcss postcss autoprefixer eslint eslint-config-next --save-dev
    
    # Initialiser TypeScript
    npx tsc --init --target es2020 --lib es2020,dom --module esnext --moduleResolution bundler --jsx react-jsx --strict true --esModuleInterop true --skipLibCheck true --forceConsistentCasingInFileNames true --noEmit true --incremental true --allowJs true --resolveJsonModule true --isolatedModules true
    
    # Initialiser Tailwind CSS
    npx tailwindcss init -p
    
    # Créer la configuration Next.js
    cat > next.config.ts << 'EOF'
import type { NextConfig } from 'next'

const nextConfig: NextConfig = {
  /* config options here */
  output: 'export', // Pour Tauri, on veut une build statique
  images: {
    unoptimized: true, // Nécessaire pour l'export statique
  },
  eslint: {
    ignoreDuringBuilds: true,
  },
  typescript: {
    ignoreBuildErrors: true,
  },
}

export default nextConfig
EOF
    
    # Créer la configuration Tailwind
    cat > tailwind.config.ts << 'EOF'
import type { Config } from 'tailwindcss'

const config: Config = {
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        primary: '#4A90E2',
        'primary-light': '#7BB4F5',
        secondary: '#50C878',
        'secondary-light': '#80E0A7',
        background: '#F8FAFC',
        surface: '#FFFFFF',
        border: '#E2E8F0',
        'text-primary': '#1A202C',
        'text-secondary': '#718096',
        'text-tertiary': '#A0AEC0',
        success: '#38A169',
        warning: '#D69E2E',
        error: '#E53E3E',
        info: '#4299E1',
        'accent-warm': '#FF6B6B',
        'accent-cool': '#9F7AEA',
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        mono: ['JetBrains Mono', 'monospace'],
      },
    },
  },
  plugins: [],
}
export default config
EOF
    
    # Créer les fichiers CSS globaux
    cat > src/styles/globals.css << 'EOF'
@tailwind base;
@tailwind components;
@tailwind utilities;

:root {
  --foreground-rgb: 26, 32, 44;
  --background-rgb: 248, 250, 252;
}

@media (prefers-color-scheme: dark) {
  :root {
    --foreground-rgb: 255, 255, 255;
    --background-rgb: 26, 32, 44;
  }
}

body {
  color: rgb(var(--foreground-rgb));
  background: rgb(var(--background-rgb));
  font-feature-settings: "ss01", "ss02", "cv01", "cv02";
}

@layer utilities {
  .text-balance {
    text-wrap: balance;
  }
}
EOF
    
    # Créer la structure App Router de base
    cat > src/app/layout.tsx << 'EOF'
import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import '../styles/globals.css'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'Chat Emploi',
  description: 'Votre coach emploi empathique',
}

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  return (
    <html lang="fr">
      <body className={inter.className}>{children}</body>
    </html>
  )
}
EOF
    
    cat > src/app/page.tsx << 'EOF'
export default function Home() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-24">
      <h1 className="text-4xl font-bold text-primary mb-4">
        Chat Emploi
      </h1>
      <p className="text-lg text-text-secondary mb-8">
        Votre coach emploi empathique
      </p>
      <div className="bg-surface rounded-lg p-8 shadow-lg max-w-md">
        <p className="text-text-primary mb-4">
          L&apos;application est en cours d&apos;initialisation...
        </p>
        <p className="text-sm text-text-tertiary">
          Le frontend Tauri + Next.js sera bientôt prêt !
        </p>
      </div>
    </main>
  )
}
EOF
    
    echo "✅ Projet Next.js initialisé"
else
    echo "✅ Projet Next.js déjà existant"
fi

# ------------------------------------------------------------
# 5. INITIALISATION DE TAURI
# ------------------------------------------------------------

echo "⚙️  Initialisation de Tauri..."

# Vérifier si Tauri est déjà configuré
if [ ! -f "src-tauri/Cargo.toml" ]; then
    echo "📦 Installation de Tauri CLI..."
    npm install @tauri-apps/cli @tauri-apps/api --save-dev
    
    # Initialiser Tauri dans le dossier src-tauri
    echo "⚙️  Configuration de Tauri..."
    npx tauri init \
        --app-name "Chat Emploi" \
        --window-title "Chat Emploi" \
        --dist-dir "../out" \
        --dev-path "http://localhost:3000"
    
    # Mettre à jour la configuration Tauri
    cat > src-tauri/tauri.conf.json << 'EOF'
{
  "productName": "Chat Emploi",
  "version": "0.1.0",
  "identifier": "com.chatemploi.app",
  "build": {
    "beforeDevCommand": "npm run dev",
    "beforeBuildCommand": "npm run build",
    "devPath": "http://localhost:3000",
    "distDir": "../out",
    "withGlobalTauri": false
  },
  "app": {
    "withGlobalTauri": false,
    "windows": [
      {
        "title": "Chat Emploi",
        "width": 1200,
        "height": 800,
        "minWidth": 800,
        "minHeight": 600,
        "resizable": true,
        "fullscreen": false,
        "center": true,
        "decorations": true
      }
    ],
    "security": {
      "csp": "default-src 'self'; connect-src https://*.googleapis.com https://api.france-travail.fr https://serpapi.com"
    }
  },
  "bundle": {
    "active": true,
    "targets": "all",
    "icon": [
      "icons/32x32.png",
      "icons/128x128.png",
      "icons/128x128@2x.png"
    ]
  }
}
EOF
    
    # Créer le fichier Rust principal
    cat > src-tauri/src/main.rs << 'EOF'
// Prevents additional console window on Windows in release, DO NOT REMOVE!!
#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

fn main() {
    chat_emploi_lib::run()
}
EOF
    
    # Créer le fichier lib.rs
    cat > src-tauri/src/lib.rs << 'EOF'
#![cfg_attr(
    all(not(debug_assertions), target_os = "windows"),
    windows_subsystem = "windows"
)]

#[tauri::command]
fn greet(name: &str) -> String {
    format!("Hello, {}! You've been greeted from Rust!", name)
}

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .plugin(tauri_plugin_opener::init())
        .invoke_handler(tauri::generate_handler![greet])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
EOF
    
    # Mettre à jour Cargo.toml
    cat > src-tauri/Cargo.toml << 'EOF'
[package]
name = "chat-emploi"
version = "0.1.0"
description = "Chat Emploi - Votre coach emploi empathique"
authors = ["Chat Emploi Team"]
license = "MIT"
edition = "2021"

# See more keys and their definitions at https://doc.rust-lang.org/cargo/reference/manifest.html

[build-dependencies]
tauri-build = { version = "2.0", features = [] }

[dependencies]
tauri = { version = "2.0", features = ["opener"] }
serde = { version = "1.0", features = ["derive"] }
serde_json = "1.0"
thiserror = "1.0"

[features]
default = ["custom-protocol"]
# this feature is used for production builds when using the desktop-only Tauri CLI
# it should NOT be enabled for mobile builds
custom-protocol = ["tauri/custom-protocol"]
EOF
    
    echo "✅ Tauri initialisé"
else
    echo "✅ Tauri déjà configuré"
fi

cd ..

echo "✅ Frontend initialisé"
echo ""

# ------------------------------------------------------------
# 6. INITIALISATION DU BACKEND PYTHON
# ------------------------------------------------------------

echo "🐍 Initialisation du backend Python..."

cd backend

# Créer un environnement virtuel s'il n'existe pas
if [ ! -d ".venv" ]; then
    echo "🔧 Création de l'environnement virtuel Python..."
    python3 -m venv .venv
fi

# Activer l'environnement virtuel
source .venv/bin/activate

# Créer les fichiers de configuration de base
echo "📄 Création des fichiers de configuration Python..."

# pyproject.toml
cat > pyproject.toml << 'EOF'
[project]
name = "chat-emploi-backend"
version = "0.1.0"
description = "Backend Python pour Chat Emploi"
authors = [{name = "Chat Emploi Team"}]
readme = "README.md"
requires-python = ">=3.11"
dependencies = [
    "fastapi>=0.115.0",
    "uvicorn[standard]>=0.30.0",
    "pydantic>=2.0.0",
    "sqlalchemy>=2.0.0",
    "alembic>=1.13.0",
    "chromadb>=0.5.0",
    "llama-index>=0.14.0",
    "langgraph>=0.1.0",
    "crewai>=0.28.0",
    "google-generativeai>=0.3.0",
    "python-dotenv>=1.0.0",
    "redis>=5.0.0",
    "prometheus-client>=0.20.0",
    "structlog>=24.0.0",
    "pypdf2>=3.0.0",
    "pdf2image>=1.16.0",
    "spacy>=3.7.0",
    "cryptography>=42.0.0",
    "msgpack>=1.0.0",
    "httpx>=0.27.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0.0",
    "pytest-asyncio>=0.23.0",
    "pytest-cov>=5.0.0",
    "black>=24.0.0",
    "ruff>=0.4.0",
    "mypy>=1.9.0",
    "pre-commit>=3.0.0",
    "ipython>=8.0.0",
    "jupyter>=1.0.0",
]

[build-system]
requires = ["setuptools>=61.0", "wheel"]
build-backend = "setuptools.build_meta"

[tool.black]
line-length = 88
target-version = ['py311']
include = '\.pyi?$'
extend-exclude = '''
/(
    \.git
  | \.hg
  | \.mypy_cache
  | \.tox
  | \.venv
  | _build
  | buck-out
  | build
  | dist
)/
'''

[tool.ruff]
target-version = "py311"
line-length = 88
select = [
    "E",  # pycodestyle errors
    "W",  # pycodestyle warnings
    "F",  # pyflakes
    "I",  # isort
    "B",  # flake8-bugbear
    "C4", # flake8-comprehensions
    "UP", # pyupgrade
]
ignore = [
    "E501",  # line too long, handled by black
    "B008",  # do not perform function calls in argument defaults
]

[tool.mypy]
python_version = "3.11"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
disallow_incomplete_defs = true
check_untyped_defs = true
disallow_untyped_decorators = true
no_implicit_optional = true
warn_redundant_casts = true
warn_unused_ignores = true
warn_no_return = true
warn_unreachable = true
strict_equality = true

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = "-v --cov=src --cov-report=term-missing --cov-report=html"
asyncio_mode = "auto"
EOF

# requirements.txt (pour compatibilité)
cat > requirements.txt << 'EOF'
# Production dependencies
fastapi>=0.115.0
uvicorn[standard]>=0.30.0
pydantic>=2.0.0
sqlalchemy>=2.0.0
alembic>=1.13.0
chromadb>=0.5.0
llama-index>=0.14.0
langgraph>=0.1.0
crewai>=0.28.0
google-generativeai>=0.3.0
python-dotenv>=1.0.0
redis>=5.0.0
prometheus-client>=0.20.0
structlog>=24.0.0
pypdf2>=3.0.0
pdf2image>=1.16.0
spacy>=3.7.0
cryptography>=42.0.0
msgpack>=1.0.0
httpx>=0.27.0

# Development dependencies (optionnel)
pytest>=8.0.0
pytest-asyncio>=0.23.0
pytest-cov>=5.0.0
black>=24.0.0
ruff>=0.4.0
mypy>=1.9.0
pre-commit>=3.0.0
EOF

# requirements-dev.txt
cat > requirements-dev.txt << 'EOF'
# Development dependencies
-r requirements.txt
pytest>=8.0.0
pytest-asyncio>=0.23.0
pytest-cov>=5.0.0
black>=24.0.0
ruff>=0.4.0
mypy>=1.9.0
pre-commit>=3.0.0
ipython>=8.0.0
jupyter>=1.0.0
EOF

# .env.example
cat > .env.example << 'EOF'
# Configuration backend Python
APP_ENV=development
APP_SECRET_KEY=change-this-in-production

# Base de données
DATABASE_URL=sqlite:///./chat_emploi.db

# Vector Store (ChromaDB)
CHROMA_DB_PATH=./chroma_db

# Cache Redis
REDIS_URL=redis://localhost:6379/0

# APIs externes
GEMINI_API_KEY=your-gemini-api-key-here
FRANCE_TRAVAIL_API_KEY=your-france-travail-api-key-here
SERPAPI_API_KEY=your-serpapi-api-key-here

# Configuration application
LOG_LEVEL=INFO
DEBUG=true
EOF

# Créer un fichier README pour le backend
cat > README.md << 'EOF'
# Backend Chat Emploi

Backend Python pour l'application Chat Emploi.

## Structure

- `src/api/` - Endpoints FastAPI
- `src/agents/` - Agents LangGraph/CrewAI
- `src/services/` - Services métier
- `src/database/` - Modèles SQLAlchemy et migrations
- `src/rag/` - Système RAG avec LlamaIndex
- `src/monitoring/` - Métriques Prometheus et logs

## Installation

1. Activer l'environnement virtuel :
   ```bash
   source .venv/bin/activate
   ```

2. Installer les dépendances :
   ```bash
   pip install -r requirements-dev.txt
   ```

3. Configurer les variables d'environnement :
   ```bash
   cp .env.example .env
   # Éditer .env avec vos clés API
   ```

4. Lancer le serveur de développement :
   ```bash
   uvicorn src.api.main:app --reload
   ```

## Tests

```bash
pytest tests/ -v
```
EOF

# Créer un fichier Python de base pour la structure
mkdir -p src/__init__.py
cat > src/__init__.py << 'EOF'
"""Backend Chat Emploi."""
__version__ = "0.1.0"
EOF

# Créer le point d'entrée FastAPI
cat > src/api/main.py << 'EOF'
"""Point d'entrée principal FastAPI."""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .rpc_server import json_rpc_router

# Configuration logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gestion du cycle de vie de l'application."""
    # Startup
    logger.info("Starting Chat Emploi backend...")
    yield
    # Shutdown
    logger.info("Shutting down Chat Emploi backend...")


# Création de l'application FastAPI
app = FastAPI(
    title="Chat Emploi Backend",
    description="Backend Python pour l'application Chat Emploi",
    version="0.1.0",
    lifespan=lifespan,
)

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # À restreindre en production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inclusion des routes
app.include_router(json_rpc_router, prefix="/api/v1")


@app.get("/")
async def root():
    """Endpoint racine."""
    return {"message": "Chat Emploi Backend API", "version": "0.1.0"}


@app.get("/health")
async def health():
    """Endpoint de santé."""
    return {"status": "healthy"}
EOF

echo "✅ Backend Python initialisé"
cd ..

echo ""

# ------------------------------------------------------------
# 7. CONFIGURATION DES LINTERS & FORMATEURS
# ------------------------------------------------------------

echo "🔧 Configuration des linters et formateurs..."

# Frontend: ESLint + Prettier
cd frontend
cat > .eslintrc.json << 'EOF'
{
  "extends": ["next/core-web-vitals", "next/typescript"],
  "rules": {
    "@typescript-eslint/no-unused-vars": ["error", { "argsIgnorePattern": "^_" }],
    "react/no-unescaped-entities": "off"
  }
}
EOF

cat > .prettierrc << 'EOF'
{
  "semi": true,
  "trailingComma": "es5",
  "singleQuote": true,
  "tabWidth": 2,
  "useTabs": false,
  "printWidth": 100,
  "endOfLine": "lf"
}
EOF

# Backend: pre-commit hooks
cd ../backend
cat > .pre-commit-config.yaml << 'EOF'
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files
      - id: check-merge-conflict
      - id: check-toml
      - id: check-json

  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.4.2
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.9.0
    hooks:
      - id: mypy
        additional_dependencies: [types-all]

  - repo: local
    hooks:
      - id: pytest-check
        name: pytest
        entry: pytest tests/ -v --tb=short
        language: system
        pass_filenames: false
        always_run: true
        stages: [push]
EOF

echo "✅ Linters et formateurs configurés"
cd ..

echo ""

# ------------------------------------------------------------
# 8. CRÉATION DES SCRIPTS DE DÉVELOPPEMENT
# ------------------------------------------------------------

echo "📜 Création des scripts de développement..."

# Scripts dans scripts/dev/
cat > scripts/dev/setup.sh << 'EOF'
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
EOF

cat > scripts/dev/start.sh << 'EOF'
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
echo ""
echo "📝 Pour démarrer Tauri en mode dev :"
echo "  cd frontend && npm run tauri dev"
echo ""
echo "🛑 Pour arrêter tous les services : Ctrl+C"

# Attendre Ctrl+C
trap 'kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; echo "Services arrêtés"; exit' INT
wait
EOF

# Rendre les scripts exécutables
chmod +x scripts/dev/setup.sh
chmod +x scripts/dev/start.sh

echo "✅ Scripts de développement créés"
echo ""

# ------------------------------------------------------------
# 9. CRÉATION DU README.md PRINCIPAL
# ------------------------------------------------------------

echo "📖 Création du README.md principal..."

cat > README.md << 'EOF'
# Chat Emploi

> Votre coach emploi empathique

Une application de bureau intelligente basée sur une architecture multi-agents (LangGraph, CrewAI) qui accompagne les demandeurs d'emploi dans leur recherche.

## 🎯 Vision

"Transformer la recherche d'emploi, processus solitaire et décourageant, en une expérience conversationnelle intelligente et empathique, où chaque demandeur d'emploi bénéficie d'un agent de carrière personnel, disponible 24h/24."

## 🏗️ Architecture Technique

### Stack utilisée

- **Frontend Desktop** : Tauri 2.0 + Next.js 15 (App Router) + TypeScript + Tailwind CSS
- **Backend Python** : FastAPI + LangGraph + CrewAI + LlamaIndex + ChromaDB
- **Base de données** : SQLite (données structurées) + ChromaDB (vecteurs)
- **Communication** : JSON-RPC over IPC (Tauri ↔ Python)
- **Monitoring** : Prometheus + Grafana (local)

### Structure du projet

```
chat_emploi/
├── frontend/          # Tauri + Next.js
├── backend/           # Python FastAPI + Agents
├── shared/            # Types partagés TypeScript/Python
├── scripts/           # Utilitaires build/dev
├── docs/              # Documentation
└── infrastructure/    # CI/CD, monitoring
```

## 🚀 Démarrage rapide

### Prérequis

- Node.js 20+
- Python 3.11+
- Rust (optionnel, Tauri l'installera si besoin)

### Installation

1. **Cloner le projet**
   ```bash
   git clone <repository>
   cd chat_emploi
   ```

2. **Setup automatique**
   ```bash
   ./scripts/dev/setup.sh
   ```

3. **Démarrer en développement**
   ```bash
   ./scripts/dev/start.sh
   ```

4. **Lancer Tauri en mode dev** (dans un autre terminal)
   ```bash
   cd frontend
   npm run tauri dev
   ```

### Accès aux services

- **Application Tauri** : S'ouvre automatiquement
- **Frontend Next.js** : http://localhost:3000
- **Backend FastAPI** : http://localhost:8000
- **Documentation API** : http://localhost:8000/docs
- **Monitoring Grafana** : http://localhost:3001 (après configuration)

## 📁 Structure des dossiers

### Frontend (`frontend/`)
- `src/app/` - Next.js App Router pages et layouts
- `src/components/` - Composants React réutilisables
- `src/lib/` - Utilities, hooks personnalisés
- `src-tauri/` - Code Rust pour Tauri (IPC, sidecar management)

### Backend (`backend/`)
- `src/api/` - Endpoints FastAPI et JSON-RPC
- `src/agents/` - Orchestration LangGraph/CrewAI
- `src/services/` - Logique métier (CV, offres, lettres)
- `src/database/` - Modèles SQLAlchemy, migrations
- `src/rag/` - Système RAG avec LlamaIndex + ChromaDB
- `src/monitoring/` - Métriques Prometheus, logs structurés

## 🧪 Tests

### Backend Python
```bash
cd backend
source .venv/bin/activate
pytest tests/ -v
```

### Frontend
```bash
cd frontend
npm test
```

### Tests E2E (Playwright)
```bash
cd frontend
npm run test:e2e
```

## 🔧 Configuration

### Variables d'environnement

Copier le fichier `.env.example` et configurer les clés API :

```bash
cd backend
cp .env.example .env
# Éditer .env avec vos clés API
```

### Clés API requises

1. **Google Gemini API** : Pour les modèles LLM et embeddings
2. **France Travail API** : Pour la recherche d'offres d'emploi
3. **SerpAPI** (optionnel) : Pour la recherche web complémentaire

## 📊 Monitoring & Observability

L'application inclut un dashboard Grafana local pour monitorer :

- **Performance** : Latence API, temps de génération
- **Usage** : CV traités, lettres générées, offres recherchées
- **Qualité** : Scores de matching, feedback utilisateurs
- **Système** : CPU, mémoire, disque, uptime

```bash
# Démarrer le monitoring (post-MVP)
docker-compose -f infrastructure/monitoring/docker-compose.yml up
```

## 🤝 Contribution

### Workflow de développement

1. **Phase 0** : Fondations & Outillage (CI/CD, linters, monitoring)
2. **Phase 1** : Cœur du système - Backend Python
3. **Phase 2** : Agents IA & RAG System
4. **Phase 3** : Frontend Tauri + Next.js
5. **Phase 4** : Intégration & Validation MVP

### Standards de code

- **Python** : Black + Ruff + Mypy (via pre-commit hooks)
- **TypeScript** : ESLint + Prettier
- **Rust** : rustfmt + clippy
- **Git** : Conventional Commits

### Qualité & Tests

- **Coverage minimum** : 85% backend, 75% frontend
- **TDD** pour les composants critiques
- **CI/CD** avec quality gates automatisés
- **Monitoring** intégré dès le début

## 📄 Documentation

- [PRD.md](./PRD.md) - Product Requirements Document
- [TECH_SPECS.md](./TECH_SPECS.md) - Spécifications techniques
- [DESIGN.md](./DESIGN.md) - Guidelines UX/UI
- [PLANNING.md](./PLANNING.md) - Roadmap & stratégie de test

## 📞 Support & Contact

- **Problèmes techniques** : Ouvrir une issue GitHub
- **Suggestions fonctionnelles** : Voir PRD.md pour la roadmap
- **Sécurité** : security@chatemploi.fr (pour les vulnérabilités)

## 📝 Licence

Propriétaire - Usage interne uniquement

---

*"La qualité n'est jamais un accident ; c'est toujours le résultat d'un effort intelligent." - John Ruskin*
EOF

echo "✅ README.md créé"
echo ""

# ------------------------------------------------------------
# 10. FINALISATION
# ------------------------------------------------------------

echo "🎉 Initialisation terminée !"
echo ""
echo "📋 Récapitulatif des actions effectuées :"
echo "   1. ✅ Arborescence des dossiers créée"
echo "   2. ✅ .gitignore mis à jour (Python/Node/Rust)"
echo "   3. ✅ Frontend initialisé (Next.js 15 + Tauri 2.0)"
echo "   4. ✅ Backend Python initialisé (FastAPI + agents)"
echo "   5. ✅ Linters et formateurs configurés"
echo "   6. ✅ Scripts de développement créés"
echo "   7. ✅ README.md principal créé"
echo ""
echo "🚀 Prochaines étapes :"
echo "   1. Exécuter le setup : ./scripts/dev/setup.sh"
echo "   2. Démarrer les services : ./scripts/dev/start.sh"
echo "   3. Configurer les clés API dans backend/.env"
echo "   4. Lancer Tauri : cd frontend && npm run tauri dev"
echo ""
echo "📚 Documentation :"
echo "   - PRD.md : Exigences fonctionnelles"
echo "   - TECH_SPECS.md : Architecture technique"
echo "   - DESIGN.md : Guidelines UX/UI"
echo "   - PLANNING.md : Roadmap de développement"
echo ""
echo "🔍 Pour vérifier la structure :"
echo "   find . -type d | sort"