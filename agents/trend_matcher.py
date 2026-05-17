"""
🔗 Agent #33: Trend Matcher
Пересекает PH тренды с рыночными данными — находит ниши
для быстрого входа на основе реальных сигналов.

    python -m agents.trend_matcher                # Найти пересечения
    python -m agents.trend_matcher --save         # + сохранить
"""

import json
import re
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from agents.config import (
    TREND_MATCHES, TREND_MIN_OVERLAP,
    TRUSTMRR_FEED_CACHE, PH_FEED_CACHE,
)

# Keyword taxonomy — нормализация терминов
KEYWORD_MAP = {
    "ai": {"ai", "artificial", "intelligence", "ml", "machine", "gpt", "llm", "copilot"},
    "seo": {"seo", "search", "ranking", "google", "serp", "keyword"},
    "video": {"video", "youtube", "streaming", "creator", "ugc", "cinematic"},
    "automation": {"automation", "automate", "workflow", "pipeline", "agent", "agents"},
    "saas": {"saas", "subscription", "recurring", "platform", "tool", "sdk"},
    "marketing": {"marketing", "ads", "advertising", "growth", "outreach", "campaign"},
    "finance": {"finance", "payment", "fintech", "crypto", "trading", "invest"},
    "developer": {"developer", "dev", "code", "coding", "api", "sdk", "cli", "ide"},
    "design": {"design", "ui", "ux", "figma", "canvas", "visual"},
    "productivity": {"productivity", "task", "project", "management", "note", "memo"},
    "communication": {"communication", "chat", "messaging", "email", "voice", "screen"},
    "ecommerce": {"ecommerce", "shopify", "store", "commerce", "product"},
    "data": {"data", "analytics", "dashboard", "metrics", "insights", "monitor"},
    "security": {"security", "vpn", "privacy", "encrypt", "auth", "password"},
    "content": {"content", "blog", "writing", "article", "newsletter", "publish"},
}


def extract_categories(text):
    """Извлекает категории из текста."""
    words = set(re.findall(r'[a-z]+', text.lower()))
    categories = set()
    for cat, keywords in KEYWORD_MAP.items():
        if words & keywords:
            categories.add(cat)
    return categories


def find_matches(ph_products, trustmrr_startups):
    """Находит пересечения между PH трендами и TrustMRR стартапами."""
    matches = []

    for product in ph_products:
        ph_name = product.get("name", "")
        ph_tagline = product.get("tagline", "")
        ph_text = f"{ph_name} {ph_tagline}"
        ph_cats = extract_categories(ph_text)
        ph_votes = product.get("votes", 0) or 0

        for startup in trustmrr_startups:
            tm_name = startup.get("name", "")
            tm_desc = startup.get("description", "")
            tm_text = f"{tm_name} {tm_desc} {startup.get('slug', '')}"
            tm_cats = extract_categories(tm_text)
            tm_mrr = startup.get("mrr", 0) or 0

            overlap = ph_cats & tm_cats
            if len(overlap) >= TREND_MIN_OVERLAP:
                # Score: votes + MRR + overlap
                match_score = (
                    min(ph_votes / 50, 5) +  # Votes weight
                    min(tm_mrr / 20000, 5) +  # MRR weight
                    len(overlap)               # Category overlap
                )

                matches.append({
                    "ph_product": ph_name,
                    "ph_tagline": ph_tagline[:60],
                    "ph_votes": ph_votes,
                    "tm_startup": tm_name,
                    "tm_mrr": tm_mrr,
                    "overlap_categories": sorted(overlap),
                    "match_score": round(match_score, 1),
                    "niche_signal": " + ".join(sorted(overlap)),
                })

    # Дедупликация: best match per PH product
    seen = set()
    unique = []
    for m in sorted(matches, key=lambda x: -x["match_score"]):
        key = m["ph_product"]
        if key not in seen:
            seen.add(key)
            unique.append(m)

    return unique


def main():
    args = sys.argv[1:]
    save_md = "--save" in args

    print("\n" + "=" * 60)
    print("  🔗 TREND MATCHER — Phase 9 Agent #33")
    print("=" * 60)

    # Load data
    ph_products = []
    if PH_FEED_CACHE.exists():
        try:
            data = json.loads(PH_FEED_CACHE.read_text(encoding="utf-8"))
            ph_products = data.get("products", [])
        except (json.JSONDecodeError, OSError):
            pass

    trustmrr = []
    if TRUSTMRR_FEED_CACHE.exists():
        try:
            data = json.loads(TRUSTMRR_FEED_CACHE.read_text(encoding="utf-8"))
            trustmrr = data.get("listings", [])
        except (json.JSONDecodeError, OSError):
            pass

    print(f"\n  📥 PH продуктов: {len(ph_products)} | TrustMRR стартапов: {len(trustmrr)}")

    if not ph_products or not trustmrr:
        print("\n  📭 Нужны оба фида для матчинга.")
        print("     python -m agents.ph_tracker --save")
        print("     python -m agents.trustmrr_scraper --save")
        print("\n" + "=" * 60 + "\n")
        return

    matches = find_matches(ph_products, trustmrr)

    if matches:
        print(f"\n  🔗 Найдено {len(matches)} пересечений:")
        print(f"  {'PH Продукт':<25s} {'TrustMRR':<20s} {'Votes':>5s} {'MRR':>8s} {'Score':>5s} Ниша")
        print(f"  {'─'*25} {'─'*20} {'─'*5} {'─'*8} {'─'*5} {'─'*20}")
        for m in matches[:15]:
            ph = m["ph_product"][:25]
            tm = m["tm_startup"][:20]
            votes = m["ph_votes"]
            mrr = m["tm_mrr"]
            score = m["match_score"]
            niche = m["niche_signal"][:20]
            mrr_s = f"${mrr:>6,}" if mrr else "—"
            print(f"  {ph:<25s} {tm:<20s} {votes:>5d} {mrr_s:>8s} {score:>5.1f} {niche}")

        # Niche summary
        niche_counts = {}
        for m in matches:
            for cat in m["overlap_categories"]:
                niche_counts[cat] = niche_counts.get(cat, 0) + 1
        top_niches = sorted(niche_counts.items(), key=lambda x: -x[1])[:5]
        print(f"\n  🔥 Горячие ниши: {', '.join(f'{n}({c})' for n, c in top_niches)}")
    else:
        print("\n  📭 Нет пересечений с порогом overlap ≥ {TREND_MIN_OVERLAP}")

    if save_md and matches:
        TREND_MATCHES.parent.mkdir(parents=True, exist_ok=True)
        TREND_MATCHES.write_text(json.dumps({
            "matched_at": datetime.now().isoformat(),
            "count": len(matches),
            "matches": matches,
        }, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"\n  💾 Сохранено: {TREND_MATCHES}")

    print("\n" + "=" * 60 + "\n")


if __name__ == "__main__":
    main()
