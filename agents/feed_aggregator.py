"""
📡 Agent #30: Feed Aggregator
Объединяет все intelligence feeds в единый отчёт.

    python -m agents.feed_aggregator              # Агрегировать все фиды
    python -m agents.feed_aggregator --save       # + Markdown отчёт
    python -m agents.feed_aggregator --notify     # + Telegram
"""

import json
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from agents.config import (
    TRUSTMRR_FEED_CACHE, ACQUIRE_FEED_CACHE, PH_FEED_CACHE,
    AGGREGATED_FEED, FEED_HISTORY,
)


def load_feed(path, key="listings"):
    """Загружает фид из кеша."""
    if not path.exists():
        return [], "never"
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        items = data.get(key, data.get("products", []))
        scraped_at = data.get("scraped_at", "unknown")
        return items, scraped_at
    except (json.JSONDecodeError, OSError):
        return [], "error"


def merge_feeds(trustmrr, acquire, ph):
    """Объединяет и ранжирует все фиды."""
    unified = []

    # TrustMRR → тип "startup"
    for item in trustmrr:
        unified.append({
            "name": item.get("name", ""),
            "mrr": item.get("mrr", 0),
            "growth": item.get("growth", 0),
            "price": item.get("price", 0),
            "for_sale": item.get("for_sale", False),
            "category": item.get("category", ""),
            "source": "TrustMRR",
            "type": "startup",
        })

    # Acquire → тип "m&a"
    for item in acquire:
        unified.append({
            "name": item.get("name", ""),
            "mrr": item.get("mrr", 0),
            "price": item.get("price", 0),
            "category": item.get("category", ""),
            "source": "Acquire",
            "type": "m&a",
            "for_sale": True,
        })

    # ProductHunt → тип "trend"
    for item in ph:
        unified.append({
            "name": item.get("name", ""),
            "tagline": item.get("tagline", ""),
            "votes": item.get("votes", 0),
            "source": "ProductHunt",
            "type": "trend",
        })

    return unified


def analyze_signals(unified):
    """Выделяет ключевые сигналы из объединённых данных."""
    signals = {
        "hot_startups": [],  # Высокий MRR + рост
        "cheap_deals": [],   # Низкий мультипликатор
        "trending": [],      # Высокий voting на PH
        "opportunities": [], # Пересечение: растущий тренд + дешёвый лот
    }

    for item in unified:
        mrr = item.get("mrr", 0) or 0
        growth = item.get("growth", 0) or 0
        price = item.get("price", 0) or 0
        votes = item.get("votes", 0) or 0

        # Hot startup: MRR > 5k + growth > 15%
        if mrr > 5000 and growth > 15:
            signals["hot_startups"].append(item)

        # Cheap deal: multiplier < 6x
        if mrr > 0 and price > 0 and price / mrr < 6:
            signals["cheap_deals"].append(item)

        # Trending: votes > 100
        if votes > 100:
            signals["trending"].append(item)

    # Sort each
    signals["hot_startups"].sort(key=lambda x: -(x.get("growth", 0) or 0))
    signals["cheap_deals"].sort(key=lambda x: (x.get("price", 0) or 0) / max(x.get("mrr", 1), 1))
    signals["trending"].sort(key=lambda x: -(x.get("votes", 0) or 0))

    return signals


