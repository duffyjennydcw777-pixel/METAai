"""
🧠 Bayesian Bug Predictor.
Updates probability of bugs in files based on review history.
P(bug|file) = prior × likelihood / evidence.

Uses Bayesian updating: each review updates our belief about file quality.
"""
import json
from pathlib import Path
from datetime import datetime


BAYES_FILE = Path("bayes_predictions.json")

# Priors based on file type/name patterns
PRIOR_RISK = {
    "payment": 0.7,
    "auth": 0.7,
    "crypto": 0.7,
    "secret": 0.8,
    "subscription": 0.6,
    "handler": 0.5,
    "router": 0.5,
    "service": 0.4,
    "model": 0.3,
    "schema": 0.2,
    "config": 0.3,
    "utils": 0.3,
    "test": 0.1,
    "__init__": 0.05,
}
DEFAULT_PRIOR = 0.4


def _load() -> dict:
    if BAYES_FILE.exists():
        try:
            return json.loads(BAYES_FILE.read_text(encoding="utf-8"))
        except Exception:
            return {"files": {}}
    return {"files": {}}


def _save(data: dict):
    BAYES_FILE.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def get_prior(filename: str) -> float:
    """Get prior probability based on filename patterns."""
    name_lower = filename.lower().replace(".py", "")
    for pattern, prior in PRIOR_RISK.items():
        if pattern in name_lower:
            return prior
    return DEFAULT_PRIOR


def update_belief(filepath: str, had_bugs: bool, bug_count: int = 0, score: int = 50):
    """
    Bayesian update after reviewing a file.
    
    P(buggy|observed) = P(observed|buggy) × P(buggy) / P(observed)
    
    Simplified: we use beta distribution updating.
    α = "bug observations", β = "clean observations"
    P(buggy) = α / (α + β)
    """
    data = _load()
    key = Path(filepath).name

    if key not in data["files"]:
        prior = get_prior(key)
        # Convert prior to pseudo-counts (α, β)
        # Start with 2 effective observations
        alpha = prior * 2
        beta = (1 - prior) * 2
        data["files"][key] = {
            "filepath": str(filepath),
            "alpha": alpha,
            "beta": beta,
            "p_bug": prior,
            "reviews": 0,
            "bugs_found": 0,
            "clean_reviews": 0,
            "last_updated": None,
        }

    entry = data["files"][key]

    # Update with new observation
    if had_bugs:
        # Weight by severity: more bugs = stronger update
        weight = min(bug_count, 5) * 0.5 + 0.5
        entry["alpha"] += weight
        entry["bugs_found"] += 1
    else:
        entry["beta"] += 1
        entry["clean_reviews"] += 1

    # Score-based adjustment: very low score = strong bug signal
    if score < 40:
        entry["alpha"] += 0.5
    elif score > 85:
        entry["beta"] += 0.3

    entry["reviews"] += 1
    entry["p_bug"] = entry["alpha"] / (entry["alpha"] + entry["beta"])
    entry["last_updated"] = datetime.now().isoformat()

    _save(data)
    return entry["p_bug"]


def get_predictions(min_reviews: int = 0) -> list[dict]:
    """Get all predictions sorted by bug probability."""
    data = _load()
    files = data.get("files", {})

    predictions = [
        {
            "file": k,
            "p_bug": v["p_bug"],
            "reviews": v["reviews"],
            "bugs_found": v["bugs_found"],
            "confidence": min(v["reviews"] / 5, 1.0),  # 0-1, full at 5 reviews
        }
        for k, v in files.items()
        if v["reviews"] >= min_reviews
    ]

    return sorted(predictions, key=lambda x: x["p_bug"], reverse=True)


def should_review_bayes(filepath: str, threshold: float = 0.3) -> bool:
    """Decide if file needs review based on Bayesian probability."""
    data = _load()
    key = Path(filepath).name

    if key not in data["files"]:
        # Unknown file — use prior
        prior = get_prior(key)
        return prior >= threshold

    return data["files"][key]["p_bug"] >= threshold


def seed_from_entropy(entropy_score: float, filepath: str):
    """Seed Bayesian prior from entropy analysis."""
    # High entropy → higher prior probability of bugs
    if entropy_score > 80:
        had_bugs = True
        bug_count = 3
    elif entropy_score > 60:
        had_bugs = True
        bug_count = 1
    else:
        had_bugs = False
        bug_count = 0

    update_belief(filepath, had_bugs, bug_count, score=int(100 - entropy_score))


# ── CLI ──────────────────────────────────────────────────

if __name__ == "__main__":
    import sys

    print("=" * 55)
    print("🧠 Bayesian Bug Predictor")
    print("=" * 55)

    predictions = get_predictions()

    if not predictions:
        print("  No data yet. Predictions build automatically from reviews.")
        print("  Seed with: python bayes.py --seed <directory>")
        
        if len(sys.argv) > 2 and sys.argv[1] == "--seed":
            from entropy import analyze_directory
            directory = Path(sys.argv[2])
            reports = analyze_directory(directory)
            for r in reports:
                seed_from_entropy(r.complexity_score, r.filepath)
            print(f"\n  🌱 Seeded {len(reports)} files from entropy data")
            predictions = get_predictions()
    
    if predictions:
        print(f"\n{'File':<30} {'P(bug)':>8} {'Reviews':>8} {'Confidence':>10}")
        print("-" * 58)
        for p in predictions[:15]:
            emoji = "🔴" if p["p_bug"] > 0.6 else "🟡" if p["p_bug"] > 0.35 else "🟢"
            conf = f"{p['confidence']*100:.0f}%"
            print(f"  {emoji} {p['file']:<28} {p['p_bug']:>6.1%}  {p['reviews']:>6}  {conf:>8}")

    print(f"\n{'=' * 55}")
