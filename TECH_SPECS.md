# TECHNICAL SPECIFICATIONS - Chat Emploi
## Architecture Technique & Guide d'Implémentation
### Version 1.0 - MVP
**Date** : 27 janvier 2026  
**Architect** : CTO Lead  
**Statut** : Validé (Option 1 - Architecture Moderne)

---

## 1. STACK TECHNIQUE RETENUE

### 1.1 Frontend Desktop (Application Utilisateur)
- **Framework** : Tauri 2.0 + Next.js 15 (App Router)
- **Langage** : TypeScript 5.0+, React 18+
- **UI Framework** : Tailwind CSS 4.0 + shadcn/ui components
- **State Management** : Zustand (global) + React Query (server state)
- **Icons** : Lucide React Icons
- **Charts** : Recharts (pour dashboard statistiques)
- **PDF Viewer** : React-PDF (pour visualisation et annotation CV)
- **Drag & Drop** : @dnd-kit (pour dashboard Kanban)
- **Animation** : Framer Motion (micro-interactions)
- **Build Tool** : Vite (via Tauri)

### 1.2 Backend Python (Sidecar Process)
- **Framework API** : FastAPI 0.115+ avec Pydantic v2
- **Orchestration IA** : LangGraph 1.0 + CrewAI 0.28
- **RAG Framework** : LlamaIndex 0.14+
- **Vector Database** : Chroma DB (embeddings locaux)
- **Embedding Model** : Gemini `text-embedding-004` (API)
- **LLM Principal** : Gemini Pro 1.5 (API) avec fallback configurable
- **PDF Processing** : PyPDF2 + pdf2image (pour conversion PDF→images)
- **OCR Optionnel** : EasyOCR (si besoin extraction texte images)
- **Anonymisation NER** : spaCy fr_core_news_lg (détection entités)
- **Monitoring** : Prometheus Python Client + structlog
- **Sérialisation** : msgpack-rpc (pour IPC haute performance)

### 1.3 Base de Données & Stockage
- **Données structurées** : SQLite 3.45+ via SQLAlchemy 2.0
- **Vector Store** : Chroma DB (mode persistant local)
- **Cache API** : Redis Stack (local) pour cache offres France Travail
- **Stockage fichiers** : Système de fichiers local avec structure organisée
- **Chiffrement** : cryptography (AES-256-GCM) pour données sensibles

### 1.4 Infrastructure & Tooling
- **CI/CD** : GitHub Actions avec cache Rust/Python
- **Build Cross-platform** : Tauri CLI (Windows, macOS, Linux)
- **Monitoring UI** : Grafana (port 3001) + Prometheus (port 9090)
- **Logs structurés** : structlog + Loki (optionnel pour post-MVP)
- **Code Quality** : pre-commit hooks (ruff, mypy, black)
- **Testing** : pytest (backend) + Vitest (frontend) + Playwright (E2E)
- **Packaging** : Tauri updater (auto-updates) + codesign (macOS/Windows)

---

## 2. ARCHITECTURE SYSTÈME

### 2.1 Diagramme d'Architecture Global
```
┌─────────────────────────────────────────────────────────────────────────┐
│                           APPLICATION DESKTOP (TAURI)                    │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐   │
│  │   Renderer  │  │   Renderer  │  │   Renderer  │  │   Renderer  │   │
│  │  (Next.js)  │  │  (Next.js)  │  │  (Next.js)  │  │  (Next.js)  │   │
│  │    Accueil  │  │    Chat     │  │ Dashboard   │  │ Paramètres  │   │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘   │
│         │                 │                 │                 │         │
│  ┌──────────────────────────────────────────────────────────────┐       │
│  │                    TAURI CORE (Rust Runtime)                 │       │
│  │  ┌────────────┐  ┌────────────┐  ┌──────────────────────┐   │       │
│  │  │   IPC      │  │   FS       │  │   Window Management  │   │       │
│  │  │  Handler   │  │ Operations │  │    & State Sync      │   │       │
│  │  └─────┬──────┘  └─────┬──────┘  └──────────┬───────────┘   │       │
│  │        │                │                    │               │       │
│  │  ┌─────▼────────────────▼────────────────────▼───────────┐   │       │
│  │  │              Sidecar Manager (Rust)                   │   │       │
│  │  │  ┌──────────────────────────────────────────────┐    │   │       │
│  │  │  │        Python Backend Process                │    │   │       │
│  │  │  │  (stdin/stdout communication via JSON-RPC)   │    │   │       │
│  │  │  └──────────────────────────────────────────────┘    │   │       │
│  │  └──────────────────────────────────────────────────────┘   │       │
│  └──────────────────────────────────────────────────────────────┘       │
│                                                                         │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌───────────────────────────────────────────────────────────────────┐  │
│  │                     PYTHON BACKEND (SIDECAR)                      │  │
│  │                                                                   │  │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────┐  ┌────────────┐  │  │
│  │  │  FastAPI   │  │  LangGraph │  │  CrewAI    │  │ LlamaIndex │  │  │
│  │  │   Server   │  │ Orchestrator│  │  Agents    │  │   RAG      │  │  │
│  │  └─────┬──────┘  └─────┬──────┘  └─────┬──────┘  └─────┬──────┘  │  │
│  │        │                │                │                │        │  │
│  │  ┌─────▼────────────────▼────────────────▼────────────────▼───────┐  │
│  │  │                    Services Layer                               │  │
│  │  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐          │  │
│  │  │  │   CV     │ │  Offers  │ │  Letter  │ │ Interview│          │  │
│  │  │  │ Service  │ │ Service  │ │ Service  │ │  Service │          │  │
│  │  │  └────┬─────┘ └────┬─────┘ └────┬─────┘ └────┬─────┘          │  │
│  │  │       │             │             │             │               │  │
│  │  │  ┌────▼─────────────▼─────────────▼─────────────▼─────────────┐  │  │
│  │  │  │                    Data Access Layer                       │  │  │
│  │  │  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐      │  │  │
│  │  │  │  │ SQLite   │ │ ChromaDB │ │  Redis   │ │   FS     │      │  │  │
│  │  │  │  │ (SQLAlc) │ │ (Vector) │ │  (Cache) │ │  Store   │      │  │  │
│  │  │  │  └──────────┘ └──────────┘ └──────────┘ └──────────┘      │  │  │
│  │  │  └───────────────────────────────────────────────────────────┘  │  │
│  │  └─────────────────────────────────────────────────────────────────┘  │
│  └───────────────────────────────────────────────────────────────────────┘
│                                                                         │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌───────────────────────────────────────────────────────────────────┐  │
│  │                     EXTERNAL SERVICES                             │  │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────────────────────┐  │  │
│  │  │   Gemini   │  │ France     │  │   Web Search               │  │  │
│  │  │    API     │  │ Travail    │  │   (SerpAPI/Google Custom)  │  │  │
│  │  │(chat+embed)│  │   API      │  │                            │  │  │
│  │  └────────────┘  └────────────┘  └────────────────────────────┘  │  │
│  └───────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────┘
```

