"""
🏪 Agent #28: Acquire Scanner
M&A intelligence — объединяет данные из доступных источников.

Источники (приоритет):
1. TrustMRR /acquire — верифицированные стартапы на продажу
2. Ручной кеш — данные из браузера (acquire.com требует JS/auth)

    python -m agents.acquire_scanner              # Показать M&A лоты
    python -m agents.acquire_scanner --save       # + обновить кеш
    python -m agents.acquire_scanner --cached     # Только из кеша
    python -m agents.acquire_scanner --import     # Импорт из буфера обмена
"""

import json
import re
import sys
import time
import urllib.request
import urllib.error
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from agents.config import (
    ACQUIRE_FEED_CACHE, TRUSTMRR_FEED_CACHE,
    SCRAPE_DELAY_SECONDS, SCRAPE_USER_AGENT,
)


def fetch_page(url):
    """Загружает HTML-страницу."""
    req = urllib.request.Request(url, headers={
        "User-Agent": SCRAPE_USER_AGENT,
        "Accept": "text/html,application/xhtml+xml",
        "Accept-Language": "en-US,en;q=0.9",
    })
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return resp.read().decode("utf-8", errors="ignore")
    except (urllib.error.URLError, urllib.error.HTTPError) as exc:
        print(f"  ❌ Ошибка: {exc}")
        return ""


def parse_dollar(text):
    """Парсит $400k, $1.2M, $378,000 → int."""
    if not text:
        return 0
    text = str(text).strip().replace("$", "").replace(",", "").strip()
    if not text or text == "-" or text == "N/A":
        return 0
    try:
        if text.lower().endswith("k"):
            return int(float(text[:-1]) * 1000)
        if text.lower().endswith("m"):
            return int(float(text[:-1]) * 1000000)
        return int(float(text))
    except (ValueError, TypeError):
        return 0


def scrape_trustmrr_acquire():
    """Парсит TrustMRR /acquire — верифицированные стартапы на продажу."""
    url = "https://trustmrr.com/acquire"
    print(f"  🌐 TrustMRR /acquire: {url}")
    html = fetch_page(url)
    if not html:
        return []

    listings = []

    # SSR HTML: <a href="/startup/slug"> карточки
    card_pattern = re.compile(
        r'<a[^>]*href="/startup/([^"]+)"[^>]*>(.*?)</a>',
        re.DOTALL
    )
    for match in card_pattern.finditer(html):
        slug = match.group(1)
        card_html = match.group(2)

        # Имя из <h3>
        name_match = re.search(r'<h3[^>]*>([^<]+)</h3>', card_html)
        name = name_match.group(1).strip() if name_match else slug.replace("-", " ").title()

        # Метрики: font-mono значения (Revenue 30d, MRR, Total)
        metric_values = re.findall(r'font-mono[^>]*>([^<]+)<', card_html)

        mrr = 0
        revenue_30d = 0
        price = 0
        if len(metric_values) >= 3:
            revenue_30d = parse_dollar(metric_values[0])
            mrr = parse_dollar(metric_values[1])
            price = parse_dollar(metric_values[2])  # Total ≈ asking price
        elif len(metric_values) >= 1:
            mrr = parse_dollar(metric_values[0])

        listings.append({
            "name": name,
            "slug": slug,
            "mrr": mrr,
            "revenue_30d": revenue_30d,
            "price": price,
            "multiplier": f"{price / mrr / 12:.1f}×" if mrr > 0 and price > 0 else "",
            "source": "trustmrr-acquire",
        })

    with_mrr = sum(1 for item in listings if item.get("mrr", 0) > 0)
    print(f"     → {len(listings)} стартапов на продажу, {with_mrr} с MRR")
    return listings


def load_trustmrr_for_sale():
    """Загружает for-sale стартапы из TrustMRR кеша."""
    if TRUSTMRR_FEED_CACHE.exists():
        try:
            data = json.loads(TRUSTMRR_FEED_CACHE.read_text(encoding="utf-8"))
            listings = data.get("listings", [])
            # TrustMRR /acquire отдаёт стартапы с price > 0
            return [item for item in listings if item.get("total", 0) > 0
                    or item.get("price", 0) > 0]
        except (json.JSONDecodeError, OSError):
            pass
    return []


def load_cache():
    if ACQUIRE_FEED_CACHE.exists():
        try:
            data = json.loads(ACQUIRE_FEED_CACHE.read_text(encoding="utf-8"))
            return data.get("listings", []), data.get("scraped_at", "unknown")
        except (json.JSONDecodeError, OSError):
            pass
    return [], "never"


