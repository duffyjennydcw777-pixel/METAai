"""
📈 Agent #25: Revenue Forecaster
Прогнозирует MRR на основе аналогов из TrustMRR.

    python -m agents.revenue_forecaster "AI SEO" 10000 25   # ниша, стартовый MRR, рост%
    python -m agents.revenue_forecaster --save
"""

import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from agents.config import REPORTS_DIR, COMPARABLE_MRR_BANDS


# Comparable exits/benchmarks
COMPARABLES = {
    "AI SEO": [
        {"name": "SEOBOT", "mrr": 63000, "age_months": 18, "growth": 25},
        {"name": "AEO Engine", "mrr": 56000, "age_months": 24, "growth": 9},
        {"name": "SEO STACK", "mrr": 61000, "age_months": 12, "growth": 10},
    ],
    "AI Video": [
        {"name": "Vid.AI", "mrr": 95000, "age_months": 15, "growth": 22},
        {"name": "Speel.co", "mrr": 66000, "age_months": 10, "growth": 18},
        {"name": "StoryShort", "mrr": 25000, "age_months": 8, "growth": 28},
    ],
    "Creator Economy": [
        {"name": "Stan", "mrr": 3600000, "age_months": 36, "growth": 5},
    ],
    "AI LinkedIn": [
        {"name": "PROSP", "mrr": 128000, "age_months": 14, "growth": 15},
    ],
    "Data Validation": [
        {"name": "1Lookup", "mrr": 269000, "age_months": 20, "growth": 12},
    ],
    "Telegram Bot Platform": [
        {"name": "Stan (analog)", "mrr": 3600000, "age_months": 36, "growth": 5},
    ],
    "VPN Data API": [
        {"name": "1Lookup (analog)", "mrr": 269000, "age_months": 20, "growth": 12},
    ],
}


def get_band(mrr):
    for low, high, label in COMPARABLE_MRR_BANDS:
        if low <= mrr < high:
            return label
    return "Unknown"


def forecast(start_mrr, monthly_growth_pct, months=12):
    """Прогноз MRR на N месяцев."""
    projections = []
    mrr = start_mrr
    total_revenue = 0
    for m in range(1, months + 1):
        mrr = mrr * (1 + monthly_growth_pct / 100)
        total_revenue += mrr
        projections.append({
            "month": m,
            "mrr": round(mrr),
            "total": round(total_revenue),
            "band": get_band(mrr),
        })
    return projections


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    save_md = "--save" in sys.argv[1:]

    # Parse args: niche, start_mrr, growth
    niche = args[0] if args else "AI SEO"
    start_mrr = int(args[1]) if len(args) > 1 else 500  # bootstrap MVP
    growth = float(args[2]) if len(args) > 2 else 20

    comps = COMPARABLES.get(niche, [])

    print("\n" + "=" * 60)
    print("  📈 REVENUE FORECASTER — Phase 7 Agent #25")
    print("=" * 60)

    print(f"\n  📌 Ниша: {niche}")
    print(f"  💰 Старт: ${start_mrr:,}/мес")
    print(f"  📊 Рост: {growth}% MoM")

    # Comparables
    if comps:
        print(f"\n  🏷️ Аналоги ({niche}):")
        for c in comps:
            print(f"    {c['name']:20s} ${c['mrr']:>8,}/мес  "
                  f"рост: {c['growth']}%  возраст: {c['age_months']}мес")
        avg_mrr = sum(c["mrr"] for c in comps) / len(comps)
        avg_growth = sum(c["growth"] for c in comps) / len(comps)
        print(f"\n    Среднее: ${avg_mrr:,.0f}/мес, рост {avg_growth:.0f}%")

    # Forecast
    proj = forecast(start_mrr, growth, 12)
    print("\n  📅 Прогноз на 12 месяцев:")
    print(f"    {'Мес':>4s}  {'MRR':>10s}  {'Всего':>12s}  Уровень")
    print("    " + "-" * 45)
    for p in proj:
        if p["month"] in [1, 3, 6, 9, 12]:
            print(f"    {p['month']:>4d}  ${p['mrr']:>9,}  ${p['total']:>11,}  {p['band']}")

    # Key milestones
    print("\n  🎯 Ключевые вехи:")
    for target in [1000, 5000, 10000, 50000, 100000]:
        if start_mrr >= target:
            continue
        for p in proj:
            if p["mrr"] >= target:
                print(f"    ${target:>7,}/мес → месяц {p['month']}")
                break
        else:
            print(f"    ${target:>7,}/мес → не достигнуто за 12 мес")

    # Valuation estimate
    final_mrr = proj[-1]["mrr"] if proj else start_mrr
    val_low = final_mrr * 24
    val_high = final_mrr * 48
    print(f"\n  💎 Оценка через 12 мес: ${val_low:,} — ${val_high:,} (24-48× MRR)")

    print("\n" + "=" * 60 + "\n")

    if save_md:
        lines = [
            f"# 📈 Revenue Forecast — {niche} — {datetime.now().strftime('%Y-%m-%d')}",
            "",
            f"Start: ${start_mrr:,} | Growth: {growth}% MoM",
            "",
            "| Месяц | MRR | Всего | Уровень |",
            "|:-----:|----:|------:|---------|",
        ]
        for p in proj:
            lines.append(f"| {p['month']} | ${p['mrr']:,} | ${p['total']:,} | {p['band']} |")

        lines.append(f"\n**Оценка 12м:** ${val_low:,} — ${val_high:,}")

        REPORTS_DIR.mkdir(parents=True, exist_ok=True)
        path = REPORTS_DIR / f"forecast_{niche.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.md"
        path.write_text("\n".join(lines), encoding="utf-8")
        print(f"📄 Сохранено: {path}")


if __name__ == "__main__":
    main()
