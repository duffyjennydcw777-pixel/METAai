"""
💰 Agent #32: Deal Evaluator
Deep-dive оценка M&A сделок из Signal Router.
Скорит каждую сделку по 6 критериям → рекомендация BUY/WATCH/SKIP.

    python -m agents.deal_evaluator               # Оценить сделки
    python -m agents.deal_evaluator --save         # + сохранить
"""

import json
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from agents.config import (
    SIGNAL_LOG, DEAL_EVALUATIONS,
    DEAL_MIN_MRR, DEAL_MAX_MULTIPLIER, DEAL_TOP_N,
    TRUSTMRR_FEED_CACHE,
)


# Скоринговые критерии
DEAL_CRITERIA = {
    "mrr_strength":     {"weight": 0.25, "desc": "MRR > $10k = хорошо"},
    "price_efficiency":  {"weight": 0.20, "desc": "Мультипликатор < 5× = отлично"},
    "growth_signal":     {"weight": 0.15, "desc": "Revenue 30d > MRR = рост"},
    "niche_fit":         {"weight": 0.15, "desc": "Пересечение с нашим стеком"},
    "risk_profile":      {"weight": 0.15, "desc": "Данных достаточно для оценки"},
    "exit_potential":     {"weight": 0.10, "desc": "Перепродажа за 2-3 года"},
}

# Наши компетенции — для niche_fit
OUR_KEYWORDS = {"ai", "seo", "bot", "telegram", "vpn", "api", "saas",
                "video", "tool", "automation", "data", "analytics",
                "linkedin", "creator", "content", "marketing"}


def score_deal(deal):
    """Оценивает сделку по 6 критериям (0-10 каждый)."""
    mrr = deal.get("mrr", 0) or 0
    price = deal.get("price", 0) or deal.get("total", 0) or 0
    rev30 = deal.get("revenue_30d", 0) or 0
    name = deal.get("name", "").lower()
    slug = deal.get("slug", "").lower()

    # 1. MRR Strength
    if mrr >= 100000:
        mrr_score = 10
    elif mrr >= 50000:
        mrr_score = 8
    elif mrr >= 20000:
        mrr_score = 6
    elif mrr >= 10000:
        mrr_score = 5
    elif mrr >= 5000:
        mrr_score = 3
    else:
        mrr_score = 1

    # 2. Price Efficiency (lower mult = better)
    if mrr > 0 and price > 0:
        mult = price / mrr
        if mult <= 3:
            price_score = 10
        elif mult <= 5:
            price_score = 8
        elif mult <= 8:
            price_score = 6
        elif mult <= 15:
            price_score = 4
        else:
            price_score = 2
    else:
        price_score = 3  # Недостаточно данных

    # 3. Growth Signal
    if rev30 > 0 and mrr > 0:
        growth_ratio = rev30 / mrr
        if growth_ratio >= 1.2:
            growth_score = 10
        elif growth_ratio >= 1.0:
            growth_score = 7
        elif growth_ratio >= 0.8:
            growth_score = 5
        else:
            growth_score = 3
    else:
        growth_score = 5  # Neutral — no data

    # 4. Niche Fit
    words = set((name + " " + slug).replace("-", " ").split())
    overlap = len(words & OUR_KEYWORDS)
    niche_score = min(overlap * 3, 10)

    # 5. Risk Profile (data completeness)
    has_mrr = mrr > 0
    has_price = price > 0
    has_rev30 = rev30 > 0
    has_name = len(name) > 3
    data_points = sum([has_mrr, has_price, has_rev30, has_name])
    risk_score = min(data_points * 2.5, 10)

    # 6. Exit Potential (can we resell at 2x in 2-3 years?)
    if mrr >= 50000 and price > 0:
        exit_score = 9  # Big enough to resell
    elif mrr >= 20000:
        exit_score = 7
    elif mrr >= 10000:
        exit_score = 5
    else:
        exit_score = 3  # Hard to resell small businesses

    scores = {
        "mrr_strength": mrr_score,
        "price_efficiency": price_score,
        "growth_signal": growth_score,
        "niche_fit": niche_score,
        "risk_profile": risk_score,
        "exit_potential": exit_score,
    }

    # Weighted total
    total = sum(scores[k] * DEAL_CRITERIA[k]["weight"] for k in scores)

    # Verdict
    if total >= 7.5:
        verdict = "🟢 BUY"
    elif total >= 5.5:
        verdict = "🟡 WATCH"
    else:
        verdict = "🔴 SKIP"

    return {
        "name": deal.get("name", ""),
        "slug": deal.get("slug", ""),
        "mrr": mrr,
        "price": price,
        "revenue_30d": rev30,
        "multiplier": round(price / mrr, 1) if mrr > 0 and price > 0 else 0,
        "scores": scores,
        "total": round(total, 2),
        "verdict": verdict,
        "evaluated_at": datetime.now().isoformat(),
    }


