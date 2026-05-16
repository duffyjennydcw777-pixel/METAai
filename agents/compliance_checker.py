"""
🔍 Agent #1: Compliance Checker
Сканирует все проекты и проверяет соответствие мета-системе.

Что проверяет:
1. Наличие обязательных файлов (.agent/rules/, CHANGELOG.md)
2. Наличие обязательных rules (playbooks.md, habits.md, code_complexity.md)
3. Синхронизацию rules между проектами (дрифт контента)
4. Свежесть ключевых файлов Second Brain
5. Незавершённые решения в Decision Log (статус ❌)

Использование:
    python -m agents.compliance_checker          # Полный отчёт в консоль
    python -m agents.compliance_checker --md     # + Markdown отчёт в agents/reports/
    python -m agents.compliance_checker --fix    # Авто-фикс (копирует недостающие rules)
"""

import hashlib
import sys
from datetime import datetime
from pathlib import Path

# Добавляем parent dir для импорта config
sys.path.insert(0, str(Path(__file__).parent.parent))
from agents.config import (
    PROJECTS, REQUIRED_RULES, RECOMMENDED_RULES,
    REQUIRED_STRUCTURE, RECOMMENDED_STRUCTURE,
    MONITORED_FILES, STALENESS_THRESHOLDS, DEFAULT_STALENESS,
    MASTER_RULES, REPORTS_DIR, SECOND_BRAIN,
)


class ComplianceResult:
    """Результат проверки одного проекта."""

    def __init__(self, name: str):
        self.name = name
        self.errors: list[str] = []      # 🔴 Критические
        self.warnings: list[str] = []    # 🟡 Рекомендации
        self.passed: list[str] = []      # 🟢 Пройдено
        self.drift: list[str] = []       # 🔄 Рассинхрон

    @property
    def score(self) -> int:
        """Compliance score: 0-100."""
        total = len(self.errors) + len(self.warnings) + len(self.passed)
        if total == 0:
            return 100
        return round((len(self.passed) / total) * 100)

    @property
    def emoji(self) -> str:
        if self.score >= 90:
            return "🟢"
        elif self.score >= 70:
            return "🟡"
        else:
            return "🔴"


def file_hash(path: Path) -> str:
    """MD5 хеш файла для сравнения контента."""
    return hashlib.md5(path.read_bytes()).hexdigest()


def check_project(name: str, path: Path) -> ComplianceResult:
    """Проверяет один проект на соответствие стандартам."""
    result = ComplianceResult(name)

    if not path.exists():
        result.errors.append(f"Директория проекта не найдена: {path}")
        return result

    # 1. Обязательная структура
    for rel_path, description in REQUIRED_STRUCTURE.items():
        target = path / rel_path
        if target.exists():
            result.passed.append(f"✅ {description}: `{rel_path}`")
        else:
            result.errors.append(f"❌ Нет {description}: `{rel_path}`")

    # 2. Рекомендуемая структура
    for rel_path, description in RECOMMENDED_STRUCTURE.items():
        target = path / rel_path
        if target.exists():
            result.passed.append(f"✅ {description}: `{rel_path}`")
        else:
            result.warnings.append(f"⚠️ Рекомендуется: {description} (`{rel_path}`)")

    # 3. Обязательные rules
    rules_dir = path / ".agent" / "rules"
    for rule_file in REQUIRED_RULES:
        target = rules_dir / rule_file
        if target.exists():
            result.passed.append(f"✅ Rule: `{rule_file}`")
        else:
            result.errors.append(f"❌ Нет обязательного rule: `{rule_file}`")

    # 4. Рекомендуемые rules
    for rule_file in RECOMMENDED_RULES:
        target = rules_dir / rule_file
        if target.exists():
            result.passed.append(f"✅ Rule: `{rule_file}` (опциональный)")
        else:
            result.warnings.append(f"⚠️ Рекомендуется rule: `{rule_file}`")

    # 5. Проверка дрифта (рассинхронизации) rules
    for rule_file, master_path in MASTER_RULES.items():
        target = rules_dir / rule_file
        if target.exists() and master_path.exists():
            if file_hash(target) != file_hash(master_path):
                result.drift.append(
                    f"🔄 `{rule_file}` отличается от мастер-копии ({master_path.parent.parent.parent.name})"
                )
            else:
                result.passed.append(f"✅ `{rule_file}` синхронизирован")

    # 6. CHANGELOG свежесть
    changelog = path / "CHANGELOG.md"
    if changelog.exists():
        age_days = (datetime.now() - datetime.fromtimestamp(changelog.stat().st_mtime)).days
        if age_days > 30:
            result.warnings.append(f"⚠️ CHANGELOG не обновлялся {age_days} дней")
        else:
            result.passed.append(f"✅ CHANGELOG свежий ({age_days}д назад)")

    return result