def save_cache(listings):
    ACQUIRE_FEED_CACHE.parent.mkdir(parents=True, exist_ok=True)
    ACQUIRE_FEED_CACHE.write_text(json.dumps({
        "scraped_at": datetime.now().isoformat(),
        "count": len(listings),
        "listings": listings,
    }, indent=2, ensure_ascii=False), encoding="utf-8")


def main():
    args = sys.argv[1:]
    save_md = "--save" in args
    cached_only = "--cached" in args

    print("\n" + "=" * 60)
    print("  🏪 ACQUIRE SCANNER — Phase 8 Agent #28")
    print("=" * 60)

    if cached_only:
        listings, scraped_at = load_cache()
        print(f"\n  📦 Из кеша ({scraped_at}): {len(listings)} листингов")
    else:
        all_listings = []

        # Источник 1: TrustMRR /acquire (живой скрапинг)
        trustmrr_listings = scrape_trustmrr_acquire()
        all_listings.extend(trustmrr_listings)
        time.sleep(SCRAPE_DELAY_SECONDS)

        # Источник 2: TrustMRR кеш (стартапы с ценой)
        trustmrr_cached = load_trustmrr_for_sale()
        if trustmrr_cached:
            for item in trustmrr_cached:
                item["source"] = "trustmrr-cache"
                # Нормализуем price (TrustMRR Total = total revenue, не asking price)
                if item.get("total"):
                    item["price"] = item["total"]
            print(f"  📦 TrustMRR кеш: {len(trustmrr_cached)} стартапов с revenue data")
            all_listings.extend(trustmrr_cached)

        # Источник 3: Ручной кеш Acquire.com (если есть)
        acquire_cached, cached_at = load_cache()
        if acquire_cached:
            print(f"  📦 Acquire кеш ({cached_at}): {len(acquire_cached)} листингов")
            all_listings.extend(acquire_cached)

        # Примечание: Acquire.com API заблокирован (SPA + auth + Cloudflare)
        if not trustmrr_listings and not trustmrr_cached and not acquire_cached:
            print("  ℹ️  Acquire.com требует JS/auth — данные через TrustMRR")
            print("     Для ручного импорта: python -m agents.acquire_scanner --import")

        # Дедупликация по slug/name
        seen = set()
        listings = []
        for item in all_listings:
            key = item.get("slug", "") or item.get("name", "").lower()
            if key and key not in seen:
                seen.add(key)
                listings.append(item)

        print(f"\n  📊 Итого: {len(listings)} уникальных M&A лотов")

        if save_md and listings:
            save_cache(listings)
            print(f"  💾 Кеш: {ACQUIRE_FEED_CACHE}")

    # Display
    has_mrr = [item for item in listings if item.get("mrr", 0) > 0]
    if has_mrr:
        has_mrr.sort(key=lambda x: -x["mrr"])
        print(f"\n  🏆 M&A лоты с MRR ({len(has_mrr)} из {len(listings)}):")
        print(f"    {'Стартап':<25s} {'MRR':>8s} {'Price/Total':>12s} {'×':>5s} Источник")
        print(f"    {'─'*25} {'─'*8} {'─'*12} {'─'*5} {'─'*15}")
        for item in has_mrr[:20]:
            name = item.get("name", "")[:25]
            mrr = item.get("mrr", 0)
            price = item.get("price", 0) or item.get("total", 0)
            mult = item.get("multiplier", "")
            if not mult and mrr > 0 and price > 0:
                mult = f"{price / mrr:.0f}×"
            source = item.get("source", "")[:15]
            mrr_s = f"${mrr:>6,}"
            price_s = f"${price:>10,}" if price else "—"
            print(f"    {name:<25s} {mrr_s:>8s} {price_s:>12s} {mult:>5s} {source}")
    elif listings:
        print(f"\n  📋 {len(listings)} лотов без MRR данных:")
        for item in listings[:15]:
            name = item.get("name", item.get("slug", ""))
            print(f"    📌 {name}")
    else:
        print("\n  ⚠️ Нет данных. Запусти:")
        print("     python -m agents.trustmrr_scraper --save  (заполнит TrustMRR кеш)")
        print("     python -m agents.acquire_scanner --import  (ручной импорт)")

    print("\n" + "=" * 60 + "\n")


if __name__ == "__main__":
    main()
