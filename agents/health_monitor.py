"""
📊 Agent #4: Project Health Monitor (Phase 2)
Глубокий анализ здоровья каждого проекта.

Что делает:
1. Анализирует размер кодовой базы (LOC, файлы)
2. Проверяет частоту коммитов (активный vs заброшенный)
3. Оценивает документацию (README, CHANGELOG полнота)
4. Считает TODO/FIXME/HACK в коде
5. Проверяет тестовое покрытие

Использование:
    python -m agents.health_monitor              # Все проекты
    python -m agents.health_monitor --project ONYX  # Один проект
    python -m agents.health_monitor --save       # Сохранить отчёт
"""

import subprocess
import sys
import re
from datetime import datetime, timedelta
from pathlib import Path
from collections import Counter

sys.path.insert(0, str(Path(__file__).parent.parent))
from agents.config import PROJECTS, REPORTS_DIR


def count_lines(project_path: Path) -> dict:
    """Считает строки кода по типам файлов."""
    stats = Counter()
    total_files = 0
    total_lines = 0

    code_extensions = {
        ".py": "Python",
        ".js": "JavaScript",
        ".ts": "TypeScript",
        ".jsx": "React JSX",
        ".tsx": "React TSX",
        ".html": "HTML",
        ".css": "CSS",
        ".md": "Markdown",
        ".json": "JSON",
        ".yaml": "YAML",
        ".yml": "YAML",
        ".toml": "TOML",
        ".sh": "Shell",
        ".bat": "Batch",
        ".sql": "SQL",
    }

    skip_dirs = {
        ".git", ".venv", "venv", "node_modules", "__pycache__",
        ".next", "out", "dist", "build", ".eggs", ".pytest_cache",
        ".idea", ".vscode", "htmlcov",
    }

    for path in project_path.rglob("*"):
        if any(d in path.parts for d in skip_dirs):
            continue
        if path.is_file() and path.suffix in code_extensions:
            try:
                lines = len(path.read_text(encoding="utf-8", errors="replace").splitlines())
                lang = code_extensions[path.suffix]
                stats[lang] += lines
                total_files += 1
                total_lines += lines
            except (PermissionError, OSError):
                pass

    return {
        "by_lang": dict(stats.most_common()),
        "total_files": total_files,
        "total_lines": total_lines,
    }


def count_debt_markers(project_path: Path) -> dict:
    """Ищет TODO, FIXME, HACK, XXX в коде."""
    markers = {"TODO": 0, "FIXME": 0, "HACK": 0, "XXX": 0}
    examples = []

    skip_dirs = {
        ".git", ".venv", "venv", "node_modules", "__pycache__",
        ".next", "dist", "build",
    }

    code_exts = {".py", ".js", ".ts", ".jsx", ".tsx", ".sh", ".bat"}

    for path in project_path.rglob("*"):
        if any(d in path.parts for d in skip_dirs):
            continue
        if path.is_file() and path.suffix in code_exts:
            try:
                for i, line in enumerate(path.read_text(
                    encoding="utf-8", errors="replace"
                ).splitlines(), 1):
                    for marker in markers:
                        if marker in line.upper():
                            markers[marker] += 1
                            if len(examples) < 5:
                                rel = path.relative_to(project_path)
                                examples.append(f"{rel}:{i} → {line.strip()[:80]}")
            except (PermissionError, OSError):
                pass

    return {"counts": markers, "examples": examples}


