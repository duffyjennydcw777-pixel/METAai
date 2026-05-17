"""
📊 Agent #10: Obsidian Pulse
Автоматически обновляет Second Brain на основе данных всех агентов.

Что делает:
1. Собирает последние отчёты Phase 1+2+3
2. Обновляет Main_Dashboard.md (таблица здоровья проектов)
3. Обновляет EVOLUTION_LOG.md (weekly summary)
4. --metrics: обновляет BUSINESS_METRICS.md

Использование:
    python -m agents.obsidian_pulse            # Обновить Dashboard
    python -m agents.obsidian_pulse --metrics  # + бизнес-метрики
    python -m agents.obsidian_pulse --save     # + Markdown отчёт
"""

import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from agents.config import PROJECTS, REPORTS_DIR, SECOND_BRAIN


def get_latest_report(prefix: str) -> Path | None:
    """Находит последний отчёт по префиксу."""
    reports = sorted(REPORTS_DIR.glob(f"{prefix}*.md"), reverse=True)
    return reports[0] if reports else None


def parse_health_scores() -> dict[str, int]:
    """Парсит health scores из последнего health report."""
    report = get_latest_report("health_")
    if not report:
        return {}

    content = report.read_text(encoding="utf-8", errors="ignore")
    scores = {}

    # Ищем строки вида "## 🟡 ONYX — 70%"
    for match in re.finditer(r"## [🟢🟡🔴]\s+(\w+)\s+—\s+(\d+)%", content):
        scores[match.group(1)] = int(match.group(2))

    return scores


def get_git_stats() -> dict[str, dict]:
    """Собирает git-статистику по всем проектам."""
    stats = {}
    for name, path in PROJECTS.items():
        if not (path / ".git").exists():
            continue

        try:
            # Коммитов за 30 дней
            result = subprocess.run(
                ["git", "log", "--oneline", "--since=30.days", "--format=%H"],
                capture_output=True, text=True, timeout=10,
                cwd=str(path),
            )
            commit_count = len(result.stdout.strip().split("\n")) if result.stdout.strip() else 0

            # Последний коммит
            result = subprocess.run(
                ["git", "log", "-1", "--format=%cd|%s", "--date=short"],
                capture_output=True, text=True, timeout=10,
                cwd=str(path),
            )
            if result.stdout.strip():
                parts = result.stdout.strip().split("|", 1)
                last_date = parts[0]
                last_msg = parts[1][:50] if len(parts) > 1 else ""
            else:
                last_date = "N/A"
                last_msg = ""

            stats[name] = {
                "commits_30d": commit_count,
                "last_date": last_date,
                "last_msg": last_msg,
            }
        except (subprocess.TimeoutExpired, OSError):
            stats[name] = {"commits_30d": 0, "last_date": "N/A", "last_msg": ""}

    return stats


def parse_compliance_score() -> int | None:
    """Парсит общий compliance score из последнего compliance report."""
    report = get_latest_report("compliance_")
    if not report:
        return None

    content = report.read_text(encoding="utf-8", errors="ignore")
    match = re.search(r"Compliance Score:\s*[🟢🟡🔴]\s*(\d+)%", content)
    return int(match.group(1)) if match else None


def update_dashboard(health_scores: dict, git_stats: dict, compliance: int | None):
    """Обновляет Main_Dashboard.md в Second Brain."""
    dashboard_path = SECOND_BRAIN / "01_Dashboard" / "Main_Dashboard.md"
    now = datetime.now().strftime("%Y-%m-%d %H:%M")

    if not dashboard_path.exists():
        print(f"  ⚠️ Dashboard не найден: {dashboard_path}")
        return

    content = dashboard_path.read_text(encoding="utf-8")

    # Генерируем блок Agent Pulse
    pulse_block = _generate_pulse_block(health_scores, git_stats, compliance, now)

    # Ищем существующий блок Agent Pulse
    pattern = r"(## 🤖 Agent Pulse.*?)(?=\n## |\Z)"
    if re.search(pattern, content, re.DOTALL):
        content = re.sub(pattern, pulse_block, content, flags=re.DOTALL)
    else:
        # Добавляем в конец
        content = content.rstrip() + "\n\n" + pulse_block

    dashboard_path.write_text(content, encoding="utf-8")
    print(f"  ✅ Dashboard обновлён: {dashboard_path}")


