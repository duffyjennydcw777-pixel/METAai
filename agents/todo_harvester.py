"""
📌 Agent #8: TODO Harvester
Собирает все TODO/FIXME/HACK/XXX маркеры из всех проектов.

Что делает:
1. Рекурсивно сканирует исходники всех проектов
2. Группирует находки по проекту → файлу
3. Приоритизирует: FIXME > HACK > TODO > XXX
4. Отслеживает тренд (больше/меньше)
5. --save: Markdown отчёт
6. --obsidian: обновляет Second Brain TODO_BACKLOG.md

Использование:
    python -m agents.todo_harvester            # Отчёт в консоль
    python -m agents.todo_harvester --save     # + Markdown файл
    python -m agents.todo_harvester --obsidian # + обновить Obsidian
"""

import re
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from agents.config import (
    PROJECTS, TODO_PATTERNS, TODO_PRIORITY,
    TODO_EXCLUDE_DIRS, TODO_EXCLUDE_EXTENSIONS,
    REPORTS_DIR, SECOND_BRAIN,
)


def should_skip(path: Path) -> bool:
    """Проверяет, нужно ли пропустить файл/папку."""
    parts = path.parts
    for exclude_dir in TODO_EXCLUDE_DIRS:
        if exclude_dir in parts:
            return True
    if path.suffix.lower() in TODO_EXCLUDE_EXTENSIONS:
        return True
    return False


def scan_file(filepath: Path) -> list[dict]:
    """Сканирует один файл на TODO-маркеры."""
    findings = []
    try:
        content = filepath.read_text(encoding="utf-8", errors="ignore")
    except (OSError, PermissionError):
        return findings

    # Паттерн: ищем TODO/FIXME/HACK/XXX с опциональным : или пробелом после
    pattern = re.compile(
        r"\b(" + "|".join(TODO_PATTERNS) + r")\b\s*:?\s*(.*)",
        re.IGNORECASE,
    )

    for line_num, line in enumerate(content.split("\n"), 1):
        # Пропускаем слишком длинные строки (минификация)
        if len(line) > 500:
            continue

        match = pattern.search(line)
        if match:
            marker = match.group(1).upper()
            text = match.group(2).strip()[:120]  # Ограничиваем длину
            # Фильтр false positives
            if _is_false_positive(line, marker, filepath):
                continue
            findings.append({
                "marker": marker,
                "text": text,
                "line": line_num,
                "priority": TODO_PRIORITY.get(marker, 0),
            })

    return findings


def _is_false_positive(line: str, marker: str, filepath: Path) -> bool:
    """Фильтрует false positives."""
    line_lower = line.lower().strip()
    fname = filepath.name.lower()

    # 1. Переводы (translations.js)
    if '"todo"' in line_lower or "'todo'" in line_lower:
        if "filter" in line_lower or "label" in line_lower:
            return True

    # 2. Строки в кавычках (переменные, не маркеры)
    if f'"{marker}"' in line or f"'{marker}'" in line:
        return True

    # 3. Приоритетные описания вроде "FIXME > HACK > TODO > XXX"
    if ">" in line and sum(p in line.upper() for p in TODO_PATTERNS) >= 3:
        return True

    # 4. CHANGELOG.md — упоминания агентов/инструментов (не реальные маркеры)
    if fname == "changelog.md":
        agent_keywords = ["harvester", "syncer", "generator", "monitor", "enforcer",
                          "checker", "scanner", "pulse", "watchdog", "conductor"]
        if any(kw in line_lower for kw in agent_keywords):
            return True

    # 5. Markdown-файлы: шаблоны таблиц и описания форматов
    if filepath.suffix.lower() == ".md":
        # Шаблоны статусов: "XXX | Статус" — описания формата, не маркеры
        if "статус" in line_lower or "status" in line_lower:
            if "|" in line:
                return True
        # Описания архитектуры/решений (не код)
        if marker == "XXX" and "|" in line:
            return True

    # 6. Docstrings в самих агентах (описывают функционал)
    if fname in ("health_monitor.py", "todo_harvester.py", "config.py"):
        # Описания агентов: "Считает TODO/FIXME/HACK в коде"
        if "считает" in line_lower or "приоритизирует" in line_lower:
            return True
        # Списки паттернов в config
        if "patterns" in line_lower or "priority" in line_lower:
            return True

    # 7. CSS: HACK в комментариях — контексте хак-решений визуала
    if filepath.suffix.lower() == ".css":
        if marker == "HACK" and ("/*" in line or "*/" in line):
            # Это настоящий HACK-маркер в CSS, НЕ false positive
            pass

    # 8. Markdown-файлы в shared skills (не наш код)
    if ".shared" in str(filepath) or "antigravity-kit" in str(filepath):
        return True

    # 9. GitHub Actions workflow — не наш TODO
    if ".github" in str(filepath):
        return True

    return False


def scan_project(name: str, path: Path) -> dict:
    """Сканирует весь проект."""
    findings_by_file: dict[str, list[dict]] = {}
    total = 0

    if not path.exists():
        return {"name": name, "files": {}, "total": 0}

    for filepath in path.rglob("*"):
        if not filepath.is_file():
            continue
        if should_skip(filepath):
            continue

        findings = scan_file(filepath)
        if findings:
            rel_path = str(filepath.relative_to(path))
            findings_by_file[rel_path] = sorted(
                findings, key=lambda f: -f["priority"]
            )
            total += len(findings)

    return {"name": name, "files": findings_by_file, "total": total}


