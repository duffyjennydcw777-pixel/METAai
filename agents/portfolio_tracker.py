"""
💰 Agent #18: Portfolio Tracker
Трекает бизнес-метрики и обновляет BUSINESS_METRICS.md.

    python -m agents.portfolio_tracker          # Обновить
    python -m agents.portfolio_tracker --save   # + отчёт
"""

import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from agents.config import (
    PROJECTS, REPORTS_DIR, BUSINESS_METRICS_FILE,
)


def count_commits_week(project_path):
    try:
        result = subprocess.run(
            ["git", "log", "--oneline", "--since=7.days", "--format=%H"],
            capture_output=True, text=True, timeout=10,
            cwd=str(project_path), encoding="utf-8", errors="replace",
        )
        return len(result.stdout.strip().split("\n")) if result.stdout.strip() else 0
    except (subprocess.TimeoutExpired, OSError):
        return 0


def get_last_commit_date(project_path):
    try:
        result = subprocess.run(
            ["git", "log", "-1", "--format=%ci"],
            capture_output=True, text=True, timeout=10,
            cwd=str(project_path), encoding="utf-8", errors="replace",
        )
        if result.stdout.strip():
            return result.stdout.strip()[:10]
    except (subprocess.TimeoutExpired, OSError):
        pass
    return "—"


def parse_health():
    reports = sorted(REPORTS_DIR.glob("health_*.md"), reverse=True)
    if not reports:
        return {}
    content = reports[0].read_text(encoding="utf-8", errors="ignore")
    scores = {}
    for m in re.finditer(r"## [🟢🟡🔴]\s+(\w+)\s+—\s+(\d+)%", content):
        scores[m.group(1)] = int(m.group(2))
    return scores


def determine_status(health_score, commits):
    if commits == 0:
        return "💤 Idle"
    if health_score >= 90:
        return "🟢 Stable"
    if health_score >= 70:
        return "🟡 Active"
    return "🔴 Critical"


def parse_milestones():
    """Парсит ключевые milestones из DECISIONS.md каждого проекта."""
    milestones = {}
    for name, path in PROJECTS.items():
        decisions_file = path / "DECISIONS.md"
        if not decisions_file.exists():
            continue
        content = decisions_file.read_text(encoding="utf-8", errors="ignore")
        # Считаем количество решений
        count = len(re.findall(r"^##\s+", content, re.MULTILINE))
        milestones[name] = count
    return milestones


def generate_portfolio_block(data):
    """Генерирует блок для BUSINESS_METRICS.md."""
    now = datetime.now()
    week_num = now.isocalendar()[1]

    lines = [
        "",
        f"## 📊 Auto-Generated KPIs (W{week_num})",
        f"_Обновлено: {now.strftime('%Y-%m-%d %H:%M')}_",
        "",
        "| Проект | Commits/W | Health | Status | Last Activity |",
        "|--------|:---------:|:------:|--------|:-------------:|",
    ]

    for entry in data:
        lines.append(
            f"| {entry['name']} | {entry['commits']} | {entry['health']}%"
            f" | {entry['status']} | {entry['last_commit']} |"
        )

    lines.append("")
    return "\n".join(lines)


def update_business_metrics(block):
    """Обновляет BUSINESS_METRICS.md, заменяя предыдущий блок."""
    if not BUSINESS_METRICS_FILE.exists():
        BUSINESS_METRICS_FILE.parent.mkdir(parents=True, exist_ok=True)
        BUSINESS_METRICS_FILE.write_text(
            "# 💰 Business Metrics\n" + block, encoding="utf-8"
        )
        return True

    content = BUSINESS_METRICS_FILE.read_text(encoding="utf-8")

    # Удаляем предыдущий auto-generated блок
    pattern = r"\n## 📊 Auto-Generated KPIs.*?(?=\n## |\Z)"
    cleaned = re.sub(pattern, "", content, flags=re.DOTALL)

    # Добавляем новый
    updated = cleaned.rstrip() + "\n" + block
    BUSINESS_METRICS_FILE.write_text(updated, encoding="utf-8")
    return True


def main():
    args = sys.argv[1:]
    save_md = "--save" in args or "--md" in args

    health = parse_health()
    _ = parse_milestones()  # Reserved for future use

    data = []
    for name, path in PROJECTS.items():
        if not (path / ".git").exists():
            continue
        commits = count_commits_week(path)
        h = health.get(name, 0)
        status = determine_status(h, commits)
        last_commit = get_last_commit_date(path)

        data.append({
            "name": name,
            "commits": commits,
            "health": h,
            "status": status,
            "last_commit": last_commit,
        })

    block = generate_portfolio_block(data)

    print("\n" + "=" * 60)
    print("  💰 PORTFOLIO TRACKER — Phase 5 Agent #18")
    print("=" * 60)

    for entry in data:
        print(f"  {entry['status']:15s} {entry['name']:12s}"
              f" {entry['health']}%  {entry['commits']} commits/w")

    # Update BUSINESS_METRICS.md
    if update_business_metrics(block):
        print("\n  ✅ BUSINESS_METRICS.md обновлён")
        print(f"  📄 {BUSINESS_METRICS_FILE}")

    if save_md:
        REPORTS_DIR.mkdir(parents=True, exist_ok=True)
        path = REPORTS_DIR / f"portfolio_{datetime.now().strftime('%Y%m%d')}.md"
        path.write_text(block, encoding="utf-8")
        print(f"  📄 Reports: {path}")

    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
