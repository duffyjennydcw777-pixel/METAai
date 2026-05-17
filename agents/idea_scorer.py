"""
🎯 Agent #24: Idea Scorer
Оценивает бизнес-идеи по 5 критериям, сравнивает с рыночными данными.

    python -m agents.idea_scorer "AI SEO tool"       # Оценить идею
    python -m agents.idea_scorer --list               # Все оценённые
    python -m agents.idea_scorer --save               # + в Second Brain
"""

import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from agents.config import IDEA_LOG, IDEA_WEIGHTS


# Benchmark data по нишам (из TrustMRR анализа)
NICHE_BENCHMARKS = {
    "AI SEO": {"market_size": 9, "competition": 6, "avg_mrr": 60000, "time_mvp_weeks": 3},
    "AI Video": {"market_size": 8, "competition": 5, "avg_mrr": 50000, "time_mvp_weeks": 4},
    "AI LinkedIn": {"market_size": 7, "competition": 7, "avg_mrr": 128000, "time_mvp_weeks": 3},
    "Creator Economy": {"market_size": 10, "competition": 8, "avg_mrr": 3600000, "time_mvp_weeks": 4},
    "Data Validation": {"market_size": 8, "competition": 4, "avg_mrr": 269000, "time_mvp_weeks": 2},
    "AI UGC": {"market_size": 7, "competition": 4, "avg_mrr": 66000, "time_mvp_weeks": 5},
    "AI Resume": {"market_size": 9, "competition": 6, "avg_mrr": 294000, "time_mvp_weeks": 2},
    "Ad Attribution": {"market_size": 8, "competition": 7, "avg_mrr": 207000, "time_mvp_weeks": 6},
    "SaaS HR": {"market_size": 7, "competition": 5, "avg_mrr": 40000, "time_mvp_weeks": 4},
    "Telegram Bot Platform": {"market_size": 8, "competition": 2, "avg_mrr": 10000, "time_mvp_weeks": 3},
    "VPN Data API": {"market_size": 6, "competition": 3, "avg_mrr": 30000, "time_mvp_weeks": 4},
}

# Наш стек — влияет на tech_fit
OUR_STACK = {"python", "telegram", "nextjs", "vpn", "ai", "api", "linux", "postgres"}


def score_idea(idea_name, niche=None):
    """Оценивает идею по 5 критериям (0-10 каждый)."""
    # Попытка найти бенчмарк
    bench = None
    if niche and niche in NICHE_BENCHMARKS:
        bench = NICHE_BENCHMARKS[niche]
    else:
        # Fuzzy match
        idea_lower = idea_name.lower()
        for key, val in NICHE_BENCHMARKS.items():
            if any(word in idea_lower for word in key.lower().split()):
                bench = val
                niche = key
                break

    if not bench:
        bench = {"market_size": 5, "competition": 5, "avg_mrr": 20000, "time_mvp_weeks": 4}
        niche = "Unknown"

    # Calculate scores
    market_size = min(bench["market_size"], 10)
    competition = 10 - min(bench["competition"], 10)  # Inverted: low competition = high score

    # Tech fit: how much of our stack overlaps
    idea_words = set(idea_name.lower().split())
    niche_words = set(niche.lower().replace("/", " ").split())
    tech_keywords = {"ai", "seo", "telegram", "bot", "api", "vpn", "video", "linkedin", "data"}
    overlap = len((idea_words | niche_words) & OUR_STACK) + len((idea_words | niche_words) & tech_keywords)
    tech_fit = min(overlap * 2.5, 10)

    # Time to MVP
    weeks = bench["time_mvp_weeks"]
    time_score = max(10 - weeks, 2)

    # Revenue potential
    avg = bench["avg_mrr"]
    if avg >= 100000:
        rev_score = 10
    elif avg >= 50000:
        rev_score = 8
    elif avg >= 20000:
        rev_score = 6
    elif avg >= 5000:
        rev_score = 4
    else:
        rev_score = 2

    scores = {
        "market_size": market_size,
        "competition": competition,
        "tech_fit": tech_fit,
        "time_to_mvp": time_score,
        "revenue_potential": rev_score,
    }

    # Weighted total
    total = sum(scores[k] * IDEA_WEIGHTS[k] for k in scores)

    return {
        "idea": idea_name,
        "niche": niche,
        "scores": scores,
        "total": round(total, 2),
        "grade": "A" if total >= 8 else "B" if total >= 6 else "C" if total >= 4 else "D",
        "benchmark_mrr": bench["avg_mrr"],
        "mvp_weeks": bench["time_mvp_weeks"],
    }


def main():
    args = sys.argv[1:]
    save_md = "--save" in args
    list_mode = "--list" in args

    print("\n" + "=" * 60)
    print("  🎯 IDEA SCORER — Phase 7 Agent #24")
    print("=" * 60)

    if list_mode:
        print("\n  📋 Доступные ниши с бенчмарками:")
        for niche, bench in sorted(NICHE_BENCHMARKS.items()):
            print(f"    {niche:25s}  market:{bench['market_size']}"
                  f"  comp:{bench['competition']}"
                  f"  avg:${bench['avg_mrr']:>8,}"
                  f"  mvp:{bench['time_mvp_weeks']}w")
        print("=" * 60 + "\n")
        return

    # Score all niches or specific idea
    ideas_text = [a for a in args if not a.startswith("--")]
    if ideas_text:
        ideas = [" ".join(ideas_text)]
    else:
        # Score our top candidates
        ideas = [
            "Telegram Bot Platform",
            "AI SEO tool",
            "VPN Data API",
            "AI UGC video",
            "AI LinkedIn outreach",
        ]

    all_results = []
    for idea in ideas:
        result = score_idea(idea)
        all_results.append(result)

        grade_icon = {"A": "🟢", "B": "🟡", "C": "🟠", "D": "🔴"}[result["grade"]]
        print(f"\n  {grade_icon} {result['idea']} → {result['total']}/10 (Grade {result['grade']})")
        print(f"    Ниша: {result['niche']} | Benchmark MRR: ${result['benchmark_mrr']:,} | MVP: {result['mvp_weeks']}w")
        for k, v in result["scores"].items():
            bar = "█" * int(v) + "░" * (10 - int(v))
            weight = IDEA_WEIGHTS[k]
            print(f"    {k:20s}  {v:4.1f}/10  {bar}  (×{weight})")

    # Ranking
    if len(all_results) > 1:
        print("\n  📊 Рейтинг:")
        for i, r in enumerate(sorted(all_results, key=lambda x: -x["total"]), 1):
            icon = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f" {i}."
            print(f"    {icon} {r['idea']:30s} {r['total']}/10 ({r['grade']})")

    print("\n" + "=" * 60 + "\n")

    if save_md:
        lines = [
            f"# 🎯 Idea Scorer — {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            "",
            "| Идея | Score | Grade | Ниша | Benchmark MRR | MVP |",
            "|------|:-----:|:-----:|------|:-------------:|:---:|",
        ]
        for r in sorted(all_results, key=lambda x: -x["total"]):
            lines.append(
                f"| {r['idea']} | {r['total']}/10 | {r['grade']}"
                f" | {r['niche']} | ${r['benchmark_mrr']:,} | {r['mvp_weeks']}w |"
            )
        IDEA_LOG.parent.mkdir(parents=True, exist_ok=True)
        IDEA_LOG.write_text("\n".join(lines), encoding="utf-8")
        print(f"📄 Сохранено: {IDEA_LOG}")


if __name__ == "__main__":
    main()
