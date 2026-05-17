"""
🗂️ Agent #16: Sprint Planner
Генерирует Sprint Backlog из данных всех агентов.

    python -m agents.sprint_planner           # Генерация
    python -m agents.sprint_planner --save    # + в reports
"""

import re
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from agents.config import (
    REPORTS_DIR, SPRINT_DIR, SPRINT_EFFORT,
    HEALTH_WARNING_THRESHOLD,
)


def parse_health():
    reports = sorted(REPORTS_DIR.glob("health_*.md"), reverse=True)
    if not reports:
        return {}
    content = reports[0].read_text(encoding="utf-8", errors="ignore")
    scores = {}
    for m in re.finditer(r"## [🟢🟡🔴]\s+(\w+)\s+—\s+(\d+)%", content):
        scores[m.group(1)] = int(m.group(2))
    return scores


def parse_todos():
    reports = sorted(REPORTS_DIR.glob("todos_*.md"), reverse=True)
    if not reports:
        return {}
    content = reports[0].read_text(encoding="utf-8", errors="ignore")
    counts = {}
    for m in re.finditer(r"\|\s+(\w+)\s+\|.*\|\s+(\d+)\s+\|$", content, re.MULTILINE):
        counts[m.group(1)] = int(m.group(2))
    return counts


def parse_unfulfilled_decisions():
    """Парсит невыполненные решения из Decision Watchdog."""
    reports = sorted(REPORTS_DIR.glob("watchdog_*.md"), reverse=True)
    if not reports:
        return []
    content = reports[0].read_text(encoding="utf-8", errors="ignore")
    decisions = []
    for m in re.finditer(r"❌\s+(.+)", content):
        decisions.append(m.group(1).strip())
    return decisions


def estimate_effort(task_type, value=0):
    """Оценивает effort по типу задачи."""
    if task_type == "health" and value < 70:
        return "L"
    if task_type == "health":
        return "M"
    if task_type == "decision":
        return "L"
    if task_type == "todo" and value > 10:
        return "M"
    return "S"


def generate_sprint(health, todos, decisions):
    """Генерирует sprint backlog."""
    now = datetime.now()
    # Следующая неделя
    week_num = now.isocalendar()[1] + 1

    p0 = []  # Critical
    p1 = []  # Important
    p2 = []  # Nice to have

    # Health-based tasks
    for name, score in health.items():
        if score < 70:
            effort = estimate_effort("health", score)
            p0.append(f"- [ ] {name}: health {score}% → 85% [{effort}]"
                       " — добавить README, docs/, tests/")
        elif score < HEALTH_WARNING_THRESHOLD:
            effort = estimate_effort("health", score)
            p1.append(f"- [ ] {name}: health {score}% → 90% [{effort}]"
                       " — cleanup + documentation")

    # Unfulfilled decisions
    for d in decisions:
        p0.append(f"- [ ] {d} [L] — решение не реализовано")

    # TODO-based tasks
    for name, count in sorted(todos.items(), key=lambda x: -x[1]):
        if count > 10:
            effort = estimate_effort("todo", count)
            p1.append(f"- [ ] {name}: {count} TODO markers [{effort}]"
                       " — tech debt sprint")
        elif count > 0:
            p2.append(f"- [ ] {name}: {count} TODO markers [S]"
                       " — minor cleanup")

    # Stable projects → optimize
    for name, score in health.items():
        if score >= 90 and score < 100:
            p2.append(f"- [ ] {name}: {score}% → 100% [S]"
                       " — final polish")

    lines = [
        "---",
        f"created: {now.strftime('%Y-%m-%d %H:%M')}",
        "tags: [auto-generated, sprint, agents]",
        "---",
        "",
        f"# 🗂️ Sprint W{week_num} — Auto-Generated",
        "",
        f"Период: неделя {week_num}, {now.year}",
        "",
    ]

    if p0:
        lines.extend(["## 🔴 P0 (Critical)", ""])
        lines.extend(p0)
        lines.append("")

    if p1:
        lines.extend(["## 🟡 P1 (Important)", ""])
        lines.extend(p1)
        lines.append("")

    if p2:
        lines.extend(["## 🟢 P2 (Nice to have)", ""])
        lines.extend(p2)
        lines.append("")

    # Effort legend
    lines.extend([
        "---",
        "## Effort Legend",
        "",
    ])
    for code, desc in SPRINT_EFFORT.items():
        lines.append(f"- **[{code}]** — {desc}")

    return "\n".join(lines), week_num


def main():
    args = sys.argv[1:]
    save_md = "--save" in args or "--md" in args

    health = parse_health()
    todos = parse_todos()
    decisions = parse_unfulfilled_decisions()

    sprint_content, week_num = generate_sprint(health, todos, decisions)

    # Сохраняем в Obsidian
    SPRINT_DIR.mkdir(parents=True, exist_ok=True)
    sprint_path = SPRINT_DIR / f"Sprint_W{week_num}.md"
    sprint_path.write_text(sprint_content, encoding="utf-8")

    print("\n" + "=" * 60)
    print("  🗂️ SPRINT PLANNER — Phase 5 Agent #16")
    print("=" * 60)
    print(f"  📄 Obsidian: {sprint_path}")

    task_count = sprint_content.count("- [ ]")
    print(f"  📋 Задач: {task_count}")

    if save_md:
        REPORTS_DIR.mkdir(parents=True, exist_ok=True)
        path = REPORTS_DIR / f"sprint_{datetime.now().strftime('%Y%m%d')}.md"
        path.write_text(sprint_content, encoding="utf-8")
        print(f"  📄 Reports: {path}")

    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