def check_second_brain() -> ComplianceResult:
    """Проверяет свежесть файлов Second Brain."""
    result = ComplianceResult("Second Brain")

    for name, path in MONITORED_FILES.items():
        if not path.exists():
            result.errors.append(f"❌ Файл не найден: {name}")
            continue

        mtime = datetime.fromtimestamp(path.stat().st_mtime)
        age = datetime.now() - mtime
        threshold = STALENESS_THRESHOLDS.get(name, DEFAULT_STALENESS)

        if age > threshold:
            result.warnings.append(
                f"⚠️ {name}: не обновлялся {age.days}д (порог: {threshold.days}д)"
            )
        else:
            result.passed.append(f"✅ {name}: свежий ({age.days}д назад)")

    return result


def check_decision_log() -> list[str]:
    """Находит незавершённые решения в Decision Log."""
    decision_log = SECOND_BRAIN / "10_MetaEngineering" / "decision_log_meta.md"
    if not decision_log.exists():
        return ["❌ Decision Log не найден"]

    content = decision_log.read_text(encoding="utf-8")
    unfinished = []

    # Ищем строки со статусом ❌
    for line in content.split("\n"):
        if "❌" in line and "НЕ ВЫПОЛНЕНО" in line:
            # Извлекаем название решения из ближайшего заголовка
            unfinished.append(f"🚨 {line.strip()}")

    # Ищем заголовки решений с ❌ статусом
    blocks = content.split("## ")
    for block in blocks:
        if "❌" in block:
            title = block.split("\n")[0].strip()
            if title and title not in [u.split("🚨 ")[-1] for u in unfinished]:
                unfinished.append(f"🚨 Незавершено: {title}")

    return unfinished


def generate_report(results: list[ComplianceResult], brain_result: ComplianceResult,
                     unfinished_decisions: list[str]) -> str:
    """Генерирует Markdown отчёт."""
    now = datetime.now().strftime("%Y-%m-%d %H:%M")

    lines = [
        f"# 📋 Compliance Report — {now}",
        "",
        "## Общий статус",
        "",
        "| Проект | Score | Ошибки | Предупреждения | Дрифт |",
        "|--------|:-----:|:------:|:--------------:|:-----:|",
    ]

    total_errors = 0
    total_warnings = 0

    for r in results:
        total_errors += len(r.errors)
        total_warnings += len(r.warnings)
        drift_str = str(len(r.drift)) if r.drift else "—"
        lines.append(
            f"| {r.emoji} {r.name} | {r.score}% | {len(r.errors)} | {len(r.warnings)} | {drift_str} |"
        )

    # Second Brain
    lines.append(
        f"| {brain_result.emoji} Second Brain | {brain_result.score}% | "
        f"{len(brain_result.errors)} | {len(brain_result.warnings)} | — |"
    )

    # Общий score
    all_results = results + [brain_result]
    avg_score = round(sum(r.score for r in all_results) / len(all_results))
    overall_emoji = "🟢" if avg_score >= 90 else "🟡" if avg_score >= 70 else "🔴"
    lines.extend([
        "",
        f"**Общий Compliance Score: {overall_emoji} {avg_score}%**",
        "",
    ])

    # Детали по проектам
    lines.append("---")
    lines.append("")
    lines.append("## Детали по проектам")

    for r in results:
        lines.append(f"\n### {r.emoji} {r.name} ({r.score}%)")

        if r.errors:
            lines.append("\n**Ошибки:**")
            for e in r.errors:
                lines.append(f"- {e}")

        if r.drift:
            lines.append("\n**Дрифт (рассинхронизация):**")
            for d in r.drift:
                lines.append(f"- {d}")

        if r.warnings:
            lines.append("\n**Рекомендации:**")
            for w in r.warnings:
                lines.append(f"- {w}")

        if not r.errors and not r.warnings and not r.drift:
            lines.append("\nВсё в порядке! ✨")

    # Second Brain
    lines.append(f"\n### {brain_result.emoji} Second Brain ({brain_result.score}%)")
    if brain_result.errors:
        for e in brain_result.errors:
            lines.append(f"- {e}")
    if brain_result.warnings:
        for w in brain_result.warnings:
            lines.append(f"- {w}")
    if not brain_result.errors and not brain_result.warnings:
        lines.append("\nВсе файлы актуальны ✨")

    # Незавершённые решения
    if unfinished_decisions:
        lines.append("\n---")
        lines.append("\n## 🚨 Незавершённые решения (Decision Log)")
        for d in unfinished_decisions:
            lines.append(f"- {d}")

    # Рекомендации
    lines.extend([
        "",
        "---",
        "",
        "## 📌 Рекомендуемые действия",
        "",
    ])

    if total_errors > 0:
        lines.append(f"1. **Исправить {total_errors} ошибок** — запустить `python -m agents.compliance_checker --fix`")
    if total_warnings > 0:
        lines.append(f"2. **Рассмотреть {total_warnings} рекомендаций**")
    if unfinished_decisions:
        lines.append(f"3. **Выполнить {len(unfinished_decisions)} незавершённых решений**")
    if total_errors == 0 and total_warnings == 0:
        lines.append("Всё чисто! Система в отличном состоянии. 🚀")

    return "\n".join(lines)


