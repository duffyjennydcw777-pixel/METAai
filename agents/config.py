"""
METAai Agents — Конфигурация
Единый источник правды для всех агентов (Phase 1 + Phase 2 + Phase 3).
"""
from pathlib import Path
from datetime import timedelta

# ═══════════════════════════════════════════════════════════
# ПУТИ
# ═══════════════════════════════════════════════════════════

SECOND_BRAIN = Path(r"C:\Users\Gigabyte\Second_Brain")
DEV_ROOT = Path(r"C:\Dev")
ROOT = DEV_ROOT / "METAai"

# Все активные проекты (добавляй новые сюда)
PROJECTS = {
    "ONYX":      DEV_ROOT / "ONYX",
    "Sylectus":  DEV_ROOT / "Sylectus",
    "FreshCut":  DEV_ROOT / "FreshCut",
    "METAai":    DEV_ROOT / "METAai",
    "AmazonBOT": DEV_ROOT / "AmazonBOT",
}

# Проекты в планировании (не проверяем на compliance)
PROJECTS_PLANNING = {
    "OMI": DEV_ROOT / "OMI",
}

# ═══════════════════════════════════════════════════════════
# ОБЯЗАТЕЛЬНЫЕ ФАЙЛЫ В .agent/rules/
# ═══════════════════════════════════════════════════════════

REQUIRED_RULES = [
    "playbooks.md",         # Навигация по стратегическим инструментам
    "habits.md",            # Энергетические паттерны создателя
    "CODE_COMPLEXITY.md",   # 3-уровневый QA (uppercase в проектах)
    "roi_filter.md",        # Фильтр решений через ROI
    "ai_workflow.md",       # Pre-Mortem, 3 сценария, Action Gate
]

# Опциональные (рекомендуемые) rules
RECOMMENDED_RULES = [
    "project_rules.md",   # Проектные правила
    "CONVENTIONS.md",     # Кодовые конвенции
]

# ═══════════════════════════════════════════════════════════
# ОБЯЗАТЕЛЬНАЯ СТРУКТУРА ПРОЕКТА
# ═══════════════════════════════════════════════════════════

REQUIRED_STRUCTURE = {
    ".agent/rules/":    "Папка AI-правил",
    "CHANGELOG.md":     "Журнал изменений",
}

# Рекомендуемая (не обязательная) структура
RECOMMENDED_STRUCTURE = {
    "docs/":            "Документация",
    "README.md":        "Описание проекта",
    ".gitignore":       "Git ignore",
}

# ═══════════════════════════════════════════════════════════
# ФАЙЛЫ SECOND BRAIN ДЛЯ МОНИТОРИНГА СВЕЖЕСТИ
# ═══════════════════════════════════════════════════════════

MONITORED_FILES = {
    "Decision Log":     SECOND_BRAIN / "10_MetaEngineering" / "decision_log_meta.md",
    "HABITS_TRACKER":   SECOND_BRAIN / "05_Life" / "HABITS_TRACKER.md",
    "EVOLUTION_LOG":    SECOND_BRAIN / "05_Life" / "EVOLUTION_LOG.md",
    "BUSINESS_METRICS": SECOND_BRAIN / "06_Business" / "BUSINESS_METRICS.md",
    "Main Dashboard":   SECOND_BRAIN / "01_Dashboard" / "Main_Dashboard.md",
    "Meta Roadmap":     SECOND_BRAIN / "04_Architecture" / "Meta_Engineering_Roadmap.md",
}

# Максимальный возраст файла до предупреждения
STALENESS_THRESHOLDS = {
    "Decision Log":     timedelta(days=14),    # Решения принимаются часто
    "HABITS_TRACKER":   timedelta(days=30),    # Обновлять раз в месяц
    "EVOLUTION_LOG":    timedelta(days=7),     # Должен пополняться еженедельно
    "BUSINESS_METRICS": timedelta(days=14),    # Метрики актуальны 2 недели
    "Main Dashboard":   timedelta(days=14),
    "Meta Roadmap":     timedelta(days=30),
}

