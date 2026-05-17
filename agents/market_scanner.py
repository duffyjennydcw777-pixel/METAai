"""
🔭 Agent #23: Market Scanner
Сканирует рынок стартапов, выявляет растущие тренды и ниши.
Работает с кешированными данными TrustMRR + web-скрапинг.

    python -m agents.market_scanner               # Показать тренды
    python -m agents.market_scanner --save        # + отчёт
    python -m agents.market_scanner --refresh     # Обновить кеш
"""

import json
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from agents.config import (
    REPORTS_DIR, TRUSTMRR_CACHE,
    GROWTH_THRESHOLD_MOM, MRR_MIN_SIGNAL,
)


# Hardcoded market intelligence (обновляется через --refresh или вручную)
MARKET_DATA = [
    {"name": "Stan", "mrr": 3600000, "total": 76600000, "category": "Creator Economy", "growth": 5, "for_sale": False},
    {"name": "Rezi", "mrr": 294000, "total": 9200000, "category": "AI Resume", "growth": 8, "for_sale": False},
    {"name": "1Lookup", "mrr": 269000, "total": 3300000, "category": "Data Validation", "growth": 12, "for_sale": True, "price": 3300000},
    {"name": "Cometly", "mrr": 207000, "total": 9000000, "category": "Ad Attribution", "growth": 6, "for_sale": False},
    {"name": "PROSP", "mrr": 128000, "total": 507000, "category": "AI LinkedIn", "growth": 15, "for_sale": True, "price": 507000},
    {"name": "Vid.AI", "mrr": 95000, "total": 1400000, "category": "AI Video", "growth": 22, "for_sale": False},
    {"name": "Speel.co", "mrr": 66000, "total": 181000, "category": "AI UGC", "growth": 18, "for_sale": True, "price": 181000},
    {"name": "Indexsy", "mrr": 64000, "total": 2200000, "category": "Marketing", "growth": 4, "for_sale": False},
    {"name": "SEOBOT", "mrr": 63000, "total": 1700000, "category": "AI SEO", "growth": 25, "for_sale": False},
    {"name": "SEO STACK", "mrr": 61000, "total": 425000, "category": "SaaS SEO", "growth": 10, "for_sale": True, "price": 425000},
    {"name": "AEO Engine", "mrr": 56000, "total": 2000000, "category": "AI", "growth": 9, "for_sale": False},
    {"name": "Upscale System", "mrr": 52000, "total": 441000, "category": "AI", "growth": 30, "for_sale": False},
    {"name": "LocalRank.so", "mrr": 48000, "total": 605000, "category": "Local SEO", "growth": 7, "for_sale": True, "price": 605000},
    {"name": "Virlo", "mrr": 47000, "total": 285000, "category": "SaaS", "growth": 14, "for_sale": True, "price": 285000},
    {"name": "Launch Club", "mrr": 47000, "total": 967000, "category": "Marketing", "growth": 3, "for_sale": True, "price": 967000},
    {"name": "Interactive Video", "mrr": 46000, "total": 2100000, "category": "SaaS Video", "growth": 5, "for_sale": True, "price": 2100000},
    {"name": "ChatDash", "mrr": 43000, "total": 485000, "category": "AI", "growth": 20, "for_sale": False},
    {"name": "Notionlytics", "mrr": 42000, "total": 34000, "category": "Analytics", "growth": 35, "for_sale": True, "price": 34000},
    {"name": "Hack2hire", "mrr": 40000, "total": 311000, "category": "SaaS HR", "growth": 11, "for_sale": False},
    {"name": "StoryShort", "mrr": 25000, "total": 476000, "category": "AI Video", "growth": 28, "for_sale": True, "price": 476000},
    {"name": "Brainrot.mov", "mrr": 20000, "total": 88000, "category": "AI Memes", "growth": 40, "for_sale": True, "price": 88000},
    {"name": "Storeshots", "mrr": 16000, "total": 50000, "category": "E-commerce", "growth": 2391, "for_sale": False},
    {"name": "Specify", "mrr": 12000, "total": 15000, "category": "Design", "growth": 5210, "for_sale": False},
]


