"""
🧠 Review History — Information Gain Optimizer.
Tracks which files have been reviewed, avoids re-reviewing unchanged files.
Shannon: maximize information gain per API dollar.
"""
import json
import hashlib
from pathlib import Path
from datetime import datetime


HISTORY_FILE = Path("review_history.json")


def _load_history() -> dict:
    """Load review history from disk."""
    if HISTORY_FILE.exists():
        try:
            return json.loads(HISTORY_FILE.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, Exception):
            return {"files": {}, "stats": {"total_reviews": 0, "skipped": 0, "saved_usd": 0.0}}
    return {"files": {}, "stats": {"total_reviews": 0, "skipped": 0, "saved_usd": 0.0}}


def _save_history(history: dict):
    """Save review history to disk."""
    HISTORY_FILE.write_text(json.dumps(history, indent=2, ensure_ascii=False), encoding="utf-8")


def file_hash(filepath: str | Path) -> str:
    """SHA-256 hash of file contents."""
    content = Path(filepath).read_text(encoding="utf-8", errors="ignore")
    return hashlib.sha256(content.encode()).hexdigest()[:16]


def should_review(filepath: str | Path, force: bool = False) -> bool:
    """
    Check if file needs review based on content hash.
    Returns True if file is new or changed since last review.
    Shannon: skip review when information gain ≈ 0 (file unchanged).
    """
    if force:
        return True

    filepath = str(Path(filepath).resolve())
    current_hash = file_hash(filepath)

    history = _load_history()
    files = history.get("files", {})

    if filepath in files:
        last_hash = files[filepath].get("hash", "")
        if last_hash == current_hash:
            # File unchanged — information gain ≈ 0
            history["stats"]["skipped"] = history["stats"].get("skipped", 0) + 1
            history["stats"]["saved_usd"] = history["stats"].get("saved_usd", 0) + 0.01
            _save_history(history)
            return False

    return True


def mark_reviewed(filepath: str | Path, score: int = 0, issues: int = 0):
    """Record that a file has been reviewed."""
    filepath = str(Path(filepath).resolve())
    current_hash = file_hash(filepath)

    history = _load_history()
    history["files"][filepath] = {
        "hash": current_hash,
        "last_reviewed": datetime.now().isoformat(),
        "score": score,
        "issues": issues,
        "review_count": history["files"].get(filepath, {}).get("review_count", 0) + 1,
    }
    history["stats"]["total_reviews"] = history["stats"].get("total_reviews", 0) + 1
    _save_history(history)


def get_stats() -> dict:
    """Get review history statistics."""
    history = _load_history()
    stats = history.get("stats", {})
    files = history.get("files", {})

    return {
        "total_files_tracked": len(files),
        "total_reviews": stats.get("total_reviews", 0),
        "skipped_reviews": stats.get("skipped", 0),
        "money_saved": stats.get("saved_usd", 0.0),
        "worst_files": sorted(
            [(Path(f).name, d.get("score", 0)) for f, d in files.items()],
            key=lambda x: x[1]
        )[:5],
    }


# ── CLI ──────────────────────────────────────────────────

if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "--stats":
        stats = get_stats()
        print("=" * 50)
        print("🧠 Review History — Information Gain Stats")
        print("=" * 50)
        print(f"  📁 Files tracked:     {stats['total_files_tracked']}")
        print(f"  ✅ Total reviews:     {stats['total_reviews']}")
        print(f"  ⏭️  Skipped (no IG):  {stats['skipped_reviews']}")
        print(f"  💰 Money saved:       ${stats['money_saved']:.2f}")
        if stats["worst_files"]:
            print("\n  📉 Worst scoring files:")
            for name, score in stats["worst_files"]:
                print(f"      {name}: {score}/100")
        print("=" * 50)

    elif len(sys.argv) > 1:
        filepath = sys.argv[1]
        needs = should_review(filepath)
        print(f"{'✅ NEEDS REVIEW' if needs else '⏭️ SKIP (unchanged)'}: {filepath}")

    else:
        print("Usage:")
        print("  python review_history.py --stats          # Show stats")
        print("  python review_history.py <filepath>       # Check if file needs review")