def git_activity(project_path: Path, days: int = 30) -> dict:
    """Анализирует git-активность за N дней."""
    result = {
        "has_git": False,
        "commits_30d": 0,
        "last_commit_date": None,
        "last_commit_msg": None,
        "days_since_commit": None,
        "contributors": 0,
    }

    if not (project_path / ".git").exists():
        return result

    result["has_git"] = True
    since = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")

    try:
        # Количество коммитов за 30 дней
        log = subprocess.run(
            ["git", "log", f"--since={since}", "--oneline", "--no-merges"],
            cwd=str(project_path),
            capture_output=True, text=True, timeout=10,
            encoding="utf-8", errors="replace"
        )
        if log.stdout.strip():
            result["commits_30d"] = len(log.stdout.strip().splitlines())

        # Последний коммит
        last = subprocess.run(
            ["git", "log", "-1", "--format=%ci|||%s"],
            cwd=str(project_path),
            capture_output=True, text=True, timeout=10,
            encoding="utf-8", errors="replace"
        )
        if last.stdout.strip():
            parts = last.stdout.strip().split("|||")
            if len(parts) == 2:
                date_str = parts[0].strip()[:10]
                result["last_commit_date"] = date_str
                result["last_commit_msg"] = parts[1].strip()[:60]
                try:
                    last_date = datetime.strptime(date_str, "%Y-%m-%d")
                    result["days_since_commit"] = (datetime.now() - last_date).days
                except ValueError:
                    pass

        # Контрибьюторы
        authors = subprocess.run(
            ["git", "log", "--format=%aN", "--all"],
            cwd=str(project_path),
            capture_output=True, text=True, timeout=10,
            encoding="utf-8", errors="replace"
        )
        if authors.stdout.strip():
            result["contributors"] = len(set(authors.stdout.strip().splitlines()))

    except (subprocess.TimeoutExpired, FileNotFoundError, Exception):
        pass

    return result


def assess_docs(project_path: Path) -> dict:
    """Оценивает качество документации."""
    checks = {
        "README.md": False,
        "CHANGELOG.md": False,
        "docs/": False,
        ".gitignore": False,
        "tests/": False,
    }

    for name in checks:
        target = project_path / name
        checks[name] = target.exists()

    # Оценка полноты README
    readme_quality = "missing"
    readme_path = project_path / "README.md"
    if readme_path.exists():
        content = readme_path.read_text(encoding="utf-8", errors="replace")
        lines = len(content.splitlines())
        if lines > 50:
            readme_quality = "comprehensive"
        elif lines > 20:
            readme_quality = "adequate"
        else:
            readme_quality = "minimal"

    # Оценка CHANGELOG
    changelog_entries = 0
    cl_path = project_path / "CHANGELOG.md"
    if cl_path.exists():
        content = cl_path.read_text(encoding="utf-8", errors="replace")
        changelog_entries = len(re.findall(r"^##\s", content, re.MULTILINE))

    return {
        "checks": checks,
        "readme_quality": readme_quality,
        "changelog_entries": changelog_entries,
    }


def calculate_health_score(
    loc: dict, debt: dict, git: dict, docs: dict
) -> tuple[int, list[str]]:
    """Рассчитывает общий балл здоровья (0-100)."""
    score = 100
    issues = []

    # Git activity (max -30)
    if not git["has_git"]:
        score -= 30
        issues.append("🔴 Нет git-репозитория")
    elif git["days_since_commit"] and git["days_since_commit"] > 30:
        score -= 15
        issues.append(f"🟡 Нет коммитов {git['days_since_commit']} дней")
    elif git["commits_30d"] < 3:
        score -= 5
        issues.append("🟡 Мало активности (<3 коммитов/мес)")

    # Documentation (max -25)
    if not docs["checks"]["README.md"]:
        score -= 10
        issues.append("🔴 Нет README.md")
    elif docs["readme_quality"] == "minimal":
        score -= 5
        issues.append("🟡 README слишком краткий")

    if not docs["checks"]["CHANGELOG.md"]:
        score -= 10
        issues.append("🔴 Нет CHANGELOG.md")
    elif docs["changelog_entries"] < 3:
        score -= 5
        issues.append("🟡 CHANGELOG: мало записей")

    if not docs["checks"][".gitignore"]:
        score -= 5
        issues.append("🟡 Нет .gitignore")

    # Code debt (max -20)
    total_debt = sum(debt["counts"].values())
    if total_debt > 20:
        score -= 15
        issues.append(f"🔴 Много TODO/FIXME: {total_debt}")
    elif total_debt > 5:
        score -= 5
        issues.append(f"🟡 TODO/FIXME: {total_debt}")

    # Tests (max -10)
    if not docs["checks"]["tests/"]:
        score -= 10
        issues.append("🟡 Нет тестов (tests/)")

    return max(0, score), issues


