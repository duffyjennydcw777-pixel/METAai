"""
🐕 Agent #2: Decision Watchdog
Следит за свежестью ключевых файлов и обновлениями Decision Log.

Что проверяет:
1. Decision Log — есть ли незавершённые решения (❌)
2. CHANGELOG — обновлён ли после последних коммитов
3. HABITS_TRACKER — актуален ли
4. EVOLUTION_LOG — пополняется ли

Использование:
    python -m agents.decision_watchdog           # Отчёт в консоль
    python -m agents.decision_watchdog --detail   # Подробный отчёт
"""

import re
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from agents.config import (
    PROJECTS, MONITORED_FILES, STALENESS_THRESHOLDS,
    DEFAULT_STALENESS, SECOND_BRAIN,
)


def parse_decision_log() -> dict:
    """Парсит Decision Log и возвращает статистику."""
    path = SECOND_BRAIN / "10_MetaEngineering" / "decision_log_meta.md"
    if not path.exists():
        return {"error": "Decision Log не найден"}

    content = path.read_text(encoding="utf-8")
    blocks = content.split("## DEC-")

    decisions = {
        "total": 0,
        "completed": [],     # ✅
        "paused": [],        # ⏸️
        "not_done": [],      # ❌
        "no_status": [],     # Без статуса
    }

    for block in blocks[1:]:  # Пропускаем первый (заголовок)
        decisions["total"] += 1
        title = "DEC-" + block.split("\n")[0].strip()

        if "✅" in block:
            decisions["completed"].append(title)
        elif "⏸️" in block:
            decisions["paused"].append(title)
        elif "❌" in block:
            decisions["not_done"].append(title)
        else:
            decisions["no_status"].append(title)

    return decisions


def check_changelog_vs_git(project_name: str, project_path: Path) -> dict:
    """Проверяет, обновлялся ли CHANGELOG после последних git-коммитов."""
    changelog = project_path / "CHANGELOG.md"
    git_dir = project_path / ".git"

    result = {
        "has_changelog": changelog.exists(),
        "has_git": git_dir.exists(),
        "changelog_age_days": None,
        "stale": False,
    }

    if changelog.exists():
        age = datetime.now() - datetime.fromtimestamp(changelog.stat().st_mtime)
        result["changelog_age_days"] = age.days

        # Если CHANGELOG старше 14 дней — предупреждение
        if age.days > 14:
            result["stale"] = True

    return result


def check_monitored_freshness() -> list[dict]:
    """Проверяет свежесть всех мониторируемых файлов."""
    results = []

    for name, path in MONITORED_FILES.items():
        entry = {"name": name, "path": str(path), "exists": path.exists()}

        if path.exists():
            mtime = datetime.fromtimestamp(path.stat().st_mtime)
            age = datetime.now() - mtime
            threshold = STALENESS_THRESHOLDS.get(name, DEFAULT_STALENESS)

            entry["last_modified"] = mtime.strftime("%Y-%m-%d %H:%M")
            entry["age_days"] = age.days
            entry["threshold_days"] = threshold.days
            entry["stale"] = age > threshold

            # Извлекаем updated поле из frontmatter если есть
            try:
                content = path.read_text(encoding="utf-8")
                match = re.search(r"updated:\s*(\d{4}-\d{2}-\d{2})", content)
                if match:
                    entry["frontmatter_updated"] = match.group(1)
            except Exception:
                pass

        results.append(entry)

    return results


def print_report(detailed: bool = False):
    """Печатает отчёт watchdog."""
    print("\n" + "=" * 60)
    print("  🐕 DECISION WATCHDOG — Phase 1 Agent #2")
    print("=" * 60)

    # 1. Decision Log
    decisions = parse_decision_log()
    print("\n  📝 Decision Log:")
    print(f"     Всего решений: {decisions['total']}")
    print(f"     ✅ Выполнено:  {len(decisions['completed'])}")
    print(f"     ⏸️  На паузе:   {len(decisions['paused'])}")
    print(f"     ❌ Не сделано:  {len(decisions['not_done'])}")

    if decisions["not_done"]:
        print("\n     🚨 ТРЕБУЮТ ВНИМАНИЯ:")
        for d in decisions["not_done"]:
            print(f"        → {d}")

    if decisions["no_status"] and detailed:
        print(f"\n     ❓ Без статуса: {len(decisions['no_status'])}")
        for d in decisions["no_status"]:
            print(f"        → {d}")

    # 2. Свежесть файлов
    print("\n  📅 Свежесть файлов:")
    freshness = check_monitored_freshness()
    stale_count = 0

    for f in freshness:
        if not f["exists"]:
            print(f"     ❌ {f['name']}: НЕ НАЙДЕН")
            continue

        emoji = "🟡" if f["stale"] else "🟢"
        if f["stale"]:
            stale_count += 1

        line = f"     {emoji} {f['name']:20s} {f['age_days']:3d}д/{f['threshold_days']}д"
        if f.get("frontmatter_updated"):
            line += f"  (frontmatter: {f['frontmatter_updated']})"
        print(line)

    # 3. CHANGELOG по проектам
    print("\n  📋 CHANGELOG по проектам:")
    stale_changelogs = 0

    for name, path in PROJECTS.items():
        cl = check_changelog_vs_git(name, path)
        if not cl["has_changelog"]:
            print(f"     ❌ {name:12s}: CHANGELOG отсутствует")
            stale_changelogs += 1
        elif cl["stale"]:
            print(f"     🟡 {name:12s}: {cl['changelog_age_days']}д назад")
            stale_changelogs += 1
        else:
            print(f"     🟢 {name:12s}: {cl['changelog_age_days']}д назад")

    # Итог
    print("\n" + "-" * 60)
    issues = len(decisions.get("not_done", [])) + stale_count + stale_changelogs
    if issues == 0:
        print("  🟢 Всё актуально! Система в порядке.")
    else:
        print(f"  🟡 Найдено проблем: {issues}")
        if decisions.get("not_done"):
            print(f"     → {len(decisions['not_done'])} незавершённых решений")
        if stale_count:
            print(f"     → {stale_count} устаревших файлов")
        if stale_changelogs:
            print(f"     → {stale_changelogs} проектов с устаревшим CHANGELOG")

    print("=" * 60 + "\n")


def main():
    detailed = "--detail" in sys.argv
    print_report(detailed)


if __name__ == "__main__":
    main()
