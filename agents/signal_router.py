"""
🔀 Agent #31: Signal Router
Маршрутизирует сигналы из Feed Aggregator к нужным агентам.
Замыкает цикл: scrape → analyze → route → action.

    python -m agents.signal_router                # Роутить сигналы
    python -m agents.signal_router --save         # + сохранить лог
"""

import json
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from agents.config import (
    SIGNAL_LOG, SIGNAL_RULES,
    TRUSTMRR_FEED_CACHE, ACQUIRE_FEED_CACHE, PH_FEED_CACHE,
)


def load_feed(path, key="listings"):
    """Загружает фид из кеша."""
    if not path.exists():
        return []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return data.get(key, data.get("products", []))
    except (json.JSONDecodeError, OSError):
        return []


def classify_signals(trustmrr, acquire, ph):
    """Классифицирует сигналы по правилам из config."""
    signals = []
    seen_names = set()  # Дедупликация по имени

    cheap_thresh = SIGNAL_RULES["cheap_deal"]["threshold_mult"]
    mrr_thresh = SIGNAL_RULES["high_mrr"]["threshold_mrr"]
    votes_thresh = SIGNAL_RULES["hot_trend"]["threshold_votes"]

    # M&A сигналы: дешёвые сделки (TrustMRR приоритет, acquire = fallback)
    for source_name, items in [("trustmrr", trustmrr), ("acquire", acquire)]:
        for item in items:
            name = (item.get("name", "") or item.get("slug", "")).lower().strip()
            if name in seen_names:
                continue

            mrr = item.get("mrr", 0) or 0
            price = item.get("price", 0) or item.get("total", 0) or 0
            if mrr > 0 and price > 0:
                mult = price / mrr
                if mult <= cheap_thresh:
                    seen_names.add(name)
                    signals.append({
                        "type": "cheap_deal",
                        "route_to": "deal_evaluator",
                        "priority": round(cheap_thresh - mult, 1),
                        "data": {
                            "name": item.get("name", ""),
                            "slug": item.get("slug", ""),
                            "mrr": mrr,
                            "revenue_30d": item.get("revenue_30d", 0),
                            "price": price,
                            "multiplier": round(mult, 1),
                            "source": source_name,
                        },
                    })

    # High MRR сигналы: потенциальные конкуренты или вдохновение
    for item in trustmrr:
        mrr = item.get("mrr", 0) or 0
        name = (item.get("name", "") or "").lower().strip()
        if mrr >= mrr_thresh and name not in seen_names:
            seen_names.add(name)
            signals.append({
                "type": "high_mrr",
                "route_to": "idea_scorer",
                "priority": mrr / 10000,
                "data": {
                    "name": item.get("name", ""),
                    "mrr": mrr,
                    "description": item.get("description", ""),
                    "source": "trustmrr",
                },
            })

    # Trending сигналы: горячие продукты на PH
    for item in ph:
        votes = item.get("votes", 0) or 0
        if votes >= votes_thresh:
            signals.append({
                "type": "hot_trend",
                "route_to": "trend_matcher",
                "priority": votes / 100,
                "data": {
                    "name": item.get("name", ""),
                    "tagline": item.get("tagline", ""),
                    "votes": votes,
                    "source": "producthunt",
                },
            })

    # Сортировка по приоритету
    signals.sort(key=lambda x: -x["priority"])
    return signals


def save_signals(signals):
    """Сохраняет маршрутизированные сигналы."""
    SIGNAL_LOG.parent.mkdir(parents=True, exist_ok=True)
    SIGNAL_LOG.write_text(json.dumps({
        "routed_at": datetime.now().isoformat(),
        "count": len(signals),
        "signals": signals,
    }, indent=2, ensure_ascii=False), encoding="utf-8")


def main():
    args = sys.argv[1:]
    save_md = "--save" in args

    print("\n" + "=" * 60)
    print("  🔀 SIGNAL ROUTER — Phase 9 Agent #31")
    print("=" * 60)

    # Load feeds
    trustmrr = load_feed(TRUSTMRR_FEED_CACHE, "listings")
    acquire = load_feed(ACQUIRE_FEED_CACHE, "listings")
    ph = load_feed(PH_FEED_CACHE, "products")

    print("\n  📥 Входные данные:")
    print(f"    TrustMRR:    {len(trustmrr):>3d} элементов")
    print(f"    Acquire:     {len(acquire):>3d} элементов")
    print(f"    ProductHunt: {len(ph):>3d} элементов")

    # Classify
    signals = classify_signals(trustmrr, acquire, ph)

    # Stats
    by_type = {}
    for s in signals:
        by_type.setdefault(s["type"], []).append(s)

    print(f"\n  📡 Сигналы ({len(signals)} всего):")
    for sig_type, items in by_type.items():
        route = items[0]["route_to"] if items else "?"
        print(f"    {sig_type:15s} → {route:20s} ({len(items)} шт)")

    # Display top signals
    if signals:
        print("\n  🔥 Топ-10 сигналов:")
        for i, sig in enumerate(signals[:10], 1):
            name = sig["data"].get("name", "")[:30]
            typ = sig["type"]
            if typ == "cheap_deal":
                detail = f"{sig['data']['multiplier']}× (${sig['data']['mrr']:,}/мес)"
            elif typ == "high_mrr":
                detail = f"${sig['data']['mrr']:,}/мес"
            else:
                detail = f"▲{sig['data'].get('votes', 0)}"
            print(f"    {i:2d}. [{typ:12s}] {name:<30s} {detail}")

    if save_md and signals:
        save_signals(signals)
        print(f"\n  💾 Сохранено: {SIGNAL_LOG}")

    print("\n" + "=" * 60 + "\n")


if __name__ == "__main__":
    main()
