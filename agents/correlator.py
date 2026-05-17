"""
🔗 Agent #11: Cross-Project Correlator
Находит паттерны и корреляции МЕЖДУ проектами.

Что делает:
1. Парсит все отчёты Phase 1-3
2. Строит корреляционную матрицу проблем
3. Определяет системные vs точечные проблемы
4. Генерирует рекомендации

Использование:
    python -m agents.correlator             # Анализ + вывод
    python -m agents.correlator --save      # + Markdown отчёт
"""

import re
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from agents.config import (
    PROJECTS, REPORTS_DIR, CORRELATION_MIN_PROJECTS,
    HEALTH_CRITICAL_THRESHOLD, HEALTH_WARNING_THRESHOLD,
)


def load_latest_report(prefix: str) -> str | None:
    """Загружает содержимое последнего отчёта по префиксу."""
    reports = sorted(REPORTS_DIR.glob(f"{prefix}*.md"), reverse=True)
    if not reports:
        return None
    return reports[0].read_text(encoding="utf-8", errors="ignore")


def parse_health_data() -> dict[str, int]:
    """Парсит health scores."""
    content = load_latest_report("health_")
    if not content:
        return {}
    scores = {}
    for match in re.finditer(r"## [🟢🟡🔴]\s+(\w+)\s+—\s+(\d+)%", content):
        scores[match.group(1)] = int(match.group(2))
    return scores


def parse_todo_data() -> dict[str, int]:
    """Парсит TODO counts."""
    content = load_latest_report("todos_")
    if not content:
        return {}
    counts = {}
    for match in re.finditer(r"\|\s+(\w+)\s+\|.*\|\s+(\d+)\s+\|$", content, re.MULTILINE):
        counts[match.group(1)] = int(match.group(2))
    return counts


def parse_lock_data() -> dict[str, bool]:
    """Парсит наличие lock-файлов."""
    content = load_latest_report("locks_")
    if not content:
        return {}
    locks = {}
    for match in re.finditer(r"\|\s+(\w+)\s+\|.*\|\s+(✅|❌)", content):
        locks[match.group(1)] = match.group(2) == "✅"
    return locks


def parse_rules_sync() -> dict[str, bool]:
    """Парсит sync status."""
    content = load_latest_report("rules_sync_")
    if not content:
        return {}
    synced = {}
    for match in re.finditer(r"\|\s+(\w+)\s+\|\s+(\d+)\s+\|\s+(\d+)\s+\|\s+(\d+)\s+\|", content):
        name = match.group(1)
        drift = int(match.group(2))
        missing = int(match.group(3))
        synced[name] = (drift == 0 and missing == 0)
    return synced


def find_systemic_issues(
    health: dict, todos: dict, locks: dict, rules: dict
) -> list[dict]:
    """Находит системные проблемы (повторяются в N+ проектах)."""
    issues = []

    # 1. Низкий health score
    low_health = [p for p, s in health.items() if s < HEALTH_WARNING_THRESHOLD]
    if len(low_health) >= CORRELATION_MIN_PROJECTS:
        issues.append({
            "type": "systemic",
            "severity": "🔴",
            "title": f"{len(low_health)}/{len(health)} проектов ниже {HEALTH_WARNING_THRESHOLD}% health",
            "projects": low_health,
            "recommendation": "Провести cleanup sprint: docs, README, tests",
        })

    # 2. Отсутствие lock-файлов
    no_locks = [p for p, has in locks.items() if not has]
    if len(no_locks) >= CORRELATION_MIN_PROJECTS:
        issues.append({
            "type": "systemic",
            "severity": "🟡",
            "title": f"{len(no_locks)}/{len(locks)} проектов без lock-файлов",
            "projects": no_locks,
            "recommendation": "Запустить `conductor --fix-all` или добавить pre-commit hook",
        })

    # 3. Несинхронизированные rules
    unsynced = [p for p, ok in rules.items() if not ok]
    if len(unsynced) >= CORRELATION_MIN_PROJECTS:
        issues.append({
            "type": "systemic",
            "severity": "🟡",
            "title": f"{len(unsynced)}/{len(rules)} проектов с drift в rules",
            "projects": unsynced,
            "recommendation": "Запустить `rule_syncer --fix`",
        })

    # 4. Много TODO маркеров
    high_todos = [p for p, c in todos.items() if c > 10]
    if len(high_todos) >= CORRELATION_MIN_PROJECTS:
        issues.append({
            "type": "systemic",
            "severity": "🟡",
            "title": f"{len(high_todos)}/{len(todos)} проектов с >10 TODO маркеров",
            "projects": high_todos,
            "recommendation": "Запланировать tech debt sprint",
        })

    return issues


