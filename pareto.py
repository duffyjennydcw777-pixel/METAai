"""
🎯 Pareto Hot Files — 80/20 Bug Predictor.
Tracks which files produce the most bugs.
20% of files contain 80% of bugs → focus review there.
"""
import json
from pathlib import Path
from datetime import datetime
from collections import Counter


PARETO_FILE = Path("pareto_hotfiles.json")


def _load() -> dict:
    if PARETO_FILE.exists():
        try:
            return json.loads(PARETO_FILE.read_text(encoding="utf-8"))
        except Exception:
            return {"files": {}, "updated": None}
    return {"files": {}, "updated": None}


def _save(data: dict):
    data["updated"] = datetime.now().isoformat()
    PARETO_FILE.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def record_review(filepath: str, score: int, issues_found: int, project: str = ""):
    """Record review results for a file."""
    data = _load()
    key = str(Path(filepath).name)

    if key not in data["files"]:
        data["files"][key] = {
            "full_path": str(filepath),
            "project": project,
            "reviews": 0,
            "total_issues": 0,
            "worst_score": 100,
            "best_score": 0,
            "avg_score": 0,
            "scores": [],
            "last_reviewed": None,
            "is_hot": False,
        }

    entry = data["files"][key]
    entry["reviews"] += 1
    entry["total_issues"] += issues_found
    entry["worst_score"] = min(entry["worst_score"], score)
    entry["best_score"] = max(entry["best_score"], score)
    entry["scores"].append(score)
    entry["scores"] = entry["scores"][-10:]  # Keep last 10
    entry["avg_score"] = sum(entry["scores"]) / len(entry["scores"])
    entry["last_reviewed"] = datetime.now().isoformat()

    # Mark as hot if: avg < 60 OR issues > 5 OR worst < 40
    entry["is_hot"] = (
        entry["avg_score"] < 60 or
        entry["total_issues"] > 5 or
        entry["worst_score"] < 40
    )

    _save(data)


def get_hot_files(top_n: int = 10) -> list[dict]:
    """Get the most problematic files (Pareto's vital few)."""
    data = _load()
    files = data.get("files", {})

    ranked = sorted(
        files.values(),
        key=lambda f: (f.get("total_issues", 0), -f.get("avg_score", 100)),
        reverse=True,
    )

    return ranked[:top_n]


def get_pareto_ratio() -> dict:
    """Calculate actual Pareto ratio."""
    data = _load()
    files = data.get("files", {})
    if not files:
        return {"ratio": "N/A", "hot_pct": 0, "issue_pct": 0}

    total_files = len(files)
    total_issues = sum(f.get("total_issues", 0) for f in files.values())
    if total_issues == 0:
        return {"ratio": "N/A", "hot_pct": 0, "issue_pct": 0}

    hot = [f for f in files.values() if f.get("is_hot", False)]
    hot_issues = sum(f.get("total_issues", 0) for f in hot)

    hot_pct = len(hot) / total_files * 100
    issue_pct = hot_issues / total_issues * 100

    return {
        "ratio": f"{hot_pct:.0f}% files → {issue_pct:.0f}% issues",
        "hot_files": len(hot),
        "total_files": total_files,
        "hot_pct": hot_pct,
        "issue_pct": issue_pct,
    }


def ingest_from_fixes(fixes_path: str | Path = "FIXES.md"):
    """Auto-populate from existing FIXES.md."""
    fixes = Path(fixes_path)
    if not fixes.exists():
        print(f"❌ {fixes_path} не найден")
        return

    content = fixes.read_text(encoding="utf-8")
    # Parse [Project] patterns
    import re
    entries = re.findall(r'\[(\w+)\].*?(?:📍\s*(\S+\.py))?', content)

    project_issues = Counter()
    for project, filename in entries:
        if filename:
            record_review(filename, score=50, issues_found=1, project=project)
        project_issues[project] += 1

    print(f"📊 Imported {sum(project_issues.values())} issues from FIXES.md")
    for proj, count in project_issues.most_common():
        print(f"   {proj}: {count}")


# ── CLI ──────────────────────────────────────────────────

if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "--ingest":
        ingest_from_fixes()
    elif len(sys.argv) > 1 and sys.argv[1] == "--ratio":
        r = get_pareto_ratio()
        print(f"🎯 Pareto Ratio: {r['ratio']}")
    else:
        print("=" * 50)
        print("🎯 Pareto Hot Files — Top Problematic")
        print("=" * 50)

        hot = get_hot_files()
        if not hot:
            print("  No review data yet. Run reviews first.")
            print("  Or: python pareto.py --ingest (import from FIXES.md)")
        else:
            for i, f in enumerate(hot, 1):
                emoji = "🔴" if f.get("is_hot") else "🟡"
                print(f"  {emoji} #{i} {f.get('full_path', '?')}")
                print(f"      Score: {f.get('avg_score', 0):.0f}/100 "
                      f"(worst: {f.get('worst_score', 0)}) | "
                      f"Issues: {f.get('total_issues', 0)} | "
                      f"Reviews: {f.get('reviews', 0)}")

            r = get_pareto_ratio()
            print(f"\n  📊 Pareto: {r['ratio']}")

        print("=" * 50)