### 2.2 Flux de Données Principaux

#### 2.2.1 Import & Anonymisation CV
```
Utilisateur (Frontend)
    ↓ drag & drop PDF/DOCX
Tauri FS Module → sauvegarde originale temporaire
    ↓
React-PDF Viewer → rendu PDF en canvas
    ↓
Interface Annotation → utilisateur sélectionne zones sensibles
    ↓
Canvas Processing → applique pixels noirs sur zones
    ↓
Export PDF anonymisé → sauvegarde locale chiffrée
    ↓
IPC → Python Backend pour analyse via Gemini
    ↓
Gemini API → extraction structured (JSON)
    ↓
SQLite → stockage profil anonymisé
```

#### 2.2.2 Recherche & Matching RAG
```
Profil utilisateur (SQLite)
    ↓
Service Embedding → Gemini text-embedding-004
    ↓
Vector (768-dim) → stocké dans ChromaDB (collection "profiles")
    ↓
API France Travail → fetch offres (cache Redis 24h)
    ↓
Embedding offres → Gemini text-embedding-004
    ↓
Vector offres → ChromaDB (collection "offers")
    ↓
Similarity Search → cosine similarity top-k=5
    ↓
Re-ranking → LLM-based relevancy scoring (Gemini Pro)
    ↓
Résultats → retour frontend avec scores (0-100%)
```

#### 2.2.3 Génération Lettre de Motivation
```
Offre sélectionnée + Profil utilisateur
    ↓
Agent "LetterWriter" (CrewAI) → prompt engineering
    ↓
Context Building → CV highlights + offre requirements
    ↓
Gemini Pro 1.5 → génération avec template structured
    ↓
Post-processing → validation longueur (300-500 mots)
    ↓
Formatting → HTML → PDF (WeasyPrint)
    ↓
Sauvegarde → SQLite + système fichiers
```

### 2.3 Orchestration Multi-Agents (LangGraph + CrewAI)

#### 2.3.1 Équipe d'Agents Spécialisés
```python
# Architecture d'équipe CrewAI
Agents = {
    "coach": {
        "role": "Career Coach & Profile Analyst",
        "goal": "Understand user situation, provide empathetic guidance",
        "backstory": "Experienced career counselor with psychology background",
        "tools": ["cv_analyzer", "profile_enricher", "conversation_memory"]
    },
    "researcher": {
        "role": "Job Market Research Specialist", 
        "goal": "Find relevant job opportunities based on profile",
        "backstory": "Data-driven researcher with deep knowledge of job market",
        "tools": ["france_travail_api", "web_search", "rag_retriever"]
    },
    "writer": {
        "role": "Motivation Letter Specialist",
        "goal": "Create personalized, persuasive motivation letters",
        "backstory": "Professional writer with HR recruitment experience",
        "tools": ["template_engine", "tone_adjuster", "plagiarism_checker"]
    },
    "interview_coach": {
        "role": "Interview Preparation Expert",
        "goal": "Prepare user for interviews with personalized simulations",
        "backstory": "Former HR manager with 1000+ interviews conducted",
        "tools": ["question_generator", "feedback_analyzer", "stress_detector"]
    }
}
```

#### 2.3.2 Workflow LangGraph
```python
# State definition pour le workflow utilisateur
class UserSessionState(TypedDict):
    user_id: str
    current_step: Literal["profile", "search", "selection", "letter", "interview", "tracking"]
    profile_data: Dict[str, Any]
    selected_offers: List[Dict[str, Any]]
    generated_documents: List[Dict[str, Any]]
    conversation_history: List[Dict[str, str]]
    session_metrics: Dict[str, float]

# Graph d'orchestration principal
graph = StateGraph(UserSessionState)
graph.add_node("profile_analysis", profile_agent)
graph.add_node("job_search", research_agent)  
graph.add_node("offer_selection", selection_agent)
graph.add_node("letter_generation", writer_agent)
graph.add_node("interview_prep", interview_agent)

# Routing conditionnel basé sur l'état
graph.add_conditional_edges(
    START,
    lambda state: "profile_analysis" if not state.get("profile_data") else "job_search"
)
graph.add_edge("profile_analysis", "job_search")
graph.add_edge("job_search", "offer_selection")
graph.add_edge("offer_selection", "letter_generation")
graph.add_edge("letter_generation", "interview_prep")
graph.add_edge("interview_prep", END)
```