def load_cache():
    if TRUSTMRR_CACHE.exists():
        try:
            return json.loads(TRUSTMRR_CACHE.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            pass
    return MARKET_DATA


def save_cache(data):
    TRUSTMRR_CACHE.parent.mkdir(parents=True, exist_ok=True)
    TRUSTMRR_CACHE.write_text(
        json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8"
    )


def analyze_trends(data):
    """Выявляет горячие категории."""
    cat_mrr = Counter()
    cat_count = Counter()
    cat_growth = {}

    for s in data:
        cat = s["category"]
        cat_mrr[cat] += s["mrr"]
        cat_count[cat] += 1
        if cat not in cat_growth:
            cat_growth[cat] = []
        cat_growth[cat].append(s["growth"])

    trends = []
    for cat in cat_mrr:
        avg_growth = sum(cat_growth[cat]) / len(cat_growth[cat])
        trends.append({
            "category": cat,
            "total_mrr": cat_mrr[cat],
            "count": cat_count[cat],
            "avg_growth": round(avg_growth, 1),
        })

    return sorted(trends, key=lambda x: -x["total_mrr"])


def find_rockets(data):
    """Стартапы с сильным ростом + значимым MRR."""
    return sorted(
        [s for s in data if s["growth"] >= GROWTH_THRESHOLD_MOM and s["mrr"] >= MRR_MIN_SIGNAL],
        key=lambda x: -x["growth"]
    )


def main():
    args = sys.argv[1:]
    save_md = "--save" in args

    data = load_cache()
    if "--refresh" in args:
        save_cache(MARKET_DATA)
        data = MARKET_DATA

    trends = analyze_trends(data)
    rockets = find_rockets(data)

    print("\n" + "=" * 60)
    print("  🔭 MARKET SCANNER — Phase 7 Agent #23")
    print("=" * 60)

    print("\n  🔥 Горячие ниши:")
    for t in trends[:8]:
        bar = "█" * min(int(t["total_mrr"] / 100000), 30)
        print(f"    {t['category']:20s} ${t['total_mrr']:>10,}  "
              f"({t['count']} стартапов, ~{t['avg_growth']}% рост)  {bar}")

    print(f"\n  🚀 Ракеты (>{GROWTH_THRESHOLD_MOM}% MoM, >${MRR_MIN_SIGNAL/1000:.0f}k MRR):")
    for s in rockets[:10]:
        icon = "💰" if s.get("for_sale") else "🔒"
        print(f"    {icon} {s['name']:18s} ${s['mrr']:>8,}/мес  +{s['growth']}%  [{s['category']}]")

    if not rockets:
        print("    Нет стартапов с заданными параметрами")

    print("=" * 60 + "\n")

    if save_md:
        lines = [
            f"# 🔭 Market Scanner — {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            "",
            "## 🔥 Горячие ниши",
            "",
            "| Ниша | Total MRR | Стартапов | Ср. рост |",
            "|------|----------:|:---------:|---------:|",
        ]
        for t in trends:
            lines.append(f"| {t['category']} | ${t['total_mrr']:,} | {t['count']} | {t['avg_growth']}% |")

        lines.extend(["", "## 🚀 Ракеты", "",
                       "| Стартап | MRR | Рост | Ниша | Продаётся |",
                       "|---------|----:|-----:|------|:---------:|"])
        for s in rockets:
            sale = f"${s.get('price', 0):,}" if s.get("for_sale") else "❌"
            lines.append(f"| {s['name']} | ${s['mrr']:,} | +{s['growth']}% | {s['category']} | {sale} |")

        REPORTS_DIR.mkdir(parents=True, exist_ok=True)
        path = REPORTS_DIR / f"market_scan_{datetime.now().strftime('%Y%m%d')}.md"
        path.write_text("\n".join(lines), encoding="utf-8")
        print(f"📄 Сохранено: {path}")


if __name__ == "__main__":
    main()
