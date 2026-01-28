"""Monitoring metrics for Chat Emploi backend."""

from prometheus_client import Counter, Gauge, Histogram

# ============================================================================
# Métriques d'usage (Counters)
# ============================================================================

CV_PROCESSED = Counter(
    "cv_processed_total",
    "Total CVs processed",
    ["anonymization_method"],  # 'manual', 'auto', 'hybrid'
)

OFFERS_FETCHED = Counter(
    "offers_fetched_total",
    "Total job offers fetched",
    ["source"],  # 'france_travail', 'web_scraped', 'manual'
)

LETTERS_GENERATED = Counter(
    "letters_generated_total",
    "Total cover letters generated",
    ["tone"],  # 'professional', 'enthusiastic', 'formal'
)

# ============================================================================
# Métriques de performance (Histograms)
# ============================================================================

API_LATENCY = Histogram(
    "api_latency_seconds",
    "API call latency",
    ["endpoint", "method", "status_code"],
    buckets=[0.01, 0.05, 0.1, 0.5, 1.0, 2.0, 5.0, 10.0, float("inf")],
)

RAG_MATCHING_TIME = Histogram(
    "rag_matching_seconds",
    "RAG matching time",
    buckets=[0.1, 0.5, 1.0, 2.0, 3.0, 5.0, 10.0, float("inf")],
)

LLM_GENERATION_TIME = Histogram(
    "llm_generation_seconds",
    "LLM generation time",
    ["model", "task"],  # 'gemini-pro', 'gemini-embedding', 'letter', 'analysis'
    buckets=[0.5, 1.0, 2.0, 5.0, 10.0, 30.0, 60.0, float("inf")],
)

# ============================================================================
# Métriques de qualité (Gauges)
# ============================================================================

MATCH_SCORE = Gauge(
    "match_score_current", "Current match score for latest search", ["search_id"]
)

LETTER_QUALITY = Gauge(
    "letter_quality_score",
    "Quality score of generated letters",
    ["document_type"],  # 'cover_letter', 'interview_prep', 'cv_analysis'
)

USER_SATISFACTION = Gauge(
    "user_satisfaction_score",
    "User feedback rating",
    ["feedback_type"],  # 'offer_match', 'letter_quality', 'agent_response'
)

# ============================================================================
# Métriques système (Gauges)
# ============================================================================

MEMORY_USAGE = Gauge(
    "memory_usage_bytes",
    "Memory usage in bytes",
    ["type"],  # 'rss', 'vms', 'shared'
)

CPU_USAGE = Gauge(
    "cpu_usage_percent",
    "CPU usage percentage",
    ["core"],  # 'total', 'core_0', 'core_1', etc.
)

DISK_USAGE = Gauge(
    "disk_usage_bytes",
    "Disk usage in bytes",
    ["path"],  # 'data', 'cache', 'logs'
)

# ============================================================================
# Utilitaires
# ============================================================================


def record_api_latency(
    endpoint: str, method: str, status_code: int, duration: float
) -> None:
    """Enregistre la latence d'un appel API."""
    API_LATENCY.labels(
        endpoint=endpoint, method=method, status_code=status_code
    ).observe(duration)


def record_llm_generation(model: str, task: str, duration: float) -> None:
    """Enregistre le temps de génération LLM."""
    LLM_GENERATION_TIME.labels(model=model, task=task).observe(duration)


def increment_cv_processed(anonymization_method: str = "auto") -> None:
    """Incrémente le compteur de CV traités."""
    CV_PROCESSED.labels(anonymization_method=anonymization_method).inc()


def increment_offers_fetched(source: str) -> None:
    """Incrémente le compteur d'offres récupérées."""
    OFFERS_FETCHED.labels(source=source).inc()


def increment_letters_generated(tone: str = "professional") -> None:
    """Incrémente le compteur de lettres générées."""
    LETTERS_GENERATED.labels(tone=tone).inc()


def set_match_score(search_id: str, score: float) -> None:
    """Définit le score de matching pour une recherche."""
    MATCH_SCORE.labels(search_id=search_id).set(score)


def set_letter_quality(document_type: str, score: float) -> None:
    """Définit le score de qualité pour un document."""
    LETTER_QUALITY.labels(document_type=document_type).set(score)


def set_user_satisfaction(feedback_type: str, score: float) -> None:
    """Définit le score de satisfaction utilisateur."""
    USER_SATISFACTION.labels(feedback_type=feedback_type).set(score)


def update_system_metrics() -> None:
    """Met à jour les métriques système (mémoire, CPU, disque)."""
    import os

    import psutil

    # Mémoire
    process = psutil.Process(os.getpid())
    mem_info = process.memory_info()
    MEMORY_USAGE.labels(type="rss").set(mem_info.rss)
    MEMORY_USAGE.labels(type="vms").set(mem_info.vms)

    # CPU
    cpu_percent = psutil.cpu_percent(interval=0.1)
    CPU_USAGE.labels(core="total").set(cpu_percent)

    # Disque
    data_dir = os.path.expanduser("~/.chat_emploi/data")
    if os.path.exists(data_dir):
        disk_usage = psutil.disk_usage(data_dir)
        DISK_USAGE.labels(path="data").set(disk_usage.used)
