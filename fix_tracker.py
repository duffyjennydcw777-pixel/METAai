#!/usr/bin/env python3
"""
🐛 METAai Fix Tracker
Парсит review-отчёты и собирает все найденные баги в единый трекер.

Использование:
    python fix_tracker.py              # Показать все баги
    python fix_tracker.py --export     # Экспорт в FIXES.md
"""
import re
import argparse
from pathlib import Path
from datetime import datetime
from collections import Counter


def parse_issues_from_reviews(reviews_dir: Path) -> list[dict]:
    """Parse all review reports and extract issues."""
    issues = []

    for f in sorted(reviews_dir.glob("*.md")):
        content = f.read_text(encoding="utf-8", errors="ignore")

        # Extract date/type/project from filename
        name_match = re.match(r"(\d{4}-\d{2}-\d{2})_\d+_(\w+)_(.+)\.md", f.name)
        date = name_match.group(1) if name_match else "unknown"
        review_type = name_match.group(2) if name_match else "unknown"
        project = name_match.group(3) if name_match else "unknown"

        # Parse critical issues (🔴)
        for match in re.finditer(r"🔴.*?(?:CRITICAL|Critical).*?\|([^|]+)\|([^|]+)\|([^|]+)\|([^|]+)\|([^|\n]+)", content):
            issues.append({
                "severity": "🔴 CRITICAL",
                "category": match.group(2).strip(),
                "description": match.group(3).strip(),
                "location": match.group(4).strip(),
                "fix": match.group(5).strip(),
                "project": project,
                "date": date,
                "source": f.name,
                "type": review_type,
            })

        # Parse numbered critical items
        for match in re.finditer(r"### Критичные проблемы 🔴\n((?:\d+\..*\n?)+)", content):
            for line_match in re.finditer(r"\d+\.\s+(.+)", match.group(1)):
                issues.append({
                    "severity": "🔴 CRITICAL",
                    "category": "Code Review",
                    "description": line_match.group(1).strip(),
                    "location": "—",
                    "fix": "—",
                    "project": project,
                    "date": date,
                    "source": f.name,
                    "type": review_type,
                })

        # Parse HIGH issues from tables
        for match in re.finditer(r"🟠.*?HIGH.*?\|([^|]+)\|([^|]+)\|([^|]+)\|([^|]+)\|([^|\n]+)", content):
            issues.append({
                "severity": "🟠 HIGH",
                "category": match.group(2).strip(),
                "description": match.group(3).strip(),
                "location": match.group(4).strip(),
                "fix": match.group(5).strip(),
                "project": project,
                "date": date,
                "source": f.name,
                "type": review_type,
            })

    return issues


def print_tracker(issues: list[dict]):
    """Print issues summary."""
    if not issues:
        print("✅ Нет найденных багов!")
        return

    critical = [i for i in issues if "CRITICAL" in i["severity"]]
    high = [i for i in issues if "HIGH" in i["severity"]]

    print(f"\n{'='*60}")
    print(f"🐛 METAai Fix Tracker")
    print(f"{'='*60}")
    print(f"🔴 Critical: {len(critical)}")
    print(f"🟠 High:     {len(high)}")
    print(f"📊 Всего:    {len(issues)}")

    # By project
    projects = Counter(i["project"] for i in issues)
    print(f"\n📁 По проектам:")
    for proj, count in projects.most_common():
        proj_critical = len([i for i in issues if i["project"] == proj and "CRITICAL" in i["severity"]])
        print(f"   {proj}: {count} issues ({proj_critical} critical)")

    # Critical issues detail
    if critical:
        print(f"\n{'='*60}")
        print(f"🔴 CRITICAL ISSUES ({len(critical)})")
        print(f"{'='*60}")
        for i, issue in enumerate(critical, 1):
            print(f"\n  {i}. [{issue['project']}] {issue['description']}")
            if issue['location'] != '—':
                print(f"     📍 {issue['location']}")
            if issue['fix'] != '—':
                print(f"     🔧 {issue['fix']}")

    # High issues
    if high:
        print(f"\n{'='*60}")
        print(f"🟠 HIGH ISSUES ({len(high)})")
        print(f"{'='*60}")
        for i, issue in enumerate(high, 1):
            print(f"\n  {i}. [{issue['project']}] {issue['description']}")
            if issue['location'] != '—':
                print(f"     📍 {issue['location']}")
            if issue['fix'] != '—':
                print(f"     🔧 {issue['fix']}")

    print(f"\n{'='*60}\n")


def export_fixes(issues: list[dict], output: Path):
    """Export issues to FIXES.md."""
    content = f"# 🐛 Fix Tracker — Сгенерировано METAai\n\n"
    content += f"**Дата**: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
    content += f"**Всего issues**: {len(issues)}\n\n"

    # Group by project
    by_project: dict[str, list] = {}
    for issue in issues:
        by_project.setdefault(issue["project"], []).append(issue)

    for project, proj_issues in sorted(by_project.items()):
        content += f"## {project}\n\n"
        content += "| # | Severity | Category | Description | Fix |\n"
        content += "|---|----------|----------|-------------|-----|\n"
        for i, issue in enumerate(proj_issues, 1):
            desc = issue['description'][:60]
            fix = issue['fix'][:40] if issue['fix'] != '—' else '—'
            content += f"| {i} | {issue['severity']} | {issue['category']} | {desc} | {fix} |\n"
        content += "\n"

    output.write_text(content, encoding="utf-8")
    print(f"💾 Экспортировано: {output}")


def main():
    parser = argparse.ArgumentParser(description="METAai Fix Tracker")
    parser.add_argument("--export", action="store_true", help="Export to FIXES.md")
    args = parser.parse_args()

    reviews_dir = Path(__file__).parent / "reviews"
    if not reviews_dir.exists():
        print("📁 Папка reviews/ не найдена")
        return

    issues = parse_issues_from_reviews(reviews_dir)
    print_tracker(issues)

    if args.export:
        export_fixes(issues, Path(__file__).parent / "FIXES.md")


if __name__ == "__main__":
    main()