def find_project_insights(
    health: dict, todos: dict, locks: dict, rules: dict
) -> list[dict]:
    """Находит точечные проблемы и корреляции."""
    insights = []

    # Сильные проекты (>90% health, 0 TODO, lock OK)
    for name in PROJECTS:
        h = health.get(name, 0)
        t = todos.get(name, 0)
        has_lock = locks.get(name, False)

        if h >= 90 and t <= 3 and has_lock:
            insights.append({
                "type": "positive",
                "severity": "🟢",
                "title": f"{name} — эталонный проект",
                "detail": f"Health {h}%, {t} TODOs, lock ✅",
            })
        elif h < HEALTH_CRITICAL_THRESHOLD:
            insights.append({
                "type": "critical",
                "severity": "🔴",
                "title": f"{name} — критический health ({h}%)",
                "detail": f"{t} TODOs, lock {'✅' if has_lock else '❌'}",
            })

    # Корреляция: проекты с высоким health vs низким
    if health:
        best = max(health, key=health.get)
        worst = min(health, key=health.get)
        if health[best] - health[worst] > 20:
            insights.append({
                "type": "gap",
                "severity": "🟡",
                "title": f"Разрыв health: {best} ({health[best]}%) vs {worst} ({health[worst]}%)",
                "detail": f"Δ = {health[best] - health[worst]}%",
            })

    return insights


def print_console(systemic: list, insights: list, health: dict):
    """Красивый вывод."""
    print("\n" + "=" * 60)
    print("  🔗 CROSS-PROJECT CORRELATOR — Phase 4 Agent #11")
    print("=" * 60)

    if systemic:
        print("\n  📊 СИСТЕМНЫЕ ПРОБЛЕМЫ")
        for issue in systemic:
            print(f"  {issue['severity']} {issue['title']}")
            print(f"      Проекты: {', '.join(issue['projects'])}")
            print(f"      → {issue['recommendation']}")
    else:
        print("\n  ✅ Системных проблем не обнаружено")

    if insights:
        print("\n  🔍 INSIGHTS")
        for ins in insights:
            print(f"  {ins['severity']} {ins['title']}")
            if "detail" in ins:
                print(f"      {ins['detail']}")

    # Матрица
    print("\n  📋 КОРРЕЛЯЦИОННАЯ МАТРИЦА")
    print(f"  {'Проект':12s} Health  TODOs  Lock  Rules")
    print("  " + "-" * 46)
    for name in PROJECTS:
        h = health.get(name, 0)
        print(f"  {name:12s} {h:4d}%   —      —     —")

    print("=" * 60 + "\n")


def generate_report(systemic: list, insights: list, health: dict, todos: dict,
                     locks: dict, rules: dict) -> str:
    """Markdown отчёт."""
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    lines = [
        f"# 🔗 Cross-Project Correlator — {now}",
        "",
    ]

    if systemic:
        lines.append("## 📊 Системные проблемы")
        lines.append("")
        for issue in systemic:
            lines.append(f"### {issue['severity']} {issue['title']}")
            lines.append(f"- Проекты: {', '.join(issue['projects'])}")
            lines.append(f"- Рекомендация: {issue['recommendation']}")
            lines.append("")

    if insights:
        lines.append("## 🔍 Insights")
        lines.append("")
        for ins in insights:
            lines.append(f"- {ins['severity']} **{ins['title']}**"
                          + (f" — {ins['detail']}" if "detail" in ins else ""))
        lines.append("")

    lines.extend([
        "## 📋 Матрица",
        "",
        "| Проект | Health | TODOs | Lock | Rules Sync |",
        "|--------|:------:|:-----:|:----:|:----------:|",
    ])
    for name in PROJECTS:
        h = health.get(name, 0)
        t = todos.get(name, 0)
        l_ok = "✅" if locks.get(name, False) else "❌"
        r_ok = "✅" if rules.get(name, True) else "❌"
        lines.append(f"| {name} | {h}% | {t} | {l_ok} | {r_ok} |")

    return "\n".join(lines)


def main():
    args = sys.argv[1:]
    save_md = "--save" in args or "--md" in args

    health = parse_health_data()
    todos = parse_todo_data()
    locks = parse_lock_data()
    rules = parse_rules_sync()

    systemic = find_systemic_issues(health, todos, locks, rules)
    insights = find_project_insights(health, todos, locks, rules)

    print_console(systemic, insights, health)

    if save_md:
        REPORTS_DIR.mkdir(parents=True, exist_ok=True)
        report = generate_report(systemic, insights, health, todos, locks, rules)
        timestamp = datetime.now().strftime("%Y%m%d")
        path = REPORTS_DIR / f"correlator_{timestamp}.md"
        path.write_text(report, encoding="utf-8")
        print(f"📄 Сохранено: {path}")


if __name__ == "__main__":
    main()
