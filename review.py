#!/usr/bin/env python3
"""
🔍 review.py — CLI для запуска AI Code Review.

Использование:
    # Review staged changes
    python review.py

    # Review last commit
    python review.py --last-commit

    # Review with specific complexity level
    python review.py --level 3

    # Review specific file
    python review.py --file src/bot/handlers.py

    # Full preflight check
    python review.py --preflight

    # Review from stdin (pipe git diff)
    git diff | python review.py --stdin
"""
import asyncio
import argparse
import sys
import logging
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from agents.config import config
from agents.review_agent import ReviewAgent, get_git_diff
from agents.preflight_agent import PreflightAgent
from agents.orchestrator import AgentOrchestrator
from agents.test_gen_agent import TestGenAgent
from agents.refactor_agent import RefactorAgent


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("review")


async def cmd_review(args):
    """Run code review on diff."""
    # Get diff
    if args.stdin:
        diff = sys.stdin.read()
    elif args.file:
        filepath = Path(args.file)
        if not filepath.exists():
            print(f"❌ Файл не найден: {filepath}")
            sys.exit(1)
        # Read file as pseudo-diff for orchestrator pipeline
        content = filepath.read_text(encoding="utf-8")
        diff = f"--- /dev/null\n+++ b/{filepath.name}\n" + \
               "\n".join(f"+{line}" for line in content.splitlines())
    elif args.last_commit:
        diff = get_git_diff(last_commit=True)
    elif args.staged:
        diff = get_git_diff(staged=True)
    else:
        # Default: staged, then unstaged, then last commit
        diff = get_git_diff(staged=True)
        if not diff.strip():
            diff = get_git_diff()
        if not diff.strip():
            diff = get_git_diff(last_commit=True)

    if not diff.strip():
        print("⚠️ Нет изменений для review. Используй --file, --last-commit, или --stdin.")
        sys.exit(0)

    # Run pipeline
    orchestrator = AgentOrchestrator()

    # Determine project name from file path or CWD
    if args.file:
        filepath = Path(args.file)
        # Walk up to find project root (where .git or pyproject.toml lives)
        for parent in filepath.parents:
            if (parent / ".git").exists() or (parent / "pyproject.toml").exists():
                project_name = parent.name
                break
        else:
            project_name = filepath.parent.name
    else:
        project_name = Path.cwd().name

    project_dir = Path.cwd() if args.preflight else None

    results = await orchestrator.run_pipeline(
        complexity_level=args.level,
        diff=diff,
        project_dir=project_dir,
        project_name=project_name,
        context=args.context or "",
    )

    # Print reports
    for report in results.get("reports", []):
        print(report)
        print()


async def cmd_preflight(args):
    """Run preflight checks on project."""
    agent = PreflightAgent()
    project_dir = Path(args.dir) if args.dir else Path.cwd()

    print(f"🚀 Preflight check: {project_dir.name}")
    print("-" * 40)

    result = await agent.check_project(project_dir)

    if result["issues"]:
        for issue in result["issues"]:
            icon = {"critical": "🔴", "warning": "🟡", "info": "🟢"}.get(
                issue["severity"], "❓"
            )
            print(f"  {icon} [{issue['severity']}] {issue['message']}")
    else:
        print("  ✅ Все проверки пройдены!")

    print(f"\n🏁 Рекомендация: {result['recommendation']}")
    print(f"📊 Уверенность: {result['confidence']}%")


async def cmd_test_gen(args):
    """Generate pytest tests for a file."""
    if not args.file:
        print("❌ Укажи --file для генерации тестов")
        sys.exit(1)

    filepath = Path(args.file)
    if not filepath.exists():
        print(f"❌ Файл не найден: {filepath}")
        sys.exit(1)

    agent = TestGenAgent()
    print(f"🧪 Генерирую тесты для {filepath.name}...")

    tests = await agent.generate_tests(filepath, context=args.context or "")

    print(f"\n{'='*60}")
    print(f"🧪 Generated Tests — {filepath.name}")
    print(f"{'='*60}")
    print(tests)
    print(f"{'='*60}")
    print(f"💾 Тесты сохранены в generated_tests/test_{filepath.stem}.py")


