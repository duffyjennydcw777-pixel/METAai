"""
METAai Agents — Конфигурация
Единый источник правды для всех агентов (Phase 1 + Phase 2).
"""
from pathlib import Path
from datetime import timedelta

# ═══════════════════════════════════════════════════════════
# ПУТИ
# ═══════════════════════════════════════════════════════════

SECOND_BRAIN = Path(r"C:\Users\Gigabyte\Second_Brain")
DEV_ROOT = Path(r"C:\Dev")

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
    "playbooks.md",       # Навигация по стратегическим инструментам
    "habits.md",          # Энергетические паттерны создателя
    "code_complexity.md", # 3-уровневый QA
    "roi_filter.md",      # Фильтр решений через ROI
    "ai_workflow.md",     # Pre-Mortem, 3 сценария, Action Gate
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
# ПРАВИЛА СИНХРОНИЗАЦИИ RULES
# ═══════════════════════════════════════════════════════════

# Эталонные файлы (мастер-копии)
MASTER_RULES = {
    "playbooks.md":       DEV_ROOT / "FreshCut" / ".agent" / "rules" / "playbooks.md",
    "habits.md":          DEV_ROOT / "FreshCut" / ".agent" / "rules" / "habits.md",
    "code_complexity.md": DEV_ROOT / "ONYX" / ".agent" / "rules" / "code_complexity.md",
    "roi_filter.md":      DEV_ROOT / "FreshCut" / ".agent" / "rules" / "roi_filter.md",
    "ai_workflow.md":     DEV_ROOT / "FreshCut" / ".agent" / "rules" / "ai_workflow.md",
}

# ═══════════════════════════════════════════════════════════
# ОТЧЁТЫ
# ═══════════════════════════════════════════════════════════

REPORTS_DIR = DEV_ROOT / "METAai" / "agents" / "reports"