def load_previous_count() -> int | None:
    """Загружает количество TODO из предыдущего отчёта для тренда."""
    reports = sorted(REPORTS_DIR.glob("todos_*.md"), reverse=True)
    if not reports:
        return None

    content = reports[0].read_text(encoding="utf-8", errors="ignore")
    # Ищем строку "Всего маркеров: N"
    match = re.search(r"Всего маркеров:\s*\*\*(\d+)\*\*", content)
    if match:
        return int(match.group(1))
    return None


def print_console(project_results: list[dict], prev_count: int | None):
    """Красивый вывод в консоль."""
    print("\n" + "=" * 60)
    print("  📌 TODO HARVESTER — Phase 3 Agent #8")
    print("=" * 60)

    grand_total = sum(p["total"] for p in project_results)

    for proj in project_results:
        if proj["total"] == 0:
            print(f"  🟢 {proj['name']:12s}  0 маркеров ✨")
            continue

        emoji = "🔴" if proj["total"] > 10 else "🟡" if proj["total"] > 3 else "🟢"
        print(f"  {emoji} {proj['name']:12s}  {proj['total']} маркеров")

        # Топ-3 критичных
        all_findings = []
        for rel_path, findings in proj["files"].items():
            for f in findings:
                all_findings.append({**f, "file": rel_path})

        all_findings.sort(key=lambda x: -x["priority"])
        for f in all_findings[:3]:
            print(f"      └─ [{f['marker']}] {f['file']}:{f['line']} — {f['text'][:60]}")
        if len(all_findings) > 3:
            print(f"      └─ ...и ещё {len(all_findings) - 3}")

    print("-" * 60)

    # Тренд
    trend = ""
    if prev_count is not None:
        diff = grand_total - prev_count
        if diff > 0:
            trend = f" 📈 +{diff} с прошлого прогона"
        elif diff < 0:
            trend = f" 📉 {diff} с прошлого прогона"
        else:
            trend = " ➡️ без изменений"

    print(f"  Всего маркеров: **{grand_total}**{trend}")
    print("=" * 60 + "\n")


def generate_report(project_results: list[dict], prev_count: int | None) -> str:
    """Генерирует Markdown отчёт."""
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    grand_total = sum(p["total"] for p in project_results)

    lines = [
        f"# 📌 TODO Harvester Report — {now}",
        "",
        f"Всего маркеров: **{grand_total}**",
        "",
    ]

    if prev_count is not None:
        diff = grand_total - prev_count
        if diff != 0:
            direction = "📈" if diff > 0 else "📉"
            lines.append(f"Тренд: {direction} {diff:+d} с прошлого прогона")
            lines.append("")

    lines.extend([
        "| Проект | FIXME | HACK | TODO | XXX | Всего |",
        "|--------|:-----:|:----:|:----:|:---:|:-----:|",
    ])

    for proj in project_results:
        counts = {"FIXME": 0, "HACK": 0, "TODO": 0, "XXX": 0}
        for findings in proj["files"].values():
            for f in findings:
                counts[f["marker"]] = counts.get(f["marker"], 0) + 1
        lines.append(
            f"| {proj['name']} | {counts['FIXME']} | {counts['HACK']} | "
            f"{counts['TODO']} | {counts['XXX']} | {proj['total']} |"
        )

    # Детали
    for proj in project_results:
        if proj["total"] == 0:
            continue
        lines.extend(["", "---", f"\n## {proj['name']} ({proj['total']})", ""])

        for rel_path, findings in sorted(proj["files"].items()):
            lines.append(f"### `{rel_path}`")
            for f in findings:
                lines.append(f"- **[{f['marker']}]** L{f['line']}: {f['text']}")
            lines.append("")

    return "\n".join(lines)


def update_obsidian(project_results: list[dict]):
    """Обновляет TODO_BACKLOG.md в Second Brain."""
    backlog_path = SECOND_BRAIN / "03_Projects" / "TODO_BACKLOG.md"
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    grand_total = sum(p["total"] for p in project_results)

    lines = [
        "---",
        f"updated: {now}",
        "tags: [auto-generated, agents]",
        "---",
        "",
        "# 📌 TODO Backlog (Auto-Generated)",
        "",
        f"> Последнее обновление: {now}",
        f"> Всего маркеров: **{grand_total}**",
        "",
    ]

    for proj in project_results:
        if proj["total"] == 0:
            continue
        lines.append(f"## {proj['name']} ({proj['total']})")
        lines.append("")

        all_findings = []
        for rel_path, findings in proj["files"].items():
            for f in findings:
                all_findings.append({**f, "file": rel_path})

        all_findings.sort(key=lambda x: -x["priority"])
        for f in all_findings:
            lines.append(f"- [ ] **[{f['marker']}]** `{f['file']}:{f['line']}` — {f['text']}")
        lines.append("")

    backlog_path.parent.mkdir(parents=True, exist_ok=True)
    backlog_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"📓 Obsidian обновлён: {backlog_path}")


def main():
    args = sys.argv[1:]
    save_md = "--save" in args or "--md" in args
    do_obsidian = "--obsidian" in args

    project_results = []
    for name, path in PROJECTS.items():
        project_results.append(scan_project(name, path))

    prev_count = load_previous_count()
    print_console(project_results, prev_count)

    if save_md:
        REPORTS_DIR.mkdir(parents=True, exist_ok=True)
        report = generate_report(project_results, prev_count)
        timestamp = datetime.now().strftime("%Y%m%d")
        path = REPORTS_DIR / f"todos_{timestamp}.md"
        path.write_text(report, encoding="utf-8")
        print(f"📄 Сохранено: {path}")

    if do_obsidian:
        update_obsidian(project_results)


if __name__ == "__main__":
    main()
