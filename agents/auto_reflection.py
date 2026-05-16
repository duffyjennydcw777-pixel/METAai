"""
🪞 Agent #3: Auto-Reflection
Ночной агент — собирает итоги дня и обновляет EVOLUTION_LOG.

Что делает:
1. Сканирует git diff за сегодня во ВСЕХ проектах
2. Считает изменённые файлы, добавленные строки
3. Генерирует Daily Summary в Markdown
4. Опционально: дописывает в EVOLUTION_LOG.md

Использование:
    python -m agents.auto_reflection              # Отчёт в консоль
    python -m agents.auto_reflection --save       # Сохранить в reports/
    python -m agents.auto_reflection --evolution   # Добавить в EVOLUTION_LOG
    python -m agents.auto_reflection --days 3     # За последние 3 дня
"""

import subprocess
import sys
from datetime import datetime, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from agents.config import PROJECTS, SECOND_BRAIN, REPORTS_DIR


def git_log_today(project_path: Path, days: int = 1) -> dict:
    """Получает git log за указанное количество дней."""
    result = {
        "commits": [],
        "files_changed": 0,
        "insertions": 0,
        "deletions": 0,
        "error": None,
    }

    if not (project_path / ".git").exists():
        result["error"] = "Нет git репозитория"
        return result

    since = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")

    try:
        # Список коммитов
        log_output = subprocess.run(
            ["git", "log", f"--since={since}", "--oneline", "--no-merges"],
            cwd=str(project_path),
            capture_output=True, text=True, timeout=10,
            encoding="utf-8", errors="replace"
        )
        if log_output.stdout.strip():
            result["commits"] = log_output.stdout.strip().split("\n")

        # Статистика изменений (для возможного расширения)
        subprocess.run(
            ["git", "diff", "--stat", f"HEAD~{len(result['commits']) or 1}..HEAD"],
            cwd=str(project_path),
            capture_output=True, text=True, timeout=10,
            encoding="utf-8", errors="replace"
        )

        # Shortstat для цифр
        shortstat = subprocess.run(
            ["git", "log", f"--since={since}", "--shortstat", "--no-merges", "--format="],
            cwd=str(project_path),
            capture_output=True, text=True, timeout=10,
            encoding="utf-8", errors="replace"
        )

        if shortstat.stdout:
            for line in shortstat.stdout.split("\n"):
                if "file" in line:
                    import re
                    files = re.search(r"(\d+) files? changed", line)
                    inserts = re.search(r"(\d+) insertions?", line)
                    deletes = re.search(r"(\d+) deletions?", line)
                    if files:
                        result["files_changed"] += int(files.group(1))
                    if inserts:
                        result["insertions"] += int(inserts.group(1))
                    if deletes:
                        result["deletions"] += int(deletes.group(1))

    except subprocess.TimeoutExpired:
        result["error"] = "Git timeout"
    except FileNotFoundError:
        result["error"] = "Git не установлен"
    except Exception as e:
        result["error"] = str(e)

    return result


def generate_daily_summary(days: int = 1) -> str:
    """Генерирует Daily Summary по всем проектам."""
    now = datetime.now()
    date_str = now.strftime("%Y-%m-%d")
    period = f"за {days} день" if days == 1 else f"за {days} дней"

    lines = [
        f"# 🪞 Daily Reflection — {date_str}",
        "",
        f"> Автоматический отчёт {period}",
        f"> Сгенерировано: {now.strftime('%H:%M')}",
        "",
    ]

    total_commits = 0
    total_files = 0
    total_insertions = 0
    total_deletions = 0
    active_projects = []

    lines.append("## Проекты")
    lines.append("")

    for name, path in PROJECTS.items():
        git_data = git_log_today(path, days)

        if git_data["error"]:
            lines.append(f"### ⚪ {name}")
            lines.append(f"- {git_data['error']}")
            lines.append("")
            continue

        if not git_data["commits"]:
            lines.append(f"### ⚪ {name} — без изменений")
            lines.append("")
            continue

        active_projects.append(name)
        commit_count = len(git_data["commits"])
        total_commits += commit_count
        total_files += git_data["files_changed"]
        total_insertions += git_data["insertions"]
        total_deletions += git_data["deletions"]

        lines.append(f"### 🟢 {name} — {commit_count} коммит(ов)")
        lines.append(f"- Файлов: {git_data['files_changed']} | "
                      f"+{git_data['insertions']} / -{git_data['deletions']}")
        lines.append("- Коммиты:")
        for c in git_data["commits"][:10]:  # Макс 10
            lines.append(f"  - `{c}`")
        lines.append("")

    # Итог
    lines.extend([
        "---",
        "",
        "## 📊 Итог дня",
        "",
        "| Метрика | Значение |",
        "|---------|----------|",
        f"| Активных проектов | {len(active_projects)} из {len(PROJECTS)} |",
        f"| Коммитов | {total_commits} |",
        f"| Файлов изменено | {total_files} |",
        f"| Строк добавлено | +{total_insertions} |",
        f"| Строк удалено | -{total_deletions} |",
        f"| Чистый прирост | {total_insertions - total_deletions:+d} строк |",
        "",
    ])

    # Уровень продуктивности
    if total_commits == 0:
        level = "😴 Отдых"
    elif total_commits <= 3:
        level = "🟡 Лёгкий день"
    elif total_commits <= 10:
        level = "🟢 Нормальный день"
    elif total_commits <= 20:
        level = "🔥 Продуктивный день"
    else:
        level = "⚡ Марафон!"

    lines.append(f"**Продуктивность: {level}**")

    return "\n".join(lines)


def append_to_evolution_log(summary: str):
    """Добавляет запись в EVOLUTION_LOG.md."""
    evo_log = SECOND_BRAIN / "05_Life" / "EVOLUTION_LOG.md"

    if not evo_log.exists():
        print("  ❌ EVOLUTION_LOG.md не найден")
        return

    # Готовим компактную запись
    now = datetime.now()
    date_str = now.strftime("%Y-%m-%d")

    entry = f"\n\n## [{date_str}] Auto-Reflection\n"
    entry += "- Автоматический ночной отчёт\n"

    # Извлекаем итоговую таблицу из summary
    in_summary = False
    for line in summary.split("\n"):
        if "## 📊 Итог дня" in line:
            in_summary = True
        elif in_summary and line.startswith("##"):
            break
        elif in_summary and line.strip():
            entry += line + "\n"

    content = evo_log.read_text(encoding="utf-8")
    content += entry
    evo_log.write_text(content, encoding="utf-8")
    print("  ✅ Добавлено в EVOLUTION_LOG.md")


def main():
    args = sys.argv[1:]
    save = "--save" in args
    evolution = "--evolution" in args
    days = 1

    # Парсим --days N
    if "--days" in args:
        idx = args.index("--days")
        if idx + 1 < len(args):
            try:
                days = int(args[idx + 1])
            except ValueError:
                pass

    summary = generate_daily_summary(days)

    # Вывод в консоль
    print(summary)

    # Сохранение
    if save:
        REPORTS_DIR.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d")
        path = REPORTS_DIR / f"reflection_{timestamp}.md"
        path.write_text(summary, encoding="utf-8")
        print(f"\n📄 Сохранено: {path}")

    # В EVOLUTION_LOG
    if evolution:
        append_to_evolution_log(summary)


if __name__ == "__main__":
    main()