---

## 3. MODÈLE DE DONNÉES

### 3.1 Base SQLite (Schéma Principal)

```sql
-- Table: users (sessions locales)
CREATE TABLE users (
    id TEXT PRIMARY KEY,  -- UUID v7
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_active TIMESTAMP,
    settings JSON,  -- préférences utilisateur
    metadata JSON   -- données techniques (version, os, etc.)
);

-- Table: anonymized_profiles
CREATE TABLE anonymized_profiles (
    id TEXT PRIMARY KEY,
    user_id TEXT REFERENCES users(id) ON DELETE CASCADE,
    original_hash TEXT,  -- hash du fichier original (pour déduplication)
    anonymized_path TEXT,  -- chemin fichier anonymisé
    analysis_json JSON,  -- sortie Gemini structurée
    extracted_data JSON,  -- {skills: [], experiences: [], education: [], ...}
    embedding_vector BLOB,  -- embedding Gemini (serialized)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP
);

-- Table: job_offers (cache local)
CREATE TABLE job_offers (
    id TEXT PRIMARY KEY,  -- ID France Travail + hash
    source TEXT,  -- 'france_travail', 'web_scraped', 'manual'
    raw_data JSON,  -- données complètes API
    title TEXT,
    company TEXT,
    location TEXT,
    contract_type TEXT,
    publication_date DATE,
    description TEXT,
    requirements TEXT,
    embedding_vector BLOB,
    fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP  -- cache invalidation (30 jours)
);

-- Table: applications (suivi candidatures)
CREATE TABLE applications (
    id TEXT PRIMARY KEY,
    user_id TEXT REFERENCES users(id) ON DELETE CASCADE,
    profile_id TEXT REFERENCES anonymized_profiles(id),
    offer_id TEXT REFERENCES job_offers(id),
    status TEXT CHECK(status IN ('draft', 'applied', 'interview', 'rejected', 'accepted')),
    applied_date DATE,
    cover_letter_path TEXT,
    notes TEXT,
    interview_date TIMESTAMP,
    reminders JSON,  -- {reminder1: datetime, reminder2: datetime}
    metrics JSON,  -- {match_score: 0.85, letter_quality: 0.92, ...}
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP
);

-- Table: conversation_history
CREATE TABLE conversation_history (
    id TEXT PRIMARY KEY,
    user_id TEXT REFERENCES users(id) ON DELETE CASCADE,
    session_id TEXT,
    agent_type TEXT,  -- 'coach', 'researcher', 'writer', 'interviewer'
    message_type TEXT CHECK(message_type IN ('user', 'agent')),
    content TEXT,
    metadata JSON,  -- {tokens: 150, latency: 1.2, model: 'gemini-pro'}
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table: feedback (amélioration continue)
CREATE TABLE feedback (
    id TEXT PRIMARY KEY,
    user_id TEXT REFERENCES users(id) ON DELETE CASCADE,
    item_type TEXT,  -- 'offer', 'letter', 'interview', 'agent_response'
    item_id TEXT,  -- référence à l'item évalué
    rating INTEGER CHECK(rating BETWEEN 1 AND 5),
    comment TEXT,
    metadata JSON,  -- {context: 'search_results', step: 'offer_selection'}
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 3.2 ChromaDB Collections
```python
# Collection: user_profiles
{
    "id": "user_{uuid}",
    "embedding": vector_768_dim,  # Gemini embedding-004
    "metadata": {
        "skills": ["python", "react", "project_management"],
        "experience_years": 5,
        "education_level": "master",
        "last_updated": "2026-01-27T10:30:00Z"
    },
    "document": "JSON stringified profile summary"
}

# Collection: job_offers  
{
    "id": "offer_{source}_{id}",
    "embedding": vector_768_dim,
    "metadata": {
        "title": "Développeur Full-Stack",
        "company": "Startup Tech",
        "location": "Paris",
        "contract": "CDI",
        "publication_date": "2026-01-25",
        "salary_range": "45k-55k"
    },
    "document": "Full offer description text"
}
```

### 3.3 Justification des Choix Base de Données

**SQLite** :
- ✅ Parfait pour application desktop mono-utilisateur
- ✅ Zero-configuration, fichiers locaux
- ✅ Transactions ACID complètes
- ✅ Bonnes performances jusqu'à 100k+ lignes
- ✅ Support JSON natif (JSON1 extension)

**ChromaDB** :
- ✅ Conçu spécifiquement pour les embeddings
- ✅ Persistance locale simple
- ✅ Intégration native avec LlamaIndex
- ✅ Recherche similitude optimisée
- ✅ Métadonnées riches et queryable

**Redis Stack (cache)** :
- ✅ Cache mémoire pour API externes
- ✅ TTL automatique (24h pour offres)
- ✅ Structures de données riches
- ✅ Pub/Sub pour future extensibilité

---

## 4. DÉFINITION DES API

### 4.1 Style d'API : JSON-RPC over IPC
- **Transport** : stdin/stdout entre Tauri (Rust) et Python
- **Format** : JSON-RPC 2.0 avec batch support
- **Authentification** : session token local (généré au démarrage)
- **Versioning** : header `X-API-Version: 1.0`

### 4.2 Endpoints Principaux (Python Backend)

#### 4.2.1 CV Processing & Analysis
```python
# Request
{
    "jsonrpc": "2.0",
    "method": "cv.process_and_analyze",
    "params": {
        "file_path": "/path/to/anonymized_cv.pdf",
        "anonymization_regions": [
            {"page": 1, "x": 100, "y": 150, "width": 200, "height": 50},
            {"page": 1, "x": 300, "y": 200, "width": 150, "height": 30}
        ],
        "options": {
            "extract_skills": true,
            "detect_experience": true,
            "infer_education": true
        }
    },
    "id": 1
}