async def cmd_fix(args):
    """Generate fixes from a review report."""
    agent = RefactorAgent()

    if args.review:
        review_path = Path(args.review)
        if not review_path.exists():
            print(f"❌ Отчёт не найден: {review_path}")
            sys.exit(1)
        print(f"🔧 Генерирую фиксы из {review_path.name}...")
        fixes = await agent.fix_from_review(review_path)
    elif args.file and args.issue:
        filepath = Path(args.file)
        if not filepath.exists():
            print(f"❌ Файл не найден: {filepath}")
            sys.exit(1)
        code = filepath.read_text(encoding="utf-8")
        print(f"🔧 Генерирую фикс для {filepath.name}...")
        fixes = await agent.fix_issue(args.issue, code, str(filepath))
    else:
        # Auto-fix: find latest review
        reviews_dir = Path("reviews")
        if reviews_dir.exists():
            latest = sorted(reviews_dir.glob("*.md"))[-1] if list(reviews_dir.glob("*.md")) else None
            if latest:
                print(f"🔧 Автофикс из последнего review: {latest.name}...")
                fixes = await agent.fix_from_review(latest)
            else:
                print("❌ Нет review отчётов")
                sys.exit(1)
        else:
            print("❌ Папка reviews/ не найдена")
            sys.exit(1)

    print(f"\n{'='*60}")
    print(f"🔧 Generated Fixes")
    print(f"{'='*60}")
    print(fixes)
    print(f"{'='*60}")


def cmd_entropy(args):
    """Run Shannon entropy analysis on file or directory."""
    from entropy import analyze_file, analyze_directory
    from collections import Counter

    target = Path(args.path)

    print("=" * 60)
    print("📐 Shannon Entropy Analyzer")
    print("=" * 60)

    if target.is_file():
        report = analyze_file(target)
        print(f"\n{report}")
        if report.flags:
            for flag in report.flags:
                print(f"    {flag}")
    elif target.is_dir():
        reports = analyze_directory(target, args.pattern)
        if not reports:
            print(f"No {args.pattern} files found in {target}")
            return

        level_counts = Counter(r.recommended_level for r in reports)
        avg_complexity = sum(r.complexity_score for r in reports) / len(reports)

        print(f"\n📁 {target.name}: {len(reports)} files, "
              f"avg complexity: {avg_complexity:.0f}/100")
        print(f"   🟢 Level 1: {level_counts.get(1, 0)} | "
              f"🟡 Level 2: {level_counts.get(2, 0)} | "
              f"🔴 Level 3: {level_counts.get(3, 0)}")
        print()

        for report in reports:
            print(f"  {report}")
            if report.flags:
                for flag in report.flags:
                    print(f"      {flag}")
    else:
        print(f"❌ Не найдено: {target}")
        sys.exit(1)

    print(f"\n{'='*60}")


def cmd_impact(args):
    """Show dependency graph and blast radius."""
    from impact import full_graph_report, analyze_impact

    target = Path(args.path)
    if not target.is_dir():
        print(f"❌ Не найдено: {target}")
        sys.exit(1)

    if args.file:
        report = analyze_impact(target, args.file)
        print(f"🕸️ Impact of changing {report.changed_file}:")
        print(f"   Risk: {report.risk_level} | Blast radius: {report.blast_radius}")
        print(f"   Direct ({len(report.direct_dependents)}): {', '.join(report.direct_dependents)}")
        print(f"   Indirect ({len(report.indirect_dependents)}): {', '.join(report.indirect_dependents)}")
    else:
        print(full_graph_report(target))


def cmd_pareto(args):
    """Show Pareto hot files."""
    from pareto import get_hot_files, get_pareto_ratio, ingest_from_fixes

    if args.ingest:
        ingest_from_fixes()
        return

    print("=" * 50)
    print("🎯 Pareto Hot Files")
    print("=" * 50)

    hot = get_hot_files()
    if not hot:
        print("  No data. Run: python review.py pareto --ingest")
    else:
        for i, f in enumerate(hot, 1):
            emoji = "🔴" if f.get("is_hot") else "🟡"
            print(f"  {emoji} #{i} {f.get('full_path', '?')}")
            print(f"      Score: {f.get('avg_score', 0):.0f}/100 | Issues: {f.get('total_issues', 0)}")

        r = get_pareto_ratio()
        print(f"\n  📊 Pareto: {r['ratio']}")
    print("=" * 50)