def save_history(signals):
    """Сохраняет историю для трендов."""
    FEED_HISTORY.parent.mkdir(parents=True, exist_ok=True)
    history = {}
    if FEED_HISTORY.exists():
        try:
            history = json.loads(FEED_HISTORY.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            pass

    today = datetime.now().strftime("%Y-%m-%d")
    history[today] = {
        "hot_count": len(signals["hot_startups"]),
        "deals_count": len(signals["cheap_deals"]),
        "trending_count": len(signals["trending"]),
    }

    # Keep last 30 days
    keys = sorted(history.keys(), reverse=True)[:30]
    history = {k: history[k] for k in keys}

    FEED_HISTORY.write_text(
        json.dumps(history, indent=2, ensure_ascii=False), encoding="utf-8"
    )


def main():
    args = sys.argv[1:]
    save_md = "--save" in args

    print("\n" + "=" * 60)
    print("  📡 FEED AGGREGATOR — Phase 8 Agent #30")
    print("=" * 60)

    # Load all feeds
    trustmrr, tm_date = load_feed(TRUSTMRR_FEED_CACHE, "listings")
    acquire, aq_date = load_feed(ACQUIRE_FEED_CACHE, "listings")
    ph, ph_date = load_feed(PH_FEED_CACHE, "products")

    print("\n  📦 Источники:")
    print(f"    TrustMRR:     {len(trustmrr):>3d} листингов  (обновлён: {tm_date})")
    print(f"    Acquire.com:  {len(acquire):>3d} листингов  (обновлён: {aq_date})")
    print(f"    ProductHunt:  {len(ph):>3d} продуктов  (обновлён: {ph_date})")

    total = len(trustmrr) + len(acquire) + len(ph)
    print(f"\n  📊 Всего: {total} элементов")

    if total == 0:
        print("\n  ⚠️ Все фиды пустые. Запусти скраперы:")
        print("     python -m agents.trustmrr_scraper --save")
        print("     python -m agents.acquire_scanner --save")
        print("     python -m agents.ph_tracker --save")
        print("\n" + "=" * 60 + "\n")
        return

    # Merge and analyze
    unified = merge_feeds(trustmrr, acquire, ph)
    signals = analyze_signals(unified)

    # Display signals
    if signals["hot_startups"]:
        print(f"\n  🔥 Горячие стартапы ({len(signals['hot_startups'])}):")
        for item in signals["hot_startups"][:5]:
            print(f"    🚀 {item['name']:20s} ${item.get('mrr', 0):>8,}/мес"
                  f"  +{item.get('growth', 0)}%  [{item['source']}]")

    if signals["cheap_deals"]:
        print(f"\n  💰 Дешёвые сделки ({len(signals['cheap_deals'])}):")
        for item in signals["cheap_deals"][:5]:
            mrr = item.get("mrr", 0) or 1
            price = item.get("price", 0) or 0
            mult = price / mrr if mrr > 0 else 0
            print(f"    🏷️ {item['name']:20s} ${mrr:>8,}/мес"
                  f"  за ${price:>9,} ({mult:.1f}×)  [{item['source']}]")

    if signals["trending"]:
        print(f"\n  📈 Тренды ({len(signals['trending'])}):")
        for item in signals["trending"][:5]:
            print(f"    ▲{item.get('votes', 0):>4d}  {item['name']:20s}"
                  f"  {item.get('tagline', '')[:35]}  [{item['source']}]")

    if not any(signals.values()):
        print("\n  📭 Нет значимых сигналов в текущих данных")

    # Save history
    save_history(signals)

    print("\n" + "=" * 60 + "\n")

    if save_md:
        lines = [
            f"# 📡 Intelligence Report — {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            "",
            f"Источники: TrustMRR ({len(trustmrr)}), Acquire ({len(acquire)}), "
            f"ProductHunt ({len(ph)})",
            "",
        ]
        if signals["hot_startups"]:
            lines.extend(["## 🔥 Горячие стартапы", "",
                           "| Стартап | MRR | Рост | Источник |",
                           "|---------|----:|-----:|:--------:|"])
            for item in signals["hot_startups"][:10]:
                lines.append(f"| {item['name']} | ${item.get('mrr', 0):,}"
                             f" | +{item.get('growth', 0)}% | {item['source']} |")

        if signals["cheap_deals"]:
            lines.extend(["", "## 💰 Дешёвые сделки", "",
                           "| Стартап | MRR | Цена | ×MRR | Источник |",
                           "|---------|----:|-----:|:----:|:--------:|"])
            for item in signals["cheap_deals"][:10]:
                mrr = item.get("mrr", 0) or 1
                price = item.get("price", 0) or 0
                mult = price / mrr if mrr > 0 else 0
                lines.append(f"| {item['name']} | ${mrr:,} | ${price:,}"
                             f" | {mult:.1f}× | {item['source']} |")

        if signals["trending"]:
            lines.extend(["", "## 📈 Тренды ProductHunt", "",
                           "| Продукт | Votes | Описание |",
                           "|---------|:-----:|----------|"])
            for item in signals["trending"][:10]:
                lines.append(f"| {item['name']} | {item.get('votes', 0)}"
                             f" | {item.get('tagline', '')[:50]} |")

        AGGREGATED_FEED.parent.mkdir(parents=True, exist_ok=True)
        AGGREGATED_FEED.write_text("\n".join(lines), encoding="utf-8")
        print(f"📄 Сохранено: {AGGREGATED_FEED}")


if __name__ == "__main__":
    main()
