"""
🚀 Agent #29: ProductHunt Tracker
Трекает трендовые продукты с ProductHunt.

    python -m agents.ph_tracker                   # Сегодняшние тренды
    python -m agents.ph_tracker --save            # + кеш
    python -m agents.ph_tracker --cached          # Из кеша
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
    PH_URL, PH_FEED_CACHE,
    SCRAPE_DELAY_SECONDS, SCRAPE_USER_AGENT,
)


def fetch_page(url):
    """Загружает страницу."""
    req = urllib.request.Request(url, headers={
        "User-Agent": SCRAPE_USER_AGENT,
        "Accept": "text/html,application/xhtml+xml",
        "Accept-Language": "en-US,en;q=0.9",
    })
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            return resp.read().decode("utf-8", errors="ignore")
    except (urllib.error.URLError, urllib.error.HTTPError) as exc:
        print(f"  ❌ Ошибка: {exc}")
        return ""


def parse_ph_page(html):
    """Парсит продукты с ProductHunt.

    3 стратегии:
    1) SSR HTML cards: a[href^="/products/"] + vote buttons
    2) ApolloSSRDataTransport: streamed JSON chunks
    3) Regex fallback: /posts/ links
    """
    products = []
    if not html:
        return products

    # ─── Strategy 1: SSR HTML cards ───────────────────────
    # PH SSR: <section> карточки с <a href="/products/slug">, tagline, votes
    # Формат: "1. Product Name" → tagline → votes count

    # Ищем <a href="/posts/slug"> — это ссылки на посты
    post_links = re.findall(
        r'<a[^>]*href="/posts/([^"]+)"[^>]*>(.*?)</a>',
        html, re.DOTALL
    )

    # /products/ ссылки зарезервированы для будущего обогащения

    # Парсим из /posts/ ссылок (чаще содержат имена)
    seen_slugs = set()
    for slug, link_text in post_links:
        if slug in seen_slugs or not slug or slug.startswith("?"):
            continue
        seen_slugs.add(slug)
        # Убираем HTML теги из текста ссылки
        name = re.sub(r'<[^>]+>', '', link_text).strip()
        # Убираем нумерацию "1. "
        name = re.sub(r'^\d+\.\s*', '', name).strip()
        if not name or len(name) > 100 or len(name) < 2:
            continue

        products.append({
            "name": name,
            "slug": slug,
            "tagline": "",
            "votes": 0,
            "source": "producthunt",
        })

    # Пробуем обогатить tagline-ами из span.text-secondary
    taglines = re.findall(
        r'<span[^>]*text-secondary[^>]*>([^<]+)</span>',
        html
    )
    for i, tagline in enumerate(taglines):
        if i < len(products):
            products[i]["tagline"] = tagline.strip()[:100]

    # Пробуем обогатить votes из кнопок
    # PH votes: <button...><p>206</p></button>
    vote_counts = re.findall(
        r'<button[^>]*>(?:<[^>]+>)*?(\d+)(?:<[^>]+>)*?</button>',
        html
    )
    # Votes обычно идут парами: upvotes, comments
    vote_idx = 0
    for i in range(len(products)):
        if vote_idx < len(vote_counts):
            try:
                products[i]["votes"] = int(vote_counts[vote_idx])
            except ValueError:
                pass
            vote_idx += 2  # Пропускаем comments count

    if products:
        with_votes = sum(1 for p in products if p.get("votes", 0) > 0)
        print(f"     → Strategy 1 (SSR HTML): {len(products)} продуктов, {with_votes} с голосами")
        return products

    # ─── Strategy 2: Apollo SSR Data Transport ────────────
    # PH использует window[Symbol.for("ApolloSSRDataTransport")].push(...)
    # Данные стримятся в скриптах как JSON
    apollo_chunks = re.findall(
        r'ApolloSSRDataTransport[^{]*(\{.*?\})\s*\)',
        html, re.DOTALL
    )

    for chunk_str in apollo_chunks:
        try:
            chunk = json.loads(chunk_str)
            # Рекурсивно ищем Post объекты
            products.extend(_extract_apollo_posts(chunk))
        except (json.JSONDecodeError, ValueError):
            continue

    # Также ищем Post данные напрямую в HTML через regex
    post_matches = re.findall(
        r'"__typename"\s*:\s*"Post"[^}]*"name"\s*:\s*"([^"]+)"[^}]*"tagline"\s*:\s*"([^"]*)"',
        html
    )
    for name, tagline in post_matches:
        if name and not any(p["name"] == name for p in products):
            products.append({
                "name": name,
                "tagline": tagline[:100],
                "votes": 0,
                "source": "producthunt",
            })

    # Достаём votes из HTML для всех продуктов без голосов
    # Ищем паттерны: "votesCount":N, "latestScore":N, aria-label="N upvotes"
    vote_patterns = re.findall(
        r'"(?:votesCount|latestScore|launchDayScore)"\s*:\s*(\d+)',
        html
    )
    # Также ищем aria-label="123 upvotes"
    aria_votes = re.findall(r'aria-label="(\d+)\s*upvote', html)
    all_votes = [int(v) for v in (vote_patterns + aria_votes) if int(v) > 0]

    if all_votes and products:
        # Назначаем votes по порядку (сортировка PH = по votes desc)
        all_votes_sorted = sorted(set(all_votes), reverse=True)
        for i, prod in enumerate(products):
            if prod.get("votes", 0) == 0 and i < len(all_votes_sorted):
                prod["votes"] = all_votes_sorted[i]

    if products:
        with_votes = sum(1 for p in products if p.get("votes", 0) > 0)
        print(f"     → Strategy 2 (Apollo SSR): {len(products)} продуктов, {with_votes} с голосами")
        return products

    # ─── Strategy 3: Regex fallback ───────────────────────
    # Ищем все /products/ и /posts/ ссылки
    all_slugs = re.findall(r'href="/(?:posts|products)/([a-z0-9-]+)"', html)
    all_slugs = list(dict.fromkeys(all_slugs))  # dedupe

    for slug in all_slugs[:30]:
        name = slug.replace("-", " ").title()
        products.append({
            "name": name,
            "slug": slug,
            "tagline": "",
            "votes": 0,
            "source": "producthunt",
        })

    if products:
        print(f"     → Strategy 3 (slugs only): {len(products)} продуктов")

    return products


def _extract_apollo_posts(data, depth=0):
    """Рекурсивно извлекает Post объекты из Apollo cache."""
    posts = []
    if depth > 8:
        return posts

    if isinstance(data, dict):
        if data.get("__typename") == "Post":
            name = data.get("name", "")
            if name:
                posts.append({
                    "name": name,
                    "tagline": (data.get("tagline") or
                                data.get('tagline({"respectEmbargo":true})') or "")[:100],
                    "slug": data.get("slug", ""),
                    "votes": data.get("latestScore") or data.get("launchDayScore") or 0,
                    "comments": data.get("commentsCount", 0),
                    "source": "producthunt",
                })
        for val in data.values():
            if isinstance(val, (dict, list)):
                posts.extend(_extract_apollo_posts(val, depth + 1))
    elif isinstance(data, list):
        for item in data:
            if isinstance(item, (dict, list)):
                posts.extend(_extract_apollo_posts(item, depth + 1))

    return posts


def load_cache():
    if PH_FEED_CACHE.exists():
        try:
            data = json.loads(PH_FEED_CACHE.read_text(encoding="utf-8"))
            return data.get("products", []), data.get("scraped_at", "unknown")
        except (json.JSONDecodeError, OSError):
            pass
    return [], "never"


def save_cache(products):
    PH_FEED_CACHE.parent.mkdir(parents=True, exist_ok=True)
    PH_FEED_CACHE.write_text(json.dumps({
        "scraped_at": datetime.now().isoformat(),
        "count": len(products),
        "products": products,
    }, indent=2, ensure_ascii=False), encoding="utf-8")


def main():
    args = sys.argv[1:]
    save_md = "--save" in args
    cached_only = "--cached" in args

    print("\n" + "=" * 60)
    print("  🚀 PRODUCTHUNT TRACKER — Phase 8 Agent #29")
    print("=" * 60)

    if cached_only:
        products, scraped_at = load_cache()
        print(f"\n  📦 Из кеша ({scraped_at}): {len(products)} продуктов")
    else:
        all_products = []

        # Главная страница
        print(f"  🌐 Загрузка: {PH_URL}")
        html = fetch_page(PH_URL)
        if html:
            found = parse_ph_page(html)
            all_products.extend(found)
        time.sleep(SCRAPE_DELAY_SECONDS)

        # Leaderboard
        if not all_products:
            lb_url = f"{PH_URL}/leaderboard"
            print(f"  🌐 Загрузка: {lb_url}")
            html2 = fetch_page(lb_url)
            if html2:
                found2 = parse_ph_page(html2)
                all_products.extend(found2)

        # Дедупликация
        seen = set()
        products = []
        for p in all_products:
            key = p.get("slug", "") or p.get("name", "").lower()
            if key and key not in seen:
                seen.add(key)
                products.append(p)

        print(f"\n  📊 Итого: {len(products)} уникальных продуктов")

        if save_md and products:
            save_cache(products)
            print(f"  💾 Кеш: {PH_FEED_CACHE}")

    # Display
    if products:
        products.sort(key=lambda x: -(x.get("votes", 0) or 0))
        print("\n  🏆 Топ-15 продуктов:")
        for i, prod in enumerate(products[:15], 1):
            votes = prod.get("votes", 0)
            tagline = (prod.get("tagline", "") or "")[:45]
            vote_str = f"▲{votes:>4d}" if votes > 0 else "     "
            print(f"    {i:2d}. {vote_str}  {prod['name'][:28]:<28s}  {tagline}")
    else:
        print("\n  ⚠️ Нет данных. ProductHunt требует JS или API-ключ.")
        print("     Используй --cached для последнего кеша.")

    print("\n" + "=" * 60 + "\n")


if __name__ == "__main__":
    main()