def generate_report(target_project: str = None) -> str:
    """Генерирует полный Health Report."""
    now = datetime.now()
    lines = [
        "# 🏥 Project Health Report",
        "",
        f"> Сгенерировано: {now.strftime('%Y-%m-%d %H:%M')}",
        "",
    ]

    projects = PROJECTS
    if target_project:
        if target_project in projects:
            projects = {target_project: projects[target_project]}
        else:
            return f"❌ Проект '{target_project}' не найден в конфиге"

    scores = {}

    for name, path in projects.items():
        if not path.exists():
            lines.append(f"## ⚪ {name} — не найден\n")
            continue

        loc = count_lines(path)
        debt = count_debt_markers(path)
        git = git_activity(path)
        docs = assess_docs(path)
        score, issues = calculate_health_score(loc, debt, git, docs)
        scores[name] = score

        # Иконка
        if score >= 90:
            icon = "🟢"
        elif score >= 70:
            icon = "🟡"
        else:
            icon = "🔴"

        lines.append(f"## {icon} {name} — {score}%")
        lines.append("")

        # Кодовая база
        lines.append("### 📁 Кодовая база")
        lines.append(f"- Файлов: {loc['total_files']} | Строк: {loc['total_lines']:,}")
        if loc["by_lang"]:
            top_3 = list(loc["by_lang"].items())[:3]
            langs = ", ".join(f"{lang}: {count:,}" for lang, count in top_3)
            lines.append(f"- Топ: {langs}")
        lines.append("")

        # Git
        lines.append("### 📊 Git-активность")
        if git["has_git"]:
            lines.append(f"- Коммитов (30д): {git['commits_30d']}")
            if git["last_commit_date"]:
                lines.append(
                    f"- Последний: {git['last_commit_date']} "
                    f"({git['days_since_commit']}д назад)"
                )
                lines.append(f"- Сообщение: `{git['last_commit_msg']}`")
        else:
            lines.append("- ⚠️ Нет git-репозитория")
        lines.append("")

        # Техдолг
        total_debt = sum(debt["counts"].values())
        if total_debt > 0:
            lines.append(f"### 🔧 Техдолг ({total_debt} маркеров)")
            for marker, count in debt["counts"].items():
                if count:
                    lines.append(f"- {marker}: {count}")
            if debt["examples"]:
                lines.append("- Примеры:")
                for ex in debt["examples"][:3]:
                    lines.append(f"  - `{ex}`")
            lines.append("")

        # Проблемы
        if issues:
            lines.append("### ⚠️ Проблемы")
            for issue in issues:
                lines.append(f"- {issue}")
            lines.append("")

        lines.append("---")
        lines.append("")

    # Итоговая таблица
    if len(scores) > 1:
        lines.append("## 📊 Сводка")
        lines.append("")
        lines.append("| Проект | Здоровье | Статус |")
        lines.append("|--------|----------|--------|")
        avg = 0
        for name, score in sorted(scores.items(), key=lambda x: -x[1]):
            icon = "🟢" if score >= 90 else "🟡" if score >= 70 else "🔴"
            bar = "█" * (score // 10) + "░" * (10 - score // 10)
            lines.append(f"| {name} | {bar} {score}% | {icon} |")
            avg += score

        avg_score = avg // len(scores) if scores else 0
        lines.append(f"| **Среднее** | | **{avg_score}%** |")
        lines.append("")

    return "\n".join(lines)


def main():
    args = sys.argv[1:]
    save = "--save" in args
    target = None

    if "--project" in args:
        idx = args.index("--project")
        if idx + 1 < len(args):
            target = args[idx + 1]

    report = generate_report(target)
    print(report)

    if save:
        REPORTS_DIR.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d")
        path = REPORTS_DIR / f"health_{timestamp}.md"
        path.write_text(report, encoding="utf-8")
        print(f"\n📄 Сохранено: {path}")


if __name__ == "__main__":
    main()