# Response
{
    "jsonrpc": "2.0",
    "result": {
        "profile_id": "profile_abc123",
        "extracted_data": {
            "skills": [
                {"name": "Python", "level": "advanced", "years": 5},
                {"name": "React", "level": "intermediate", "years": 3}
            ],
            "experiences": [
                {
                    "title": "Développeur Full-Stack",
                    "company": "Tech Corp",
                    "duration": "2 years",
                    "description": "Développement applications web..."
                }
            ],
            "education": [
                {"degree": "Master Informatique", "school": "Université Paris", "year": 2020}
            ]
        },
        "embedding_generated": true,
        "processing_time_ms": 2450
    },
    "id": 1
}
```

#### 4.2.2 Job Search & Matching
```python
# Request
{
    "jsonrpc": "2.0",
    "method": "jobs.search_and_match",
    "params": {
        "profile_id": "profile_abc123",
        "filters": {
            "location": "Paris",
            "contract_type": ["CDI", "CDD"],
            "remote_ok": true,
            "publication_max_days": 30
        },
        "search_options": {
            "max_results": 50,
            "use_cache": true,
            "force_refresh": false
        }
    },
    "id": 2
}

# Response
{
    "jsonrpc": "2.0",
    "result": {
        "search_id": "search_xyz789",
        "matches": [
            {
                "offer_id": "offer_ft_12345",
                "match_score": 0.87,
                "explanation": "Strong alignment on Python skills and 3+ years experience",
                "offer_details": {
                    "title": "Développeur Python Senior",
                    "company": "DataTech SA",
                    "location": "Paris (75)",
                    "contract": "CDI",
                    "salary": "55k-65k",
                    "description_preview": "Nous recherchons un développeur Python expérimenté..."
                }
            },
            {
                "offer_id": "offer_ft_12346",
                "match_score": 0.72,
                "explanation": "Good match on React skills, but requires more seniority",
                "offer_details": {...}
            }
        ],
        "search_metrics": {
            "total_offers_fetched": 47,
            "offers_after_filtering": 23,
            "matching_time_ms": 3200,
            "cache_hit": true
        }
    },
    "id": 2
}
```

#### 4.2.3 Cover Letter Generation
```python
# Request
{
    "jsonrpc": "2.0",
    "method": "documents.generate_cover_letter",
    "params": {
        "profile_id": "profile_abc123",
        "offer_id": "offer_ft_12345",
        "generation_options": {
            "tone": "professional",  # professional, enthusiastic, formal
            "length": "medium",  # short (250w), medium (350w), detailed (500w)
            "highlight_experiences": ["exp_1", "exp_2"],
            "custom_instructions": "Focus on my Python backend experience"
        }
    },
    "id": 3
}

# Response
{
    "jsonrpc": "2.0",
    "result": {
        "document_id": "letter_def456",
        "content": {
            "html": "<div class='letter'>...formatted HTML...</div>",
            "markdown": "# Lettre de motivation...",
            "plain_text": "Madame, Monsieur,\n\nJe vous écrite..."
        },
        "metadata": {
            "word_count": 342,
            "generation_time_ms": 4500,
            "model_used": "gemini-pro-1.5",
            "tokens_consumed": 1250
        },
        "file_paths": {
            "pdf": "/data/letters/letter_def456.pdf",
            "html": "/data/letters/letter_def456.html",
            "json": "/data/letters/letter_def456.json"
        }
    },
    "id": 3
}
```

### 4.3 API Externes Consommées

#### 4.3.1 Gemini API (Google AI Studio)
- **Endpoint** : `https://generativelanguage.googleapis.com/v1beta/models`
- **Models utilisés** :
  - `gemini-pro-1.5` : Génération texte (chat, lettres)
  - `text-embedding-004` : Embeddings (CV & offres)
- **Rate limiting** : 60 RPM / 1,000 TPM (par défaut)
- **Coût estimé MVP** : ~$50-100/mois pour usage intensif

#### 4.3.2 API France Travail
- **Format** : JSON API (documentation locale fournie)
- **Endpoints** :
  - `GET /api/offres` : Recherche avec filtres
  - `GET /api/offres/{id}` : Détail d'une offre
- **Cache** : Redis TTL 24h (conformité données fraîches)
- **Fallback** : Recherche web via SerpAPI si indisponible

#### 4.3.3 SerpAPI (Recherche Web)
- **Usage** : Recherche offres complémentaires
- **Limits** : 100 recherches/mois (plan gratuit)
- **Alternative** : Google Custom Search JSON API

---

## 5. STRATÉGIE DE SÉCURITÉ

### 5.1 Protection des Données Personnelles

#### 5.1.1 Anonymisation Visuelle (Client-side)
```typescript
// Processus d'anonymisation frontend
interface AnonymizationProcess {
  // Étape 1 : Conversion PDF → Canvas
  const pages = await pdfjs.getDocument(pdfPath).promise;
  
  // Étape 2 : Interface utilisateur pour sélection zones
  // Utilisation de react-canvas-draw pour sélection rectangulaire
  
  // Étape 3 : Application pixels noirs
  const canvas = document.createElement('canvas');
  const ctx = canvas.getContext('2d');
  ctx.fillStyle = '#000000';
  ctx.fillRect(x, y, width, height); // Pour chaque zone
  
  // Étape 4 : Reconversion en PDF anonymisé
  const anonymizedPDF = await canvasToPDF(canvas);
  
  // Étape 5 : Suppression fichiers temporaires
  await secureDelete(originalFile);
}
```