def load_candidates():
    """Загружает кандидатов из Signal Router или напрямую из фидов."""
    candidates = []

    # 1. Из Signal Router (приоритет)
    if SIGNAL_LOG.exists():
        try:
            data = json.loads(SIGNAL_LOG.read_text(encoding="utf-8"))
            for sig in data.get("signals", []):
                if sig.get("type") == "cheap_deal":
                    candidates.append(sig["data"])
        except (json.JSONDecodeError, OSError):
            pass

    # 2. Fallback: из TrustMRR кеша
    if not candidates and TRUSTMRR_FEED_CACHE.exists():
        try:
            data = json.loads(TRUSTMRR_FEED_CACHE.read_text(encoding="utf-8"))
            for item in data.get("listings", []):
                mrr = item.get("mrr", 0) or 0
                price = item.get("total", 0) or item.get("price", 0) or 0
                if mrr >= DEAL_MIN_MRR and price > 0:
                    mult = price / mrr
                    if mult <= DEAL_MAX_MULTIPLIER:
                        candidates.append(item)
        except (json.JSONDecodeError, OSError):
            pass

    return candidates[:DEAL_TOP_N]


def main():
    args = sys.argv[1:]
    save_md = "--save" in args

    print("\n" + "=" * 60)
    print("  💰 DEAL EVALUATOR — Phase 9 Agent #32")
    print("=" * 60)

    candidates = load_candidates()
    print(f"\n  📥 Кандидатов для оценки: {len(candidates)}")

    if not candidates:
        print("\n  📭 Нет сделок для оценки.")
        print("     Запусти: python -m agents.signal_router --save")
        print("\n" + "=" * 60 + "\n")
        return

    evaluations = []
    for deal in candidates:
        result = score_deal(deal)
        evaluations.append(result)

    evaluations.sort(key=lambda x: -x["total"])

    # Display
    print(f"\n  {'Стартап':<25s} {'MRR':>8s} {'Цена':>10s} {'×':>4s} {'Score':>6s} Вердикт")
    print(f"  {'─'*25} {'─'*8} {'─'*10} {'─'*4} {'─'*6} {'─'*10}")
    for ev in evaluations:
        name = ev["name"][:25]
        mrr = ev["mrr"]
        price = ev["price"]
        mult = ev["multiplier"]
        total = ev["total"]
        verdict = ev["verdict"]
        print(f"  {name:<25s} ${mrr:>6,} ${price:>8,} {mult:>4.1f} {total:>5.1f}/10 {verdict}")

    # Detail for top 3
    print("\n  📊 Детализация (топ-3):")
    for ev in evaluations[:3]:
        print(f"\n  {'─'*50}")
        print(f"  {ev['verdict']} {ev['name']} — {ev['total']}/10")
        for k, v in ev["scores"].items():
            bar = "█" * int(v) + "░" * (10 - int(v))
            weight = DEAL_CRITERIA[k]["weight"]
            print(f"    {k:20s} {v:4.1f}/10 {bar} (×{weight})")

    # Stats
    buys = [e for e in evaluations if "BUY" in e["verdict"]]
    watches = [e for e in evaluations if "WATCH" in e["verdict"]]
    skips = [e for e in evaluations if "SKIP" in e["verdict"]]
    print(f"\n  📈 Итого: 🟢 BUY: {len(buys)} | 🟡 WATCH: {len(watches)} | 🔴 SKIP: {len(skips)}")

    if save_md:
        DEAL_EVALUATIONS.parent.mkdir(parents=True, exist_ok=True)
        DEAL_EVALUATIONS.write_text(json.dumps({
            "evaluated_at": datetime.now().isoformat(),
            "count": len(evaluations),
            "evaluations": evaluations,
        }, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"  💾 Сохранено: {DEAL_EVALUATIONS}")

    print("\n" + "=" * 60 + "\n")


if __name__ == "__main__":
    main()
