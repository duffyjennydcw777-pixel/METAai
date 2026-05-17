"""
🔄 Agent #7: Rule Syncer
Синхронизирует глобальные rules из мастер-копии (METAai) во все проекты.

Что делает:
1. Читает master rules из METAai/.agent/rules/
2. Сравнивает MD5 с каждым проектом
3. Репортит drift (рассинхронизацию)
4. --fix: автокопирование (НЕ трогает project-specific файлы)

Использование:
    python -m agents.rule_syncer           # Показать drift
    python -m agents.rule_syncer --fix     # Исправить drift
    python -m agents.rule_syncer --save    # + Markdown отчёт
"""

import hashlib
import shutil
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from agents.config import (
    PROJECTS, GLOBAL_RULES, MASTER_RULES_SOURCE,
    REPORTS_DIR,
)


def file_hash(path: Path) -> str:
    """MD5 хеш файла."""
    return hashlib.md5(path.read_bytes()).hexdigest()


def scan_drift() -> dict[str, list[dict]]:
    """
    Сканирует все проекты на drift.
    Возвращает: {project_name: [{rule, status, detail}]}
    """
    results = {}

    for project_name, project_path in PROJECTS.items():
        rules_dir = project_path / ".agent" / "rules"
        project_issues = []

        for rule_file in GLOBAL_RULES:
            master = MASTER_RULES_SOURCE / rule_file
            target = rules_dir / rule_file

            if not master.exists():
                continue  # Мастер-копии нет — пропускаем

            if project_path == MASTER_RULES_SOURCE.parent.parent:
                # Это сам METAai — источник, дрифта быть не может
                project_issues.append({
                    "rule": rule_file,
                    "status": "master",
                    "detail": "Мастер-копия",
                })
                continue

            if not target.exists():
                project_issues.append({
                    "rule": rule_file,
                    "status": "missing",
                    "detail": "Файл отсутствует",
                })
            elif file_hash(master) != file_hash(target):
                project_issues.append({
                    "rule": rule_file,
                    "status": "drift",
                    "detail": "Контент отличается от мастера",
                })
            else:
                project_issues.append({
                    "rule": rule_file,
                    "status": "ok",
                    "detail": "Синхронизирован",
                })

        results[project_name] = project_issues

    return results


def fix_drift(results: dict[str, list[dict]]) -> int:
    """Копирует недостающие/устаревшие rules из мастера. Возвращает кол-во фиксов."""
    fixed = 0

    for project_name, issues in results.items():
        project_path = PROJECTS[project_name]
        rules_dir = project_path / ".agent" / "rules"

        for issue in issues:
            if issue["status"] in ("missing", "drift"):
                master = MASTER_RULES_SOURCE / issue["rule"]
                target = rules_dir / issue["rule"]

                rules_dir.mkdir(parents=True, exist_ok=True)
                shutil.copy2(master, target)
                issue["status"] = "fixed"
                issue["detail"] = "Скопирован из мастера"
                fixed += 1
                print(f"  ✅ {issue['rule']} → {project_name}")

    return fixed


def print_console(results: dict[str, list[dict]]):
    """Красивый вывод в консоль."""
    print("\n" + "=" * 60)
    print("  🔄 RULE SYNCER — Phase 3 Agent #7")
    print("=" * 60)

    total_ok = 0
    total_drift = 0
    total_missing = 0

    for project_name, issues in results.items():
        ok = sum(1 for i in issues if i["status"] in ("ok", "master"))
        drift = sum(1 for i in issues if i["status"] == "drift")
        missing = sum(1 for i in issues if i["status"] == "missing")
        fixed = sum(1 for i in issues if i["status"] == "fixed")

        total_ok += ok + fixed
        total_drift += drift
        total_missing += missing

        if drift == 0 and missing == 0:
            emoji = "🟢"
        elif missing > 0:
            emoji = "🔴"
        else:
            emoji = "🟡"

        status_parts = []
        if ok > 0:
            status_parts.append(f"✅{ok}")
        if drift > 0:
            status_parts.append(f"🔄{drift}")
        if missing > 0:
            status_parts.append(f"❌{missing}")
        if fixed > 0:
            status_parts.append(f"🔧{fixed}")

        print(f"  {emoji} {project_name:12s}  {' '.join(status_parts)}")

        # Показать детали drift/missing
        for issue in issues:
            if issue["status"] in ("drift", "missing"):
                print(f"      └─ {issue['rule']}: {issue['detail']}")

    print("-" * 60)
    total = total_ok + total_drift + total_missing
    score = round((total_ok / total) * 100) if total > 0 else 100
    emoji = "🟢" if score == 100 else "🟡" if score >= 80 else "🔴"
    print(f"  {emoji} Синхронизация: {score}% ({total_ok}/{total} rules)")
    print("=" * 60 + "\n")


def generate_report(results: dict[str, list[dict]]) -> str:
    """Генерирует Markdown отчёт."""
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    lines = [
        f"# 🔄 Rule Sync Report — {now}",
        "",
        "| Проект | ✅ OK | 🔄 Drift | ❌ Missing | 🔧 Fixed |",
        "|--------|:-----:|:--------:|:---------:|:--------:|",
    ]

    for project_name, issues in results.items():
        ok = sum(1 for i in issues if i["status"] in ("ok", "master"))
        drift = sum(1 for i in issues if i["status"] == "drift")
        missing = sum(1 for i in issues if i["status"] == "missing")
        fixed = sum(1 for i in issues if i["status"] == "fixed")
        lines.append(f"| {project_name} | {ok} | {drift} | {missing} | {fixed} |")

    # Детали
    lines.extend(["", "---", "", "## Детали"])
    for project_name, issues in results.items():
        problem_issues = [i for i in issues if i["status"] not in ("ok", "master")]
        if problem_issues:
            lines.append(f"\n### {project_name}")
            for i in problem_issues:
                lines.append(f"- `{i['rule']}`: {i['detail']}")

    return "\n".join(lines)


def main():
    args = sys.argv[1:]
    do_fix = "--fix" in args
    save_md = "--save" in args or "--md" in args

    results = scan_drift()

    if do_fix:
        print("🔧 Синхронизация rules...\n")
        fixed = fix_drift(results)
        if fixed == 0:
            print("  Всё уже синхронизировано — нечего фиксить.\n")
        else:
            print(f"\n  Исправлено: {fixed} файлов\n")

    print_console(results)

    if save_md:
        REPORTS_DIR.mkdir(parents=True, exist_ok=True)
        report = generate_report(results)
        timestamp = datetime.now().strftime("%Y%m%d")
        path = REPORTS_DIR / f"rules_sync_{timestamp}.md"
        path.write_text(report, encoding="utf-8")
        print(f"📄 Сохранено: {path}")


if __name__ == "__main__":
    main()