#### 5.1.2 Détection Automatique NER (Backend)
```python
# Détection complémentaire avec spaCy
import spacy

nlp = spacy.load("fr_core_news_lg")

def detect_sensitive_entities(text: str) -> List[Dict]:
    """Détecte les entités sensibles dans le texte extrait"""
    doc = nlp(text)
    sensitive_entities = []
    
    for ent in doc.ents:
        if ent.label_ in ["PER", "ORG", "LOC", "MISC"]:
            sensitive_entities.append({
                "text": ent.text,
                "label": ent.label_,
                "start": ent.start_char,
                "end": ent.end_char,
                "confidence": ent._.score if hasattr(ent._, "score") else 0.8
            })
    
    return sensitive_entities
```

### 5.2 Chiffrement & Stockage Sécurisé

#### 5.2.1 Chiffrement AES-256-GCM
```python
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import os

class SecureStorage:
    def __init__(self, user_salt: bytes):
        # Dérivation de clé depuis un secret utilisateur
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=user_salt,
            iterations=100000
        )
        key = base64.urlsafe_b64encode(kdf.derive(b"user-master-secret"))
        self.cipher = Fernet(key)
    
    def encrypt_data(self, data: Dict) -> bytes:
        serialized = json.dumps(data).encode('utf-8')
        return self.cipher.encrypt(serialized)
    
    def decrypt_data(self, encrypted: bytes) -> Dict:
        decrypted = self.cipher.decrypt(encrypted)
        return json.loads(decrypted.decode('utf-8'))
```

#### 5.2.2 Gestion des Secrets API
```rust
// Côté Tauri (Rust) - Stockage sécurisé des clés API
#[derive(Serialize, Deserialize)]
struct ApiSecrets {
    gemini_api_key: String,
    france_travail_token: String,
    serpapi_key: String,
}

impl ApiSecrets {
    fn load() -> Result<Self> {
        // Lecture depuis le secure storage du système
        // macOS: Keychain, Windows: Credential Manager, Linux: libsecret
        let stored = system_keychain::get("chat_emploi_secrets")?;
        serde_json::from_str(&stored).map_err(|e| e.into())
    }
    
    fn save(&self) -> Result<()> {
        let serialized = serde_json::to_string(self)?;
        system_keychain::set("chat_emploi_secrets", &serialized)
    }
}
```

### 5.3 Isolation & Sandboxing

#### 5.3.1 Architecture en Sandbox
- **Processus Python** : Exécuté dans un environnement virtuel isolé
- **Communications** : Seulement via stdin/stdout sérialisé JSON
- **Accès fichiers** : Restreint au dossier `~/.chat_emploi/data/`
- **Network access** : Whitelist uniquement (api.gemini, france-travail, serpapi)
- **Tauri permissions** : Déclarées explicitement dans `tauri.conf.json`

#### 5.3.2 Configuration Tauri Security
```json
{
  "tauri": {
    "security": {
      "csp": "default-src 'self'; connect-src https://*.googleapis.com https://api.france-travail.fr https://serpapi.com",
      "dangerousDisableAssetCspModification": false
    },
    "bundle": {
      "active": true,
      "targets": ["deb", "appimage", "msi", "dmg"],
      "icon": ["icons/32x32.png", "icons/128x128.png", "icons/128x128@2x.png"]
    }
  }
}
```

### 5.4 Conformité RGPD

#### 5.4.1 Principes Implementés
1. **Minimisation des données** : Seules données nécessaires collectées
2. **Stockage local** : Pas de transfert cloud non consent
3. **Droit à l'effacement** : Suppression complète via interface
4. **Transparence** : Logs d'accès consultables dans l'application
5. **Privacy by design** : Anonymisation avant tout traitement IA

#### 5.4.2 Journal d'Audit
```sql
CREATE TABLE audit_logs (
    id TEXT PRIMARY KEY,
    user_id TEXT REFERENCES users(id),
    event_type TEXT,  -- 'cv_upload', 'api_call', 'data_export', 'data_deletion'
    event_data JSON,
    ip_address TEXT,  -- localhost seulement
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## 6. PLAN DE TEST & CI/CD

### 6.1 Stratégie de Testing

#### 6.1.1 Tests Unitaires (Backend Python)
```python
# Structure de tests pytest
tests/
├── unit/
│   ├── test_cv_processing.py
│   ├── test_embedding_service.py
│   ├── test_rag_matching.py
│   └── test_letter_generation.py
├── integration/
│   ├── test_api_endpoints.py
│   ├── test_database_operations.py
│   └── test_external_apis.py
└── fixtures/
    ├── sample_cv.pdf
    ├── sample_offers.json
    └── mock_responses/

# Exemple: Test de matching RAG
def test_rag_matching_accuracy():
    """Test que le matching retourne les offres les plus pertinentes"""
    profile = create_sample_profile()
    offers = load_sample_offers()
    
    matches = rag_service.find_matches(profile, offers, top_k=3)
    
    assert len(matches) == 3
    assert matches[0].score >= 0.7  # Seuil de pertinence minimum
    assert "Python" in matches[0].explanation  # Vérification explication