# Дефолтный порог для файлов без явного threshold
DEFAULT_STALENESS = timedelta(days=30)

# ═══════════════════════════════════════════════════════════
# ПРАВИЛА СИНХРОНИЗАЦИИ RULES (Phase 3: Rule Syncer)
# ═══════════════════════════════════════════════════════════

# Источник мастер-копий — METAai
MASTER_RULES_SOURCE = DEV_ROOT / "METAai" / ".agent" / "rules"

# Глобальные rules — синхронизируются во ВСЕ проекты
GLOBAL_RULES = [
    "GLOBAL.md",
    "MODES.md",
    "MAKER_PROFILE.md",
    "CONVENTIONS.md",
    "CODE_COMPLEXITY.md",
    "habits.md",
    "playbooks.md",
    "roi_filter.md",
    "ai_workflow.md",
]

# Старый формат для обратной совместимости (Compliance Checker)
MASTER_RULES = {
    rule: MASTER_RULES_SOURCE / rule
    for rule in GLOBAL_RULES
    if (MASTER_RULES_SOURCE / rule).exists()
}

# Файлы, которые Rule Syncer НЕ трогает (уникальны для каждого проекта)
PROJECT_SPECIFIC_RULES = [
    "PROJECT.md",
    "ODAF.md",
    "freshcut.md",
    "onyx.md",
    "sylectus.md",
    "amazonbot.md",
]

# ═══════════════════════════════════════════════════════════
# TODO HARVESTER (Phase 3)
# ═══════════════════════════════════════════════════════════

# Паттерны для поиска техдолга
TODO_PATTERNS = ["TODO", "FIXME", "HACK", "XXX"]

# Приоритет (чем выше индекс, тем критичнее)
TODO_PRIORITY = {"XXX": 0, "TODO": 1, "HACK": 2, "FIXME": 3}

# Файлы/папки исключённые из поиска TODO
TODO_EXCLUDE_DIRS = [
    ".git", ".venv", "venv", "node_modules", "__pycache__",
    ".agent", "reports", "dist", "build", ".shared",
]

TODO_EXCLUDE_EXTENSIONS = [
    ".pyc", ".pyo", ".exe", ".dll", ".so", ".whl",
    ".zip", ".tar", ".gz", ".pdf", ".docx", ".xlsx",
    ".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp",
    ".lock", ".map",
]

# ═══════════════════════════════════════════════════════════
# ОТЧЁТЫ
# ═══════════════════════════════════════════════════════════

REPORTS_DIR = DEV_ROOT / "METAai" / "agents" / "reports"

# ═══════════════════════════════════════════════════════════
# PHASE 4: Intelligence Layer
# ═══════════════════════════════════════════════════════════

# Drift Predictor: история health scores
HISTORY_FILE = REPORTS_DIR / "history.json"

# Auto-Committer: whitelist файлов, разрешённых для авто-коммита
AUTO_COMMIT_WHITELIST = [
    ".agent/rules/*.md",
    "requirements.lock",
    "package-lock.json",
    "CHANGELOG.md",
    "DECISIONS.md",
    "EXPERIMENTS.md",
    "REFLEXION_LOG.md",
    "SOLUTION_PATTERNS.md",
]

# Weekly Digest: куда сохранять
DIGEST_DIR = SECOND_BRAIN / "01_Dashboard"

# Correlator: пороги
CORRELATION_MIN_PROJECTS = 2  # Мин. проектов для "системной" проблемы
HEALTH_CRITICAL_THRESHOLD = 70  # Ниже — критично
HEALTH_WARNING_THRESHOLD = 85  # Ниже — предупреждение
TREND_ALERT_DAYS = 3  # Дней подряд снижения для алерта

# ═══════════════════════════════════════════════════════════
# PHASE 5: Outreach
# ═══════════════════════════════════════════════════════════

