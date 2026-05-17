"""
📬 Agent #14: Weekly Digest
Генерирует еженедельный стратегический отчёт в Second Brain.

    python -m agents.weekly_digest            # Генерация
    python -m agents.weekly_digest --save     # + в reports
"""

import re
import subprocess
import sys
from datetime import datetime, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from agents.config import PROJECTS, REPORTS_DIR, DIGEST_DIR, HISTORY_FILE

import json


def get_week_reports(prefix: str, days: int = 7) -> list[Path]:
    """Находит отчёты за последние N дней."""
    cutoff = datetime.now() - timedelta(days=days)
    result = []
    for p in REPORTS_DIR.glob(f"{prefix}*.md"):
        # Парсим дату из имени файла: prefix_YYYYMMDD.md
        try:
            date_str = p.stem.split("_")[-1]
            date = datetime.strptime(date_str, "%Y%m%d")
            if date >= cutoff:
                result.append(p)
        except ValueError:
            continue
    return sorted(result)


def count_weekly_commits() -> dict[str, int]:
    """Считает коммиты за 7 дней по всем проектам."""
    commits = {}
    for name, path in PROJECTS.items():
        if not (path / ".git").exists():
            commits[name] = 0
            continue
        try:
            result = subprocess.run(
                ["git", "log", "--oneline", "--since=7.days", "--format=%H"],
                capture_output=True, text=True, timeout=10,
                cwd=str(path), encoding="utf-8", errors="replace",
            )
            count = len(result.stdout.strip().split("\n")) if result.stdout.strip() else 0
            commits[name] = count
        except (subprocess.TimeoutExpired, OSError):
            commits[name] = 0
    return commits


def get_health_delta() -> dict[str, dict]:
    """Считает дельту health за неделю из history.json."""
    if not HISTORY_FILE.exists():
        return {}
    try:
        history = json.loads(HISTORY_FILE.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}

    dates = sorted(history.keys())
    if len(dates) < 2:
        return {}

    latest = history[dates[-1]]
    week_ago_date = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")

    # Найти ближайшую дату к неделе назад
    older = {}
    for d in dates:
        if d <= week_ago_date:
            older = history[d]

    if not older:
        older = history[dates[0]]

    deltas = {}
    for project in latest:
        cur = latest[project]
        prev = older.get(project, cur)
        deltas[project] = {"current": cur, "previous": prev, "delta": cur - prev}

    return deltas


def parse_todo_count() -> int:
    """Считает текущее количество TODO."""
    reports = sorted(REPORTS_DIR.glob("todos_*.md"), reverse=True)
    if not reports:
        return 0
    content = reports[0].read_text(encoding="utf-8", errors="ignore")
    match = re.search(r"Всего маркеров:\s*\*\*(\d+)\*\*", content)
    return int(match.group(1)) if match else 0


def generate_digest() -> str:
    """Генерирует Weekly Digest."""
    now = datetime.now()
    week_num = now.isocalendar()[1]
    year = now.year

    commits = count_weekly_commits()
    total_commits = sum(commits.values())
    deltas = get_health_delta()
    todo_count = parse_todo_count()

    avg_health = 0
    health_delta = 0
    if deltas:
        avg_health = round(sum(d["current"] for d in deltas.values()) / len(deltas))
        health_delta = round(sum(d["delta"] for d in deltas.values()) / len(deltas))

    lines = [
        "---",
        f"created: {now.strftime('%Y-%m-%d %H:%M')}",
        "tags: [auto-generated, weekly-digest, agents]",
        "---",
        "",
        f"# 📬 Weekly Digest — {year}-W{week_num:02d}",
        "",
        "## 📊 KPI",
        "",
        "| Метрика | Значение | Δ |",
        "|---------|:--------:|:-:|",
        f"| Коммиты | {total_commits} | — |",
        f"| Avg Health | {avg_health}% | {health_delta:+d}% |",
        f"| TODOs | {todo_count} | — |",
        f"| Активных проектов | {sum(1 for c in commits.values() if c > 0)}/{len(commits)} | — |",
        "",
    ]

    # По проектам
    lines.extend(["## 📋 По проектам", ""])
    for name in PROJECTS:
        c = commits.get(name, 0)
        d = deltas.get(name, {})
        health = d.get("current", 0)
        delta = d.get("delta", 0)
        delta_str = f" ({delta:+d}%)" if delta != 0 else ""

        if c == 0:
            emoji = "💤"
        elif health >= 90:
            emoji = "🟢"
        else:
            emoji = "🟡"

        lines.append(f"- {emoji} **{name}**: {c} commits, health {health}%{delta_str}")

    # Достижения
    lines.extend(["", "## 🏆 Достижения", ""])

    achievements = []
    for name, c in commits.items():
        if c >= 10:
            achievements.append(f"- {name}: {c} коммитов — активная разработка")
    for name, d in deltas.items():
        if d.get("delta", 0) > 5:
            achievements.append(f"- {name}: health +{d['delta']}%")
    if not achievements:
        achievements.append("- Стабильная неделя — без крупных изменений")
    lines.extend(achievements)

    # Action items
    lines.extend(["", "## ⚡ Action Items", ""])
    for name, d in deltas.items():
        if d.get("current", 100) < 85:
            lines.append(f"- [ ] {name}: health {d['current']}% → target 85%")
    if todo_count > 20:
        lines.append(f"- [ ] Tech debt sprint: {todo_count} TODO маркеров")

    lines.append("")
    return "\n".join(lines)


def main():
    args = sys.argv[1:]
    save_md = "--save" in args or "--md" in args

    digest = generate_digest()

    # Сохраняем в Obsidian
    now = datetime.now()
    week_num = now.isocalendar()[1]
    year = now.year
    filename = f"Weekly_Digest_{year}-W{week_num:02d}.md"

    DIGEST_DIR.mkdir(parents=True, exist_ok=True)
    digest_path = DIGEST_DIR / filename
    digest_path.write_text(digest, encoding="utf-8")

    print("\n" + "=" * 60)
    print("  📬 WEEKLY DIGEST — Phase 4 Agent #14")
    print("=" * 60)
    print(f"  📄 Obsidian: {digest_path}")

    if save_md:
        REPORTS_DIR.mkdir(parents=True, exist_ok=True)
        path = REPORTS_DIR / f"digest_{now.strftime('%Y%m%d')}.md"
        path.write_text(digest, encoding="utf-8")
        print(f"  📄 Reports: {path}")

    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