```

#### 6.1.2 Tests Composants Frontend (Vitest)
```typescript
// Tests composants React
describe('CVAnonymizationTool', () => {
  test('permet la sélection de zones rectangulaires', async () => {
    const { container } = render(<CVAnonymizationTool pdfUrl={samplePDF} />);
    
    const canvas = container.querySelector('canvas');
    expect(canvas).toBeInTheDocument();
    
    // Simuler clic et drag pour sélection zone
    fireEvent.mouseDown(canvas, { clientX: 100, clientY: 100 });
    fireEvent.mouseMove(canvas, { clientX: 200, clientY: 200 });
    fireEvent.mouseUp(canvas);
    
    // Vérifier qu'une zone a été ajoutée
    expect(screen.getByText('Zone 1')).toBeInTheDocument();
  });
});
```

#### 6.1.3 Tests End-to-End (Playwright)
```typescript
// Scénario complet utilisateur
test('complète un cycle de candidature', async ({ page }) => {
  // 1. Import CV
  await page.goto('/');
  await page.setInputFiles('input[type="file"]', 'sample_cv.pdf');
  await page.waitForSelector('[data-testid="cv-preview"]');
  
  // 2. Anonymisation
  await page.click('[data-testid="anonymize-btn"]');
  await page.waitForSelector('[data-testid="anonymization-canvas"]');
  
  // 3. Conversation avec agent
  await page.fill('[data-testid="chat-input"]', 'Je cherche un poste de dev Python');
  await page.click('[data-testid="send-btn"]');
  await expect(page.locator('[data-testid="agent-message"]')).toHaveCount(1);
  
  // 4. Recherche offres
  await page.click('[data-testid="search-offers-btn"]');
  await page.waitForSelector('[data-testid="offer-card"]', { timeout: 10000 });
  
  // 5. Génération lettre
  await page.click('[data-testid="offer-card"]:first-child [data-testid="generate-letter-btn"]');
  await page.waitForSelector('[data-testid="letter-preview"]', { timeout: 15000 });
  
  // 6. Vérification dashboard
  await page.click('[data-testid="dashboard-tab"]');
  await expect(page.locator('[data-testid="application-card"]')).toHaveCount(1);
});
```

### 6.2 CI/CD Pipeline (GitHub Actions)

#### 6.2.1 Workflow Principal
```yaml
name: Build and Test

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test-backend:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ['3.11', '3.12']
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Setup Python ${{ matrix.python-version }}
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}
        cache: 'pip'
    
    - name: Install dependencies
      run: |
        cd backend
        pip install -r requirements-dev.txt
        pip install -e .
    
    - name: Run unit tests
      run: |
        cd backend
        pytest tests/unit/ -v --cov=src --cov-report=xml
    
    - name: Upload coverage
      uses: codecov/codecov-action@v3
      with:
        file: backend/coverage.xml
        flags: backend

  test-frontend:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Setup Node.js
      uses: actions/setup-node@v4
      with:
        node-version: '20'
        cache: 'npm'
    
    - name: Install dependencies
      run: |
        cd frontend
        npm ci
    
    - name: Run unit tests
      run: |
        cd frontend
        npm test -- --coverage
    
    - name: Run E2E tests
      run: |
        cd frontend
        npm run test:e2e
    
    - name: Upload frontend coverage
      uses: codecov/codecov-action@v3
      with:
        directory: frontend/coverage/
        flags: frontend

  build-cross-platform:
    needs: [test-backend, test-frontend]
    runs-on: ${{ matrix.os }}
    strategy:
      matrix:
        os: [macos-latest, ubuntu-latest, windows-latest]
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Setup Rust
      uses: dtolnay/rust-toolchain@stable
      with:
        targets: ${{ matrix.os == 'macos-latest' && 'aarch64-apple-darwin,x86_64-apple-darwin' || matrix.os == 'windows-latest' && 'x86_64-pc-windows-msvc' || 'x86_64-unknown-linux-gnu' }}
    
    - name: Setup Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.12'
        cache: 'pip'
    
    - name: Cache Cargo dependencies
      uses: actions/cache@v3
      with:
        path: |
          ~/.cargo/registry
          ~/.cargo/git
          target
        key: ${{ runner.os }}-cargo-${{ hashFiles('**/Cargo.lock') }}
    
    - name: Build Tauri application
      run: |
        cd frontend
        npm ci
        npm run tauri build
    
    - name: Upload artifacts
      uses: actions/upload-artifact@v3
      with:
        name: chat-emploi-${{ matrix.os }}
        path: frontend/src-tauri/target/release/bundle/
```

#### 6.2.2 Release Pipeline
```yaml
name: Release

on:
  push:
    tags:
      - 'v*'

