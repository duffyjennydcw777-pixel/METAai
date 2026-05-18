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

# ═══════════════════════════════════════════════════════════
# PHASE 9: Autonomous Loop
# ═══════════════════════════════════════════════════════════

# Signal Router
SIGNAL_LOG = REPORTS_DIR / "signals" / "routed.json"
SIGNAL_RULES = {
    "cheap_deal": {"threshold_mult": 6, "route_to": "deal_evaluator"},
    "hot_trend": {"threshold_votes": 100, "route_to": "trend_matcher"},
    "high_mrr": {"threshold_mrr": 50000, "route_to": "idea_scorer"},
}

# Deal Evaluator
DEAL_EVALUATIONS = REPORTS_DIR / "signals" / "deal_evaluations.json"
DEAL_MIN_MRR = 5000           # Минимальный MRR для deep-dive
DEAL_MAX_MULTIPLIER = 8       # Только сделки ≤ 8× MRR
DEAL_TOP_N = 10               # Топ-N сделок для оценки

# Trend Matcher
TREND_MATCHES = REPORTS_DIR / "signals" / "trend_matches.json"
TREND_MIN_OVERLAP = 2         # Мин. пересечение слов для матча

# Action Generator
ACTION_QUEUE = REPORTS_DIR / "signals" / "actions.json"
ACTION_LOG = REPORTS_DIR / "signals" / "action_history.json"
MAX_ACTIONS_PER_RUN = 5       # Не больше 5 задач за цикл

# ═══════════════════════════════════════════════════════════
# PHASE 10: Competitor Intelligence
# ═══════════════════════════════════════════════════════════

# Competitor Tracker
COMPETITOR_CACHE = REPORTS_DIR / "competitors" / "tracker.json"
COMPETITORS = {
    "ONYX": [
        {"name": "Outline VPN", "url": "https://getoutline.org"},
        {"name": "Amnezia VPN", "url": "https://amnezia.org"},
        {"name": "Windscribe", "url": "https://windscribe.com"},
    ],
    "Sylectus": [
        {"name": "LoadSmart", "url": "https://loadsmart.com"},
        {"name": "Convoy", "url": "https://convoy.com"},
    ],
}

# Feature Radar
FEATURE_CACHE = REPORTS_DIR / "competitors" / "features.json"

# Pricing Monitor
PRICING_CACHE = REPORTS_DIR / "competitors" / "pricing.json"


# ═══════════════════════════════════════════════════════════
# Phase 12: Meta-Evolution
# ═══════════════════════════════════════════════════════════
EVOLUTION_DIR = REPORTS_DIR / "evolution"

# Knowledge Distiller — агрегирует insights из всех отчётов
KNOWLEDGE_CACHE = EVOLUTION_DIR / "knowledge.json"
KNOWLEDGE_MAX_INSIGHTS = 50

# Portfolio Tracker — отслеживает все наши проекты
PORTFOLIO_CACHE = EVOLUTION_DIR / "portfolio.json"
PORTFOLIO = {
    "ONYX": {
        "type": "VPN SaaS",
        "stage": "growth",
        "mrr": 0,  # Обновляется из реальных данных
        "url": "https://t.me/onyx_vpn_bot",
    },
    "Sylectus": {
        "type": "Logistics TMS",
        "stage": "mvp",
        "mrr": 0,
        "url": "",
    },
    "FreshCut Greens": {
        "type": "Microgreens Farm",
        "stage": "pre-launch",
        "mrr": 0,
        "url": "",
    },
}

# Self-Tuner — самокоррекция параметров
TUNER_CACHE = EVOLUTION_DIR / "tuner.json"
TUNER_METRICS = {
    "signal_noise_ratio": 0.0,   # Сигналы / общее кол-во данных
    "action_completion_rate": 0.0,  # Выполненные задачи / сгенерированные
    "deal_accuracy": 0.0,        # BUY/WATCH точность (manual feedback)
    "scrape_success_rate": 0.0,  # Успешные скрейпы / попытки
}

# Performance Benchmarker
BENCHMARK_CACHE = EVOLUTION_DIR / "benchmarks.json"
BENCHMARK_HISTORY_LIMIT = 30  # Хранить N последних запусков

# ═══════════════════════════════════════════════════════════
# Phase 13: Self-Evolving System (Level 5)
# ═══════════════════════════════════════════════════════════

# LLM Reasoner
LLM_API_KEY_ENV = "OPENROUTER_API_KEY"
LLM_BASE_URL_ENV = "OPENROUTER_BASE_URL"
LLM_MODEL = "anthropic/claude-3.5-haiku"
LLM_MAX_TOKENS = 2000
LLM_TEMPERATURE = 0.3
LLM_TIMEOUT = 30  # секунд

# Agent Generator
AGENT_DRAFTS_DIR = ROOT / "agents" / "drafts"
AGENT_TEMPLATE = '''"""
{emoji} Agent #{number}: {name}
{description}

    python -m agents.{module_name}              # Запуск
    python -m agents.{module_name} --save       # + сохранить
"""

import json
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from agents.config import REPORTS_DIR


def main():
    args = sys.argv[1:]
    save_md = "--save" in args

    print("\\n" + "=" * 60)
    print("  {emoji} {name} — Phase 13 Agent #{number}")
    print("=" * 60)

    # TODO: Agent logic here

    print("\\n" + "=" * 60 + "\\n")


if __name__ == "__main__":
    main()
'''

# Config Evolver
CONFIG_EVOLUTION_LOG = EVOLUTION_DIR / "config_changes.json"
CONFIG_EVOLVER_MAX_CHANGES = 3  # Максимум изменений за раз

# Event Watcher
WATCH_DIRS = [str(REPORTS_DIR), str(ROOT / "agents")]
WATCH_POLL_SESSION = 300      # 5 минут — во время сессии
WATCH_POLL_BACKGROUND = 3600  # 1 час — фоновый режим

# Revenue Tracker (CryptoCloud)
CRYPTOCLOUD_API_KEY_ENV = "CRYPTOCLOUD_API_KEY"
CRYPTOCLOUD_SHOP_ID_ENV = "CRYPTOCLOUD_SHOP_ID"
CRYPTOCLOUD_API_URL = "https://api.cryptocloud.plus/v2"
REVENUE_CACHE = EVOLUTION_DIR / "revenue.json"

# Opportunity Engine
OPPORTUNITY_IDEAS_CACHE = EVOLUTION_DIR / "opportunities.json"
MAX_IDEAS_PER_RUN = 5
IDEA_MIN_SCORE_THRESHOLD = 6.0

# Approval Gate
APPROVAL_LOG = EVOLUTION_DIR / "approvals.json"
APPROVAL_TIMEOUT_HOURS = 24

