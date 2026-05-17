"""
🎯 Agent #26: Opportunity Radar
Мониторит M&A лоты, находит недооценённые стартапы.

    python -m agents.opportunity_radar            # Показать возможности
    python -m agents.opportunity_radar --save     # + отчёт
"""

import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from agents.config import (
    REPORTS_DIR,
    MAX_MULTIPLIER_BUY, MIN_MRR_ACQUISITION,
)


# M&A listings (from TrustMRR)
LISTINGS = [
    {"name": "1Lookup", "mrr": 269000, "price": 3300000, "category": "Data Validation",
     "growth": 12, "age_months": 20, "churn_risk": "low"},
    {"name": "PROSP", "mrr": 128000, "price": 507000, "category": "AI LinkedIn",
     "growth": 15, "age_months": 14, "churn_risk": "medium"},
    {"name": "Speel.co", "mrr": 66000, "price": 181000, "category": "AI UGC",
     "growth": 18, "age_months": 10, "churn_risk": "low"},
    {"name": "SEO STACK", "mrr": 61000, "price": 425000, "category": "SaaS SEO",
     "growth": 10, "age_months": 12, "churn_risk": "low"},
    {"name": "LocalRank.so", "mrr": 48000, "price": 605000, "category": "Local SEO",
     "growth": 7, "age_months": 16, "churn_risk": "low"},
    {"name": "Virlo", "mrr": 47000, "price": 285000, "category": "SaaS",
     "growth": 14, "age_months": 8, "churn_risk": "medium"},
    {"name": "Launch Club", "mrr": 47000, "price": 967000, "category": "Marketing",
     "growth": 3, "age_months": 24, "churn_risk": "medium"},
    {"name": "Interactive Video", "mrr": 46000, "price": 2100000, "category": "SaaS Video",
     "growth": 5, "age_months": 36, "churn_risk": "low"},
    {"name": "Notionlytics", "mrr": 42000, "price": 34000, "category": "Analytics",
     "growth": 35, "age_months": 2, "churn_risk": "high"},
    {"name": "StoryShort", "mrr": 25000, "price": 476000, "category": "AI Video",
     "growth": 28, "age_months": 8, "churn_risk": "medium"},
    {"name": "Brainrot.mov", "mrr": 20000, "price": 88000, "category": "AI Memes",
     "growth": 40, "age_months": 4, "churn_risk": "high"},
]


def analyze_opportunity(listing):
    """Оценивает M&A возможность."""
    multiplier = listing["price"] / listing["mrr"] if listing["mrr"] > 0 else 999
    payback_months = listing["price"] / listing["mrr"] if listing["mrr"] > 0 else 999

    # Score components
    price_score = max(10 - multiplier, 0)  # Lower multiplier = better
    growth_score = min(listing["growth"] / 5, 10)  # Higher growth = better
    churn_penalty = {"low": 0, "medium": -1.5, "high": -3}[listing["churn_risk"]]
    age_bonus = min(listing["age_months"] / 6, 2)  # Older = more proven

    total_score = price_score + growth_score + churn_penalty + age_bonus
    total_score = max(min(total_score, 10), 0)

    return {
        **listing,
        "multiplier": round(multiplier, 1),
        "payback_months": round(payback_months, 1),
        "score": round(total_score, 1),
        "verdict": "🟢 BUY" if total_score >= 7 else
                   "🟡 CONSIDER" if total_score >= 4 else "🔴 PASS",
    }


def main():
    args = sys.argv[1:]
    save_md = "--save" in args

    # Filter and analyze
    filtered = [item for item in LISTINGS if item["mrr"] >= MIN_MRR_ACQUISITION]
    results = [analyze_opportunity(item) for item in filtered]
    results.sort(key=lambda x: -x["score"])

    # Separate by verdict
    buys = [r for r in results if r["multiplier"] <= MAX_MULTIPLIER_BUY]

    print("\n" + "=" * 60)
    print("  🎯 OPPORTUNITY RADAR — Phase 7 Agent #26")
    print("=" * 60)

    print(f"\n  Фильтр: MRR ≥ ${MIN_MRR_ACQUISITION:,}, Multiplier ≤ {MAX_MULTIPLIER_BUY}×")
    print(f"  Всего лотов: {len(LISTINGS)} | Прошли фильтр: {len(buys)}")

    print("\n  🏆 Рейтинг возможностей:")
    print(f"    {'':2s} {'Стартап':18s} {'MRR':>8s} {'Цена':>10s} {'×MRR':>5s} "
          f"{'Окуп.':>5s} {'Рост':>5s} {'Score':>5s}  Вердикт")
    print("    " + "-" * 75)

    for i, r in enumerate(buys, 1):
        churn_icon = {"low": "🟢", "medium": "🟡", "high": "🔴"}[r["churn_risk"]]
        print(f"    {i:2d}. {r['name']:18s} ${r['mrr']:>7,} ${r['price']:>9,} "
              f"{r['multiplier']:>4.1f}× {r['payback_months']:>4.1f}м "
              f"+{r['growth']:>2d}% {r['score']:>5.1f}  "
              f"{r['verdict']} {churn_icon}")

    # Best deal highlight
    if buys:
        best = buys[0]
        print(f"\n  💎 ЛУЧШАЯ СДЕЛКА: {best['name']}")
        print(f"     ${best['mrr']:,}/мес за ${best['price']:,}")
        print(f"     Окупаемость: {best['payback_months']:.0f} мес | Рост: +{best['growth']}% MoM")
        print(f"     Категория: {best['category']} | Churn risk: {best['churn_risk']}")

    # Red flags
    print("\n  ⚠️ Красные флаги:")
    for r in results:
        flags = []
        if r["churn_risk"] == "high":
            flags.append("высокий churn")
        if r["age_months"] < 3:
            flags.append("слишком молодой (<3 мес)")
        if r["multiplier"] < 2:
            flags.append("подозрительно дёшево")
        if flags:
            print(f"    🔴 {r['name']}: {', '.join(flags)}")

    print("\n" + "=" * 60 + "\n")

    if save_md:
        lines = [
            f"# 🎯 Opportunity Radar — {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            "",
            f"Фильтр: MRR ≥ ${MIN_MRR_ACQUISITION:,}, ×MRR ≤ {MAX_MULTIPLIER_BUY}",
            "",
            "| # | Стартап | MRR | Цена | ×MRR | Окуп. | Рост | Score | Вердикт |",
            "|:-:|---------|----:|-----:|:----:|:-----:|:----:|:-----:|:-------:|",
        ]
        for i, r in enumerate(buys, 1):
            lines.append(
                f"| {i} | {r['name']} | ${r['mrr']:,} | ${r['price']:,}"
                f" | {r['multiplier']}× | {r['payback_months']}м"
                f" | +{r['growth']}% | {r['score']} | {r['verdict']} |"
            )

        REPORTS_DIR.mkdir(parents=True, exist_ok=True)
        path = REPORTS_DIR / f"opportunities_{datetime.now().strftime('%Y%m%d')}.md"
        path.write_text("\n".join(lines), encoding="utf-8")
        print(f"📄 Сохранено: {path}")


if __name__ == "__main__":
    main()