def cmd_dupes(args):
    """Find code duplication via Kolmogorov NCD."""
    from kolmogorov import find_duplicates

    target = Path(args.path)
    if not target.is_dir():
        print(f"❌ Не найдено: {target}")
        sys.exit(1)

    print("=" * 60)
    print("🧬 Kolmogorov Code Duplication Detector")
    print(f"   Scanning: {target.name}")
    print("=" * 60)

    dupes = find_duplicates(target, threshold=args.threshold)
    if not dupes:
        print(f"\n  ✅ No duplication found (>{args.threshold:.0%})")
    else:
        print(f"\n  ⚠️ {len(dupes)} pair(s):\n")
        for d in dupes:
            emoji = "🔴" if d.similarity > 0.7 else "🟡" if d.similarity > 0.5 else "🟢"
            print(f"  {emoji} {d.similarity:.0%} — {d.file_a} ↔ {d.file_b}")

    print(f"\n{'=' * 60}")



def main():
    parser = argparse.ArgumentParser(
        description="🔍 METAai Code Review — AI-powered code review and preflight checks",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    subparsers = parser.add_subparsers(dest="command", help="Команда")

    # Review command
    review_parser = subparsers.add_parser("review", help="Code review diff")
    review_parser.add_argument("--level", type=int, default=2, choices=[1, 2, 3],
                              help="Complexity level (1=trivial, 2=standard, 3=complex)")
    review_parser.add_argument("--last-commit", action="store_true",
                              help="Review last commit diff")
    review_parser.add_argument("--staged", action="store_true",
                              help="Review only staged changes")
    review_parser.add_argument("--file", type=str, help="Review a specific file")
    review_parser.add_argument("--stdin", action="store_true",
                              help="Read diff from stdin")
    review_parser.add_argument("--context", type=str, default="",
                              help="Additional context for the reviewer")
    review_parser.add_argument("--preflight", action="store_true",
                              help="Also run preflight checks")

    # Preflight command
    preflight_parser = subparsers.add_parser("preflight", help="Pre-deploy checks")
    preflight_parser.add_argument("--dir", type=str, help="Project directory (default: cwd)")

    # Test-gen command
    test_parser = subparsers.add_parser("test-gen", help="Generate pytest tests")
    test_parser.add_argument("--file", type=str, required=True, help="File to generate tests for")
    test_parser.add_argument("--context", type=str, default="", help="Additional context")

    # Fix command
    fix_parser = subparsers.add_parser("fix", help="Generate fixes for found issues")
    fix_parser.add_argument("--review", type=str, help="Review report to fix")
    fix_parser.add_argument("--file", type=str, help="File with the issue")
    fix_parser.add_argument("--issue", type=str, help="Issue description")

    # Entropy command (Shannon analyzer)
    entropy_parser = subparsers.add_parser("entropy", help="Shannon entropy analysis")
    entropy_parser.add_argument("--path", type=str, required=True, help="File or directory")
    entropy_parser.add_argument("--pattern", type=str, default="*.py", help="File pattern")

    # Impact command (dependency graph)
    impact_parser = subparsers.add_parser("impact", help="Dependency graph & blast radius")
    impact_parser.add_argument("--path", type=str, required=True, help="Project directory")
    impact_parser.add_argument("--file", type=str, help="Check impact of specific file")

    # Pareto command (hot files)
    pareto_parser = subparsers.add_parser("pareto", help="Show hottest bug-prone files")
    pareto_parser.add_argument("--ingest", action="store_true", help="Import from FIXES.md")

    # Dupes command (code duplication)
    dupes_parser = subparsers.add_parser("dupes", help="Find code duplication")
    dupes_parser.add_argument("--path", type=str, required=True, help="Directory to scan")
    dupes_parser.add_argument("--threshold", type=float, default=0.45, help="Similarity threshold")

    args = parser.parse_args()

    # Validate config
    errors = config.validate()
    if errors and args.command != "preflight":
        print("❌ Ошибки конфигурации:")
        for err in errors:
            print(f"   • {err}")
        sys.exit(1)

    # Default to review if no command
    if args.command is None:
        # Quick mode: just run review with defaults
        args.command = "review"
        args.level = 2
        args.last_commit = False
        args.staged = False
        args.file = None
        args.stdin = False
        args.context = ""
        args.preflight = False

    if args.command == "review":
        asyncio.run(cmd_review(args))
    elif args.command == "preflight":
        asyncio.run(cmd_preflight(args))
    elif args.command == "test-gen":
        asyncio.run(cmd_test_gen(args))
    elif args.command == "fix":
        asyncio.run(cmd_fix(args))
    elif args.command == "entropy":
        cmd_entropy(args)
    elif args.command == "impact":
        cmd_impact(args)
    elif args.command == "pareto":
        cmd_pareto(args)
    elif args.command == "dupes":
        cmd_dupes(args)


if __name__ == "__main__":
    main()