jobs:
  create-release:
    runs-on: ubuntu-latest
    outputs:
      upload_url: ${{ steps.create_release.outputs.upload_url }}
    
    steps:
    - name: Create Release
      id: create_release
      uses: softprops/action-gh-release@v1
      with:
        name: Release ${{ github.ref_name }}
        draft: true
        prerelease: false

  build-all-platforms:
    needs: create-release
    strategy:
      matrix:
        include:
          - platform: 'macos-latest'
            target: 'universal-apple-darwin'
            extension: '.dmg'
          - platform: 'windows-latest'
            target: 'x86_64-pc-windows-msvc'
            extension: '.msi'
          - platform: 'ubuntu-latest'
            target: 'x86_64-unknown-linux-gnu'
            extension: '.AppImage'
    
    runs-on: ${{ matrix.platform }}
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Setup build environment
      run: |
        # Setup spécifique par plateforme
        if [ "${{ matrix.platform }}" = "ubuntu-latest" ]; then
          sudo apt-get update
          sudo apt-get install -y libwebkit2gtk-4.1-dev libssl-dev
        fi
    
    - name: Build application
      run: |
        cd frontend
        npm ci
        npm run tauri build -- --target ${{ matrix.target }}
    
    - name: Upload release asset
      uses: actions/upload-release-asset@v1
      with:
        upload_url: ${{ needs.create-release.outputs.upload_url }}
        asset_path: frontend/src-tauri/target/${{ matrix.target }}/release/bundle/*${{ matrix.extension }}
        asset_name: chat-emploi-${{ github.ref_name }}-${{ matrix.target }}${{ matrix.extension }}
        asset_content_type: application/octet-stream
```

### 6.3 Monitoring & Observability

#### 6.3.1 Métriques Prometheus
```python
# Configuration métriques backend
from prometheus_client import Counter, Histogram, Gauge

# Métriques d'usage
CV_PROCESSED = Counter('cv_processed_total', 'Total CVs processed')
OFFERS_FETCHED = Counter('offers_fetched_total', 'Total job offers fetched')
LETTERS_GENERATED = Counter('letters_generated_total', 'Total cover letters generated')

# Métriques de performance
API_LATENCY = Histogram('api_latency_seconds', 'API call latency', ['endpoint'])
RAG_MATCHING_TIME = Histogram('rag_matching_seconds', 'RAG matching time')
LLM_GENERATION_TIME = Histogram('llm_generation_seconds', 'LLM generation time')

# Métriques de qualité
MATCH_SCORE = Gauge('match_score_current', 'Current match score for latest search')
LETTER_QUALITY = Gauge('letter_quality_score', 'Quality score of generated letters')
USER_SATISFACTION = Gauge('user_satisfaction_score', 'User feedback rating')

# Métriques système
MEMORY_USAGE = Gauge('memory_usage_bytes', 'Memory usage in bytes')
CPU_USAGE = Gauge('cpu_usage_percent', 'CPU usage percentage')
DISK_USAGE = Gauge('disk_usage_bytes', 'Disk usage in bytes')
```

#### 6.3.2 Dashboard Grafana
- **URL** : `http://localhost:3001` (démarre avec l'application)
- **Panels principaux** :
  1. **Performance** : Latence API, temps de génération, matching speed
  2. **Usage** : CV traités, lettres générées, offres recherchées
  3. **Qualité** : Scores de matching, feedback utilisateurs, erreurs
  4. **Système** : CPU, mémoire, disque, uptime
  5. **Coûts** : Token usage Gemini, appels API externes

#### 6.3.3 Alerting Local
```yaml
# Configuration alertes (alertmanager.yml local)
route:
  receiver: 'desktop-notification'
  group_wait: 10s
  group_interval: 1m

receivers:
- name: 'desktop-notification'
  webhook_configs:
  - url: 'http://localhost:3030/alerts'
    send_resolved: true

# Règles d'alerte
groups:
- name: performance
  rules:
  - alert: HighAPILatency
    expr: api_latency_seconds{quantile="0.95"} > 5
    for: 5m
    labels:
      severity: warning
    annotations:
      summary: "API latency above 5 seconds"
      
  - alert: LowMatchQuality
    expr: match_score_current < 0.5
    for: 10m
    labels:
      severity: critical
    annotations:
      summary: "Match quality below 50% threshold"
```

---

## 7. GUIDE DE DÉPLOIEMENT & MAINTENANCE

### 7.1 Structure du Projet
```
chat_emploi/
├── frontend/                    # Application Tauri + Next.js
│   ├── src/
│   │   ├── app/                # Next.js App Router
│   │   ├── components/         # Composants React
│   │   ├── lib/               # Utilities, types, config
│   │   ├── styles/            # Tailwind + CSS modules
│   │   └── hooks/             # Custom React hooks
│   ├── public/                # Assets statiques
│   ├── src-tauri/             # Tauri Rust backend
│   │   ├── src/              # Rust code (IPC, sidecar management)
│   │   ├── Cargo.toml
│   │   └── tauri.conf.json
│   └── package.json
│
├── backend/                    # Python sidecar process
│   ├── src/
│   │   ├── api/              # FastAPI endpoints
│   │   ├── agents/           # LangGraph/CrewAI agents
│   │   ├── services/         # Business logic
│   │   ├── database/         # SQLAlchemy models
│   │   ├── rag/             # LlamaIndex + ChromaDB
│   │   └── monitoring/       # Prometheus metrics
│   ├── tests/
│   ├── requirements.txt
│   └── pyproject.toml
│
├── shared/                    # Code partagé TypeScript/Python
│   ├── types/                # TypeScript interfaces
│   ├── schemas/              # Pydantic models (générés)
│   └── protocol/             # JSON-RPC protocol definitions
│
├── scripts/                  # Scripts utilitaires
│   ├── build/               # Build scripts cross-platform
│   ├── deploy/              # Release scripts
│   └── dev/                 # Dev environment setup
│
├── docs/                    # Documentation
│   ├── api/                # API documentation
│   ├── architecture/       # Diagrams, decisions
│   └── user/              # User guides
│
└── infrastructure/          # CI/CD, monitoring
    ├── github/             # GitHub Actions workflows
    ├── grafana/            # Dashboard definitions
    └── prometheus/         # Alert rules, configs
```

### 7.2 Pré-requis de Développement
```bash
# Développeur frontend
node >= 20.0.0
npm >= 10.0.0
rustc >= 1.75.0
tauri-cli >= 2.0.0

# Développeur backend
python >= 3.11.0
pip >= 23.0.0
uv (optional, mais recommandé)

# Outils communs
git >= 2.40.0
docker (pour tests intégration)
make (pour scripts utilitaires)
```

### 7.3 Setup Environnement de Développement
```bash
# 1. Cloner le projet
git clone https://github.com/your-org/chat_emploi.git
cd chat_emploi

# 2. Setup backend Python
cd backend
python -m venv .venv
source .venv/bin/activate  # ou .venv\Scripts\activate sur Windows
pip install -r requirements-dev.txt
pip install -e .

# 3. Setup frontend
cd ../frontend
npm install

# 4. Setup pre-commit hooks
pre-commit install

# 5. Lancer l'application en dev
npm run tauri dev
```

### 7.4 Build pour Production
```bash
# Build pour plateforme courante
npm run tauri build

# Build spécifique
npm run tauri build -- --target x86_64-pc-windows-msvc
npm run tauri build -- --target x86_64-apple-darwin
npm run tauri build -- --target x86_64-unknown-linux-gnu

# Build universal macOS (ARM + Intel)
npm run tauri build -- --target universal-apple-darwin
```

### 7.5 Maintenance & Mises à Jour

#### 7.5.1 Mise à Jour des Dépendances
```bash
# Backend Python
cd backend
uv pip compile requirements.in -o requirements.txt
uv pip sync requirements.txt

# Frontend Node.js
cd frontend
npm update
npm audit fix

# Rust (Tauri)
cd frontend/src-tauri
cargo update
```

#### 7.5.2 Gestion des Données Utilisateur
```bash
# Backup données utilisateur
# Les données sont stockées dans:
# - macOS: ~/Library/Application Support/com.chatemploi.app/
# - Windows: %APPDATA%\chat_emploi\
# - Linux: ~/.local/share/chat_emploi/

# Script de migration données
python backend/scripts/migrate_data.py --from-version 1.0 --to-version 1.1
```

#### 7.5.3 Dépannage Common
```bash
# Réinitialiser l'application (garder données)
chat-emploi --reset-settings

# Mode debug détaillé
chat-emploi --verbose --log-level=DEBUG

# Désactiver features spécifiques
chat-emploi --disable-monitoring --disable-auto-update

# Exporter données pour support
chat-emploi --export-data /path/to/export.zip
```

---

## 8. ROADMAP TECHNIQUE & ÉVOLUTIONS

### 8.1 Phase 2 (1-2 mois post-MVP)
1. **Fine-tuning local** : Entraîner modèle embedding sur corpus emploi français
2. **Cache distribué** : Partage cache offres entre utilisateurs (P2P local)
3. **Plugins externes** : Support extensions tierces (LinkedIn import, etc.)
4. **Voice interface** : Préparation entretien avec reconnaissance vocale

### 8.2 Phase 3 (3-4 mois)
1. **Mobile companion** : Application mobile synchronisée (React Native)
2. **Collaboration** : Mode conseiller (multi-utilisateurs)
3. **Analytics avancés** : Machine learning pour prédiction succès candidature
4. **Marketplace** : Templates lettres, formations partenaires

### 8.3 Phase 4 (6+ mois)
1. **Modèles locaux** : Intégration Ollama/Mistral pour fonctionnement offline
2. **Blockchain credentials** : Certifications vérifiables sur CV
3. **AR/VR interviews** : Simulations entretiens en réalité virtuelle
4. **Platform as a Service** : Version cloud pour entreprises

---

## 9. ANNEXES TECHNIQUES

### 9.1 Références APIs Externes
- **Gemini API** : https://ai.google.dev/docs
- **France Travail API** : Documentation JSON locale
- **SerpAPI** : https://serpapi.com/dashboard
- **Google Custom Search JSON API** : Alternative à SerpAPI

### 9.2 Bibliothèques Clés
- **Tauri** : https://v2.tauri.app
- **LangGraph** : https://langchain-ai.github.io/langgraph
- **CrewAI** : https://docs.crewai.com
- **LlamaIndex** : https://docs.llamaindex.ai
- **FastAPI** : https://fastapi.tiangolo.com
- **ChromaDB** : https://docs.trychroma.com

### 9.3 Standards & Conventions
- **Code Style** : Black (Python), Prettier (TypeScript), rustfmt (Rust)
- **Git** : Conventional Commits, Semantic Versioning
- **API Design** : JSON-RPC 2.0, OpenAPI 3.0 pour documentation
- **Security** : OWASP ASVS Level 1, RGPD compliance

### 9.4 Contacts & Support
- **Lead Architect** : CTO - architecture@chatemploi.fr
- **DevOps** : infra@chatemploi.fr  
- **Security** : security@chatemploi.fr
- **User Support** : support@chatemploi.fr

---

## 10. NOTES DE VERSION TECHNIQUE

### v1.0.0 (MVP - Initial Release)
**Date cible** : Avril 2026  
**Scope technique** :
- Architecture Tauri + Python sidecar opérationnelle
- Pipeline CV anonymisation → analyse → matching → génération lettre
- Dashboard de suivi candidatures avec métriques
- Monitoring local Prometheus/Grafana
- CI/CD cross-platform automatisé
- Documentation développeur complète

**Critères d'acceptation technique** :
- [ ] Build réussit sur Windows, macOS, Linux
- [ ] Tests unitaires > 80% coverage
- [ ] Tests E2E couvrent flux utilisateur principal
- [ ] Performance : matching < 5s, génération lettre < 10s
- [ ] Sécurité : audit statique code + dépendances
- [ ] Monitoring : métriques exposées + dashboard fonctionnel

---

*Document technique validé le 27 janvier 2026*  
*Propriété intellectuelle de Chat Emploi - Usage interne uniquement*