def auto_fix(results: list[ComplianceResult]):
    """Авто-фикс: копирует недостающие обязательные rules из мастер-копий."""
    import shutil

    fixed = 0
    for r in results:
        project_path = PROJECTS.get(r.name)
        if not project_path:
            continue

        rules_dir = project_path / ".agent" / "rules"

        for rule_file, master_path in MASTER_RULES.items():
            target = rules_dir / rule_file
            if not target.exists() and master_path.exists():
                rules_dir.mkdir(parents=True, exist_ok=True)
                shutil.copy2(master_path, target)
                print(f"  ✅ Скопирован {rule_file} → {r.name}")
                fixed += 1

    if fixed == 0:
        print("  Нечего фиксить — все rules на месте.")
    else:
        print(f"\n  Исправлено файлов: {fixed}")


def print_console_report(results: list[ComplianceResult], brain_result: ComplianceResult,
                          unfinished: list[str]):
    """Красивый вывод в консоль."""
    print("\n" + "=" * 60)
    print("  🔍 COMPLIANCE CHECKER — Phase 1 Agent #1")
    print("=" * 60)

    all_results = results + [brain_result]
    avg_score = round(sum(r.score for r in all_results) / len(all_results))

    for r in results:
        status = f"{r.emoji} {r.name:12s} [{r.score:3d}%]"
        issues = []
        if r.errors:
            issues.append(f"🔴{len(r.errors)}")
        if r.warnings:
            issues.append(f"🟡{len(r.warnings)}")
        if r.drift:
            issues.append(f"🔄{len(r.drift)}")
        suffix = "  " + " ".join(issues) if issues else "  ✨"
        print(f"  {status}{suffix}")

    # Second Brain
    print(f"  {brain_result.emoji} {'Second Brain':12s} [{brain_result.score:3d}%]", end="")
    if brain_result.warnings:
        print(f"  🟡{len(brain_result.warnings)}")
    else:
        print("  ✨")

    print("-" * 60)
    emoji = "🟢" if avg_score >= 90 else "🟡" if avg_score >= 70 else "🔴"
    print(f"  {emoji} ОБЩИЙ SCORE: {avg_score}%")

    if unfinished:
        print(f"\n  🚨 Незавершённые решения: {len(unfinished)}")
        for d in unfinished:
            print(f"    {d}")

    print("=" * 60 + "\n")


def main():
    args = sys.argv[1:]
    save_md = "--md" in args
    do_fix = "--fix" in args

    # Проверяем все проекты
    results: list[ComplianceResult] = []
    for name, path in PROJECTS.items():
        results.append(check_project(name, path))

    # Проверяем Second Brain
    brain_result = check_second_brain()

    # Незавершённые решения
    unfinished = check_decision_log()

    # Вывод
    print_console_report(results, brain_result, unfinished)

    # Авто-фикс
    if do_fix:
        print("🔧 Авто-фикс: копирую недостающие rules...\n")
        auto_fix(results)
        print()

    # Сохранение MD отчёта
    if save_md:
        REPORTS_DIR.mkdir(parents=True, exist_ok=True)
        report_md = generate_report(results, brain_result, unfinished)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        report_path = REPORTS_DIR / f"compliance_{timestamp}.md"
        report_path.write_text(report_md, encoding="utf-8")
        print(f"📄 Отчёт сохранён: {report_path}")


if __name__ == "__main__":
    main()
