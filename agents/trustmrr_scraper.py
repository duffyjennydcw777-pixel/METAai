"""
🔭 Agent #27: TrustMRR Scraper
Парсит листинги стартапов с TrustMRR — MRR, рост, цены.
SSR-рендер: данные прямо в HTML (Next.js App Router).

    python -m agents.trustmrr_scraper              # Скрапить и показать
    python -m agents.trustmrr_scraper --save       # + сохранить кеш
    python -m agents.trustmrr_scraper --cached     # Только из кеша
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
    TRUSTMRR_URL, TRUSTMRR_FEED_CACHE,
    SCRAPE_DELAY_SECONDS, SCRAPE_USER_AGENT,
)


def fetch_page(url):
    """Загружает HTML-страницу с rate limiting."""
    req = urllib.request.Request(url, headers={
        "User-Agent": SCRAPE_USER_AGENT,
        "Accept": "text/html,application/xhtml+xml",
        "Accept-Language": "en-US,en;q=0.9",
    })
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            return resp.read().decode("utf-8", errors="ignore")
    except (urllib.error.URLError, urllib.error.HTTPError) as exc:
        print(f"  ❌ Ошибка загрузки {url}: {exc}")
        return ""


def parse_dollar(text):
    """Парсит $X,XXX или $X.Xk формат в int."""
    if not text:
        return 0
    text = text.strip().replace("$", "").replace(",", "").strip()
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


def parse_trustmrr_html(html):
    """Парсит листинги из SSR HTML TrustMRR.

    3 стратегии:
    1) SSR HTML карточки: <a href="/startup/..."> → <h3> + grid metrics
    2) RSC stream: self.__next_f.push → JSON-подобные объекты
    3) Regex fallback: $X,XXX рядом со slug-ами
    """
    listings = []
    if not html:
        return listings

    # ─── Strategy 1: SSR HTML cards ───────────────────────
    # TrustMRR SSR: <a href="/startup/slug"> → <h3>Name</h3> → grid-cols-3 metrics
    # Карточка: a[href^="/startup/"] содержит h3 (имя) и p.font-mono (метрики)
    # Метрики в grid: Revenue 30d | MRR | Total

    # Разбиваем HTML на блоки по карточкам
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

        # Метрики: ищем все font-mono значения (Revenue 30d, MRR, Total)
        metric_values = re.findall(r'font-mono[^>]*>([^<]+)<', card_html)

        mrr = 0
        revenue_30d = 0
        total = 0
        if len(metric_values) >= 3:
            revenue_30d = parse_dollar(metric_values[0])
            mrr = parse_dollar(metric_values[1])
            total = parse_dollar(metric_values[2])
        elif len(metric_values) >= 1:
            # Берём первое как MRR
            mrr = parse_dollar(metric_values[0])

        # Описание
        desc_match = re.search(r'text-muted-foreground[^>]*>([^<]+)<', card_html)
        description = desc_match.group(1).strip() if desc_match else ""

        listings.append({
            "name": name,
            "slug": slug,
            "mrr": mrr,
            "revenue_30d": revenue_30d,
            "total": total,
            "description": description,
            "source": "trustmrr",
        })

    if listings:
        with_mrr = sum(1 for item in listings if item.get("mrr", 0) > 0)
        print(f"     → Strategy 1 (SSR HTML): {len(listings)} карточек, {with_mrr} с MRR")
        return listings

    # ─── Strategy 2: RSC stream parsing ───────────────────
    # Next.js App Router: self.__next_f.push([1,"..."]) содержит RSC payload
    startup_slugs = re.findall(r'href="/startup/([^"]+)"', html)
    startup_slugs = list(dict.fromkeys(startup_slugs))

    next_chunks = re.findall(r'self\.__next_f\.push\(\[1,"([^"]*?)"\]\)', html)
    full_stream = "".join(next_chunks)

    # Парсим JSON объекты с revenue/mrr данными
    json_candidates = re.findall(
        r'\{[^{}]*(?:"revenue"|"mrr"|"monthlyRevenue"|"monthly_revenue")[^{}]*\}',
        full_stream
    )
    for candidate in json_candidates:
        try:
            clean = candidate.replace('\\"', '"').replace('\\\\', '\\')
            obj = json.loads(clean)
            name = obj.get("name") or obj.get("title") or obj.get("startup_name", "")
            mrr = obj.get("mrr") or obj.get("monthlyRevenue") or obj.get("monthly_revenue") or obj.get("revenue", 0)
            if name and mrr:
                listings.append({
                    "name": str(name),
                    "mrr": int(float(str(mrr).replace(",", ""))) if mrr else 0,
                    "growth": obj.get("growth", obj.get("revenueGrowth", 0)) or 0,
                    "category": obj.get("category", obj.get("niche", "")) or "",
                    "price": obj.get("askingPrice", obj.get("price", 0)) or 0,
                    "source": "trustmrr",
                })
        except (json.JSONDecodeError, ValueError):
            continue

    if listings:
        print(f"     → Strategy 2 (RSC stream): {len(listings)} стартапов с MRR")
        return listings

    # Также ищем данные в RSC потоке по паттерну: slug + dollar amounts nearby
    # RSC может содержать: ["$slug","$L12",["$","h3",null,...,"StartupName"],...,"$3,600"]
    for slug in startup_slugs:
        slug_pattern = re.compile(
            re.escape(slug) + r'.*?\$\s*([\d,.]+[kKmM]?)',
            re.DOTALL
        )
        slug_match = slug_pattern.search(full_stream[:50000])  # Limit search range
        if slug_match:
            mrr = parse_dollar(slug_match.group(1))
            if mrr > 0:
                listings.append({
                    "name": slug.replace("-", " ").title(),
                    "slug": slug,
                    "mrr": mrr,
                    "source": "trustmrr",
                })

    if listings:
        print(f"     → Strategy 2b (RSC slug+$): {len(listings)} стартапов")
        return listings

    # ─── Strategy 3: Regex fallback ───────────────────────
    # Ищем все $X,XXX суммы и пытаемся привязать к slug-ам
    all_amounts = re.findall(r'\$([\d,]+(?:\.\d+)?[kKmM]?)', html)
    revenue_amounts = []
    for a in all_amounts:
        val = parse_dollar(a)
        if 100 <= val <= 50000000:
            revenue_amounts.append(val)

    if revenue_amounts:
        print(f"     → Найдено {len(revenue_amounts)} денежных сумм (не структурированы)")

    # Последний fallback: slug-only (для детального парсинга позже)
    if not listings and startup_slugs:
        for slug in startup_slugs[:50]:
            listings.append({
                "name": slug.replace("-", " ").title(),
                "slug": slug,
                "mrr": 0,
                "source": "trustmrr",
            })
        print(f"     → Strategy 3 (slugs only): {len(listings)} стартапов без MRR")

    return listings


def load_cache():
    """Загружает кеш."""
    if TRUSTMRR_FEED_CACHE.exists():
        try:
            data = json.loads(TRUSTMRR_FEED_CACHE.read_text(encoding="utf-8"))
            return data.get("listings", []), data.get("scraped_at", "unknown")
        except (json.JSONDecodeError, OSError):
            pass
    return [], "never"


def save_cache(listings):
    """Сохраняет в кеш."""
    TRUSTMRR_FEED_CACHE.parent.mkdir(parents=True, exist_ok=True)
    TRUSTMRR_FEED_CACHE.write_text(json.dumps({
        "scraped_at": datetime.now().isoformat(),
        "count": len(listings),
        "listings": listings,
    }, indent=2, ensure_ascii=False), encoding="utf-8")


def main():
    args = sys.argv[1:]
    save_md = "--save" in args
    cached_only = "--cached" in args

    print("\n" + "=" * 60)
    print("  🔭 TRUSTMRR SCRAPER — Phase 8 Agent #27")
    print("=" * 60)

    if cached_only:
        listings, scraped_at = load_cache()
        print(f"\n  📦 Из кеша ({scraped_at}): {len(listings)} листингов")
    else:
        # Правильные URL для TrustMRR (SSR, Next.js App Router)
        pages = [
            "/acquire",  # Главный листинг (for sale)
            "/category/saas",
            "/category/ai",  # Проверенный slug
        ]
        all_listings = []
        for page in pages:
            url = TRUSTMRR_URL + page
            print(f"  🌐 Загрузка: {url}")
            html = fetch_page(url)
            if html:
                found = parse_trustmrr_html(html)
                all_listings.extend(found)
            time.sleep(SCRAPE_DELAY_SECONDS)

        # Дедупликация по slug
        seen = set()
        listings = []
        for item in all_listings:
            key = item.get("slug", "") or item.get("name", "").lower()
            if key and key not in seen:
                seen.add(key)
                listings.append(item)

        print(f"\n  📊 Итого: {len(listings)} уникальных элементов")

        if save_md and listings:
            save_cache(listings)
            print(f"  💾 Кеш сохранён: {TRUSTMRR_FEED_CACHE}")

    # Display
    has_mrr = [item for item in listings if item.get("mrr", 0) > 0]
    if has_mrr:
        has_mrr.sort(key=lambda x: -x["mrr"])
        print(f"\n  🏆 Топ-15 по MRR ({len(has_mrr)} с данными):")
        print(f"    {'Стартап':<22s} {'Rev 30d':>10s} {'MRR':>10s} {'Total':>12s}")
        print(f"    {'─'*22} {'─'*10} {'─'*10} {'─'*12}")
        for item in has_mrr[:15]:
            name = item.get("name", "")[:22]
            rev = item.get("revenue_30d", 0)
            mrr = item.get("mrr", 0)
            total = item.get("total", 0)
            rev_s = f"${rev:>8,}" if rev else "—"
            mrr_s = f"${mrr:>8,}"
            total_s = f"${total:>10,}" if total else "—"
            print(f"    {name:<22s} {rev_s:>10s} {mrr_s:>10s} {total_s:>12s}")
    elif listings:
        print(f"\n  📋 {len(listings)} стартапов (без MRR — нужен детальный парсинг):")
        for item in listings[:15]:
            name = item.get("name", item.get("slug", ""))
            print(f"    📌 {name}")
    else:
        print("\n  ⚠️ Нет данных. Сайт мог заблокировать запрос или изменить структуру.")
        print("     Используй --cached для работы с последним кешем.")

    print("\n" + "=" * 60 + "\n")


if __name__ == "__main__":
    main()