def _generate_pulse_block(health_scores: dict, git_stats: dict,
                           compliance: int | None, now: str) -> str:
    """Генерирует блок Agent Pulse для Dashboard."""
    lines = [
        "## 🤖 Agent Pulse",
        "",
        f"> Последнее обновление: {now}",
        "",
        "| Проект | Здоровье | Коммиты (30д) | Последний | Статус |",
        "|--------|:--------:|:-------------:|:---------:|--------|",
    ]

    for name in PROJECTS:
        health = health_scores.get(name, 0)
        health_bar = "█" * (health // 10) + "░" * (10 - health // 10)

        stats = git_stats.get(name, {})
        commits = stats.get("commits_30d", 0)
        last_date = stats.get("last_date", "N/A")

        if health >= 90:
            status = "🟢 Отлично"
        elif health >= 70:
            status = "🟡 Внимание"
        else:
            status = "🔴 Критично"

        lines.append(
            f"| {name} | {health_bar} {health}% | {commits} | {last_date} | {status} |"
        )

    avg = round(sum(health_scores.values()) / len(health_scores)) if health_scores else 0
    lines.extend([
        "",
        f"**Средний Health Score: {avg}%**",
    ])

    if compliance is not None:
        lines.append(f"**Compliance Score: {compliance}%**")

    lines.append("")
    return "\n".join(lines)


def update_evolution_log(health_scores: dict, git_stats: dict):
    """Добавляет запись в EVOLUTION_LOG.md."""
    evo_path = SECOND_BRAIN / "05_Life" / "EVOLUTION_LOG.md"
    if not evo_path.exists():
        print(f"  ⚠️ EVOLUTION_LOG не найден: {evo_path}")
        return

    now = datetime.now()
    today = now.strftime("%Y-%m-%d")

    content = evo_path.read_text(encoding="utf-8")

    # Проверяем, не обновляли ли уже сегодня
    if f"[{today}] — Agent Pulse" in content:
        print("  ⏭️ EVOLUTION_LOG уже обновлён сегодня")
        return

    total_commits = sum(s.get("commits_30d", 0) for s in git_stats.values())
    avg_health = round(sum(health_scores.values()) / len(health_scores)) if health_scores else 0
    active_projects = sum(1 for s in git_stats.values() if s.get("commits_30d", 0) > 0)

    entry = (
        f"\n## [{today}] — Agent Pulse 🤖\n\n"
        f"- Health Score: {avg_health}% (avg across {len(health_scores)} projects)\n"
        f"- Активных проектов: {active_projects}/{len(PROJECTS)}\n"
        f"- Коммитов за 30д: {total_commits}\n"
    )

    # Добавляем после первого "---" (после frontmatter)
    parts = content.split("---", 2)
    if len(parts) >= 3:
        content = parts[0] + "---" + parts[1] + "---" + entry + parts[2]
    else:
        content += entry

    evo_path.write_text(content, encoding="utf-8")
    print("  ✅ EVOLUTION_LOG обновлён")


def print_console(health_scores: dict, git_stats: dict, compliance: int | None):
    """Красивый вывод в консоль."""
    print("\n" + "=" * 60)
    print("  📊 OBSIDIAN PULSE — Phase 3 Agent #10")
    print("=" * 60)

    for name in PROJECTS:
        health = health_scores.get(name, 0)
        stats = git_stats.get(name, {})
        commits = stats.get("commits_30d", 0)
        last = stats.get("last_date", "N/A")

        emoji = "🟢" if health >= 90 else "🟡" if health >= 70 else "🔴"
        print(f"  {emoji} {name:12s}  Health: {health}%  Commits: {commits}  Last: {last}")

    print("-" * 60)
    avg = round(sum(health_scores.values()) / len(health_scores)) if health_scores else 0
    print(f"  Avg Health: {avg}%", end="")
    if compliance is not None:
        print(f" | Compliance: {compliance}%", end="")
    print()
    print("=" * 60 + "\n")


def generate_report(health_scores: dict, git_stats: dict, compliance: int | None) -> str:
    """Генерирует Markdown отчёт."""
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    lines = [
        f"# 📊 Obsidian Pulse Report — {now}",
        "",
        "| Проект | Health | Commits (30d) | Last Commit |",
        "|--------|:------:|:-------------:|:-----------:|",
    ]

    for name in PROJECTS:
        health = health_scores.get(name, 0)
        stats = git_stats.get(name, {})
        lines.append(
            f"| {name} | {health}% | {stats.get('commits_30d', 0)} | {stats.get('last_date', 'N/A')} |"
        )

    avg = round(sum(health_scores.values()) / len(health_scores)) if health_scores else 0
    lines.extend(["", f"**Avg Health: {avg}%**"])
    if compliance is not None:
        lines.append(f"**Compliance: {compliance}%**")

    return "\n".join(lines)


def main():
    args = sys.argv[1:]
    save_md = "--save" in args or "--md" in args

    # Собираем данные
    health_scores = parse_health_scores()
    git_stats = get_git_stats()
    compliance = parse_compliance_score()

    print_console(health_scores, git_stats, compliance)

    # Обновляем Obsidian
    update_dashboard(health_scores, git_stats, compliance)
    update_evolution_log(health_scores, git_stats)

    if save_md:
        REPORTS_DIR.mkdir(parents=True, exist_ok=True)
        report = generate_report(health_scores, git_stats, compliance)
        timestamp = datetime.now().strftime("%Y%m%d")
        path = REPORTS_DIR / f"pulse_{timestamp}.md"
        path.write_text(report, encoding="utf-8")
        print(f"📄 Сохранено: {path}")


if __name__ == "__main__":
    main()
