"""
📋 Agent #5: Changelog Enforcer (Phase 2)
Гарантирует, что CHANGELOG обновляется при значимых изменениях.

Что делает:
1. Сканирует последние N коммитов каждого проекта
2. Находит "крупные" коммиты (5+ файлов изменено)
3. Проверяет, есть ли соответствующая запись в CHANGELOG.md
4. Генерирует отчёт о пропущенных записях

Использование:
    python -m agents.changelog_enforcer              # Все проекты
    python -m agents.changelog_enforcer --fix        # Предложить шаблоны
    python -m agents.changelog_enforcer --days 14    # За 14 дней
"""

import subprocess
import sys
import re
from datetime import datetime, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from agents.config import PROJECTS


def get_significant_commits(project_path: Path, days: int = 7) -> list[dict]:
    """Находит коммиты с 5+ изменёнными файлами."""
    if not (project_path / ".git").exists():
        return []

    since = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
    significant = []

    try:
        # Получаем все коммиты за период
        log = subprocess.run(
            ["git", "log", f"--since={since}", "--format=%H|||%ci|||%s",
             "--no-merges"],
            cwd=str(project_path),
            capture_output=True, text=True, timeout=15,
            encoding="utf-8", errors="replace"
        )

        for line in log.stdout.strip().splitlines():
            if not line.strip():
                continue
            parts = line.split("|||")
            if len(parts) != 3:
                continue

            sha, date, msg = parts[0].strip(), parts[1].strip()[:10], parts[2].strip()

            # Считаем файлы в коммите
            stat = subprocess.run(
                ["git", "diff-tree", "--no-commit-id", "--name-only", "-r", sha],
                cwd=str(project_path),
                capture_output=True, text=True, timeout=10,
                encoding="utf-8", errors="replace"
            )
            files = [f for f in stat.stdout.strip().splitlines() if f.strip()]
            file_count = len(files)

            if file_count >= 5:
                significant.append({
                    "sha": sha[:8],
                    "date": date,
                    "message": msg[:80],
                    "files_changed": file_count,
                    "files": files[:10],  # Первые 10 для примера
                })

    except (subprocess.TimeoutExpired, FileNotFoundError, Exception):
        pass

    return significant


def check_changelog_coverage(project_path: Path, commits: list[dict]) -> list[dict]:
    """Проверяет, есть ли записи в CHANGELOG для значимых коммитов."""
    cl_path = project_path / "CHANGELOG.md"
    missing = []

    if not cl_path.exists():
        # Все коммиты пропущены — нет CHANGELOG
        for c in commits:
            c["status"] = "no_changelog"
        return commits

    changelog = cl_path.read_text(encoding="utf-8", errors="replace").lower()

    for commit in commits:
        # Ищем дату или ключевые слова из сообщения в CHANGELOG
        date_found = commit["date"] in changelog
        # Извлекаем ключевые слова из commit message
        msg_words = re.findall(r"[a-zA-Zа-яА-Я]{4,}", commit["message"].lower())
        words_found = sum(1 for w in msg_words if w in changelog)

        if date_found or words_found >= 2:
            commit["status"] = "covered"
        else:
            commit["status"] = "missing"
            missing.append(commit)

    return missing


def generate_changelog_template(project_name: str, commit: dict) -> str:
    """Генерирует шаблон записи для CHANGELOG."""
    date = commit["date"]
    msg = commit["message"]

    # Определяем тип изменения
    if any(kw in msg.lower() for kw in ["fix", "исправ", "bug", "баг"]):
        change_type = "Fixed"
    elif any(kw in msg.lower() for kw in ["feat", "добав", "add", "new"]):
        change_type = "Added"
    elif any(kw in msg.lower() for kw in ["refactor", "рефактор", "clean"]):
        change_type = "Changed"
    else:
        change_type = "Changed"

    template = f"""
## [{date}]
### {change_type}
- {msg} ({commit['files_changed']} файлов)
"""
    return template.strip()


def generate_report(days: int = 7, fix: bool = False) -> str:
    """Генерирует отчёт по всем проектам."""
    now = datetime.now()
    lines = [
        "# 📋 Changelog Enforcement Report",
        "",
        f"> Период: {days} дней | Порог: 5+ файлов",
        f"> Дата: {now.strftime('%Y-%m-%d %H:%M')}",
        "",
    ]

    total_missing = 0
    total_covered = 0

    for name, path in PROJECTS.items():
        if not path.exists():
            continue

        commits = get_significant_commits(path, days)

        if not commits:
            lines.append(f"### ⚪ {name} — нет крупных коммитов")
            lines.append("")
            continue

        missing = check_changelog_coverage(path, commits)
        covered = len(commits) - len(missing)
        total_missing += len(missing)
        total_covered += covered

        if not missing:
            lines.append(f"### ✅ {name} — {len(commits)} коммитов, все в CHANGELOG")
            lines.append("")
            continue

        lines.append(f"### ⚠️ {name} — {len(missing)} из {len(commits)} не в CHANGELOG")
        lines.append("")

        for commit in missing:
            status = "❌ НЕТ CHANGELOG" if commit["status"] == "no_changelog" else "⚠️ Не найдено"
            lines.append(f"- `{commit['sha']}` {commit['date']} — {commit['message']}")
            lines.append(f"  {status} ({commit['files_changed']} файлов)")

            if fix:
                template = generate_changelog_template(name, commit)
                lines.append(f"  **Шаблон:**")
                lines.append(f"  ```markdown")
                for tl in template.splitlines():
                    lines.append(f"  {tl}")
                lines.append(f"  ```")

        lines.append("")

    # Итог
    total = total_missing + total_covered
    if total > 0:
        coverage = (total_covered / total * 100) if total > 0 else 0
        lines.extend([
            "---",
            "",
            "## 📊 Итог",
            "",
            f"| Метрика | Значение |",
            f"|---------|----------|",
            f"| Крупных коммитов | {total} |",
            f"| В CHANGELOG | {total_covered} |",
            f"| Пропущено | {total_missing} |",
            f"| Покрытие | {coverage:.0f}% |",
        ])

    return "\n".join(lines)


def main():
    args = sys.argv[1:]
    fix = "--fix" in args
    days = 7

    if "--days" in args:
        idx = args.index("--days")
        if idx + 1 < len(args):
            try:
                days = int(args[idx + 1])
            except ValueError:
                pass

    report = generate_report(days, fix)
    print(report)


if __name__ == "__main__":
    main()
