#!/usr/bin/env python3
"""
🔄 METAai Batch Review
Прогоняет несколько файлов через pipeline и собирает общий отчёт.

Использование:
    python batch_review.py --level 2 --project C:\\Users\\Gigabyte\\Sylectus
    python batch_review.py --level 3 --files file1.py file2.py file3.py
    python batch_review.py --level 2 --project C:\\path --pattern "*.py" --critical-only
"""
import asyncio
import argparse
import sys
import time
from pathlib import Path
from datetime import datetime

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent))
from src.agents.orchestrator import AgentOrchestrator
from src.agents.review_agent import ReviewAgent


# Patterns for critical files (security, payments, auth)
CRITICAL_PATTERNS = [
    "**/payment*", "**/auth*", "**/login*", "**/crypto*",
    "**/secret*", "**/admin*", "**/billing*", "**/subscription*",
    "**/handler*", "**/router*", "**/middleware*", "**/webhook*",
]

# Skip patterns
SKIP_PATTERNS = [
    "__pycache__", ".git", "node_modules", ".venv", "venv",
    "migrations", "tests", "test_", "__init__",
]


def find_python_files(project_dir: Path, critical_only: bool = False) -> list[Path]:
    """Find Python files in project, optionally filtering to critical ones."""
    all_files = list(project_dir.rglob("*.py"))

    # Filter out skip patterns
    filtered = []
    for f in all_files:
        skip = False
        for pattern in SKIP_PATTERNS:
            if pattern in str(f):
                skip = True
                break
        if not skip and f.stat().st_size > 100:  # Skip tiny files
            filtered.append(f)

    if critical_only:
        critical = []
        for f in filtered:
            name = f.name.lower()
            for pattern in CRITICAL_PATTERNS:
                clean = pattern.replace("**/", "").replace("*", "")
                if clean in name:
                    critical.append(f)
                    break
        return critical

    return filtered


async def batch_review(files: list[Path], level: int, project_name: str):
    """Review multiple files and produce a summary report."""
    agent = ReviewAgent()
    results = []
    total_cost = 0.0
    total_time = 0

    print(f"\n{'='*60}")
    print(f"🔄 METAai Batch Review — {project_name}")
    print(f"📁 Файлов: {len(files)} | Level: {level}")
    print(f"{'='*60}\n")

    for i, filepath in enumerate(files, 1):
        print(f"[{i}/{len(files)}] 🔍 {filepath.name}...", end=" ", flush=True)

        try:
            content = filepath.read_text(encoding="utf-8")
            lines = len(content.splitlines())

            # Skip very large files
            if lines > 1000:
                print(f"⏭️ Пропущен ({lines} строк, >1000)")
                results.append({
                    "file": filepath.name,
                    "path": str(filepath),
                    "status": "skipped",
                    "reason": f"{lines} строк (слишком большой)",
                })
                continue

            response = await agent.review_file(filepath, context=f"Level {level} review")

            # Parse verdict
            verdict = "❓"
            score = 0
            if "SAFE TO DEPLOY" in response:
                verdict = "✅"
                score = 90
            elif "NEEDS FIXES" in response:
                verdict = "⚠️"
                score = 65
            elif "DO NOT DEPLOY" in response:
                verdict = "🚫"
                score = 30

            # Extract confidence score if present
            import re
            score_match = re.search(r"(\d+)/100", response)
            if score_match:
                score = int(score_match.group(1))

            results.append({
                "file": filepath.name,
                "path": str(filepath),
                "status": "reviewed",
                "verdict": verdict,
                "score": score,
                "response": response,
            })

            print(f"{verdict} {score}/100")

            # Small delay to avoid rate limits
            await asyncio.sleep(2)

        except Exception as e:
            print(f"❌ Ошибка: {e}")
            results.append({
                "file": filepath.name,
                "path": str(filepath),
                "status": "error",
                "error": str(e),
            })

    # Summary
    reviewed = [r for r in results if r["status"] == "reviewed"]
    errors = [r for r in results if r["status"] == "error"]
    skipped = [r for r in results if r["status"] == "skipped"]

    avg_score = sum(r["score"] for r in reviewed) / len(reviewed) if reviewed else 0

    print(f"\n{'='*60}")
    print(f"📊 Batch Review Summary — {project_name}")
    print(f"{'='*60}")
    print(f"📁 Всего файлов:  {len(files)}")
    print(f"✅ Проверено:     {len(reviewed)}")
    print(f"⏭️  Пропущено:     {len(skipped)}")
    print(f"❌ Ошибок:        {len(errors)}")
    print(f"📈 Средний балл:  {avg_score:.0f}/100")
    print()

    # Ranking
    if reviewed:
        print("🏆 Рейтинг файлов:")
        for r in sorted(reviewed, key=lambda x: x["score"]):
            print(f"   {r['verdict']} {r['score']:3}/100  {r['file']}")

    print(f"{'='*60}\n")

    # Save batch report
    report_dir = Path(__file__).parent / "reviews"
    report_dir.mkdir(exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    report_file = report_dir / f"{timestamp}_batch_{project_name}.md"

    report_content = f"# 🔄 Batch Review — {project_name}\n"
    report_content += f"**Дата**: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
    report_content += f"**Level**: {level}\n"
    report_content += f"**Файлов**: {len(reviewed)}/{len(files)}\n"
    report_content += f"**Средний балл**: {avg_score:.0f}/100\n\n"

    for r in sorted(reviewed, key=lambda x: x["score"]):
        report_content += f"---\n\n## {r['verdict']} {r['file']} ({r['score']}/100)\n\n"
        report_content += r.get("response", "") + "\n\n"

    report_file.write_text(report_content, encoding="utf-8")
    print(f"💾 Отчёт сохранён: {report_file.name}")

    return results


def main():
    parser = argparse.ArgumentParser(description="METAai Batch Review")
    parser.add_argument("--level", type=int, default=2, help="Complexity level (1-3)")
    parser.add_argument("--project", type=str, help="Project directory to scan")
    parser.add_argument("--files", nargs="+", help="Specific files to review")
    parser.add_argument("--critical-only", action="store_true",
                        help="Only review critical files (payment, auth, etc)")
    parser.add_argument("--max-files", type=int, default=10,
                        help="Maximum files to review (default: 10)")

    args = parser.parse_args()

    if args.files:
        files = [Path(f) for f in args.files]
        project_name = "custom"
    elif args.project:
        project_dir = Path(args.project)
        if not project_dir.exists():
            print(f"❌ Директория не найдена: {project_dir}")
            sys.exit(1)
        files = find_python_files(project_dir, args.critical_only)
        # Find real project root
        for parent in [project_dir] + list(project_dir.parents):
            if (parent / ".git").exists():
                project_name = parent.name
                break
        else:
            project_name = project_dir.name
    else:
        print("❌ Укажи --project или --files")
        sys.exit(1)

    # Limit
    if len(files) > args.max_files:
        print(f"⚠️ Найдено {len(files)} файлов, ограничено до {args.max_files}")
        files = files[:args.max_files]

    if not files:
        print("📁 Файлы не найдены")
        sys.exit(0)

    asyncio.run(batch_review(files, args.level, project_name))


if __name__ == "__main__":
    main()