# Telegram Reporter
TELEGRAM_BOT_TOKEN_ENV = "METAAI_TELEGRAM_BOT_TOKEN"
TELEGRAM_CHAT_ID_ENV = "METAAI_TELEGRAM_CHAT_ID"

# Sprint Planner
SPRINT_DIR = SECOND_BRAIN / "04_Architecture"
SPRINT_EFFORT = {"S": "< 1 час", "M": "1-4 часа", "L": "4+ часов"}

# Portfolio Tracker
BUSINESS_METRICS_FILE = SECOND_BRAIN / "06_Business" / "BUSINESS_METRICS.md"

# ═══════════════════════════════════════════════════════════
# PHASE 6: Mastery
# ═══════════════════════════════════════════════════════════

# Git Analytics
GIT_STALE_BRANCH_DAYS = 30  # Ветки старше N дней = stale

# Cost Monitor
COST_LOG_FILE = REPORTS_DIR / "costs.json"
COST_ALERT_DAILY = 1.0  # $ в день — порог алерта

# Release Manager
RELEASE_LOG = ROOT / "RELEASES.md"

# Knowledge Distiller
KNOWLEDGE_DIR = SECOND_BRAIN / "03_Knowledge" / "METAai"

# ═══════════════════════════════════════════════════════════
# PHASE 7: Growth
# ═══════════════════════════════════════════════════════════

# Market Scanner
TRUSTMRR_CACHE = REPORTS_DIR / "trustmrr_cache.json"
MARKET_SCAN_FILE = REPORTS_DIR / "market_scan.md"
GROWTH_THRESHOLD_MOM = 20  # % MoM growth = "interesting"
MRR_MIN_SIGNAL = 5000  # Только MRR > $5k = реальный сигнал

# Idea Scorer
IDEA_LOG = SECOND_BRAIN / "06_Business" / "IDEAS_SCORED.md"
IDEA_WEIGHTS = {
    "market_size": 0.25,
    "competition": 0.20,
    "tech_fit": 0.25,
    "time_to_mvp": 0.15,
    "revenue_potential": 0.15,
}

# Revenue Forecaster
REVENUE_FORECASTS = REPORTS_DIR / "revenue_forecasts.md"
COMPARABLE_MRR_BANDS = [
    (0, 1000, "Pre-Revenue"),
    (1000, 10000, "Early Traction"),
    (10000, 50000, "Growth"),
    (50000, 200000, "Scale"),
    (200000, float("inf"), "Enterprise"),
]

# Opportunity Radar
OPPORTUNITY_FILE = REPORTS_DIR / "opportunities.md"
MAX_MULTIPLIER_BUY = 12  # Ниже 12× MRR = потенциальная сделка
MIN_MRR_ACQUISITION = 3000  # Минимальный MRR для рассмотрения

# ═══════════════════════════════════════════════════════════
# PHASE 8: Intelligence Feeds
# ═══════════════════════════════════════════════════════════

# TrustMRR Scraper
TRUSTMRR_URL = "https://trustmrr.com"
TRUSTMRR_FEED_CACHE = REPORTS_DIR / "feeds" / "trustmrr.json"

# Acquire Scanner
ACQUIRE_URL = "https://acquire.com"
ACQUIRE_FEED_CACHE = REPORTS_DIR / "feeds" / "acquire.json"

# ProductHunt Tracker
PH_URL = "https://www.producthunt.com"
PH_FEED_CACHE = REPORTS_DIR / "feeds" / "producthunt.json"

# Feed Aggregator
AGGREGATED_FEED = REPORTS_DIR / "feeds" / "aggregated.md"
FEED_HISTORY = REPORTS_DIR / "feeds" / "history.json"

# Rate limiting
SCRAPE_DELAY_SECONDS = 2  # Пауза между запросами
SCRAPE_USER_AGENT = "METAai-Intelligence/1.0 (market-research)"
