"""
💲 Agent #38: Pricing Monitor
Отслеживает цены конкурентов, находит pricing pages,
извлекает тарифы и детектит изменения.

    python -m agents.pricing_monitor               # Проверить цены
    python -m agents.pricing_monitor --save        # + сохранить
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
    PRICING_CACHE, COMPETITORS,
    SCRAPE_DELAY_SECONDS, SCRAPE_USER_AGENT,
)

# Пути к pricing page
PRICING_PATHS = [
    "/pricing", "/plans", "/price", "/subscribe",
    "/pricing/", "/plans/",
]

# Regex для цен
PRICE_PATTERNS = [
    r'\$\s*(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)',      # $9.99, $1,299
    r'(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)\s*/\s*mo',   # 9.99/mo
    r'(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)\s*/\s*month', # 9.99/month
    r'€\s*(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)',         # €9.99
]


def scan_pricing(comp):
    """Сканирует pricing page конкурента."""
    base_url = comp["url"].rstrip("/")
    result = {
        "name": comp["name"],
        "url": base_url,
        "pricing_url": None,
        "plans": [],
        "prices_found": [],
        "has_free_tier": False,
        "has_enterprise": False,
        "currency": "USD",
        "scanned_at": datetime.now().isoformat(),
    }

    # Найти pricing page
    pricing_html = ""
    for path in PRICING_PATHS:
        url = base_url + path
        req = urllib.request.Request(url, headers={
            "User-Agent": SCRAPE_USER_AGENT,
            "Accept": "text/html",
        })
        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                if resp.status == 200:
                    html = resp.read().decode("utf-8", errors="ignore")
                    if len(html) > 500 and ("pric" in html.lower() or "$" in html):
                        pricing_html = html
                        result["pricing_url"] = url
                        break
        except (urllib.error.URLError, urllib.error.HTTPError):
            continue
        time.sleep(1)

    # Fallback: главная страница
    if not pricing_html:
        req = urllib.request.Request(base_url, headers={
            "User-Agent": SCRAPE_USER_AGENT,
            "Accept": "text/html",
        })
        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                pricing_html = resp.read().decode("utf-8", errors="ignore")
        except (urllib.error.URLError, urllib.error.HTTPError):
            return result

    html_lower = pricing_html.lower()

    # Extract prices
    all_prices = []
    for pattern in PRICE_PATTERNS:
        matches = re.findall(pattern, pricing_html)
        for m in matches:
            try:
                price = float(m.replace(",", ""))
                if 0 < price < 100000:  # Разумный диапазон
                    all_prices.append(price)
            except ValueError:
                continue

    # Dedupe & sort
    unique_prices = sorted(set(all_prices))
    result["prices_found"] = unique_prices[:10]

    # Extract plan names — ищем рядом с ценами
    plan_names = re.findall(
        r'<(?:h[23]|div|span|p)[^>]*class=["\'][^"\']*(?:plan|tier|package|pricing)[^"\']*["\'][^>]*>'
        r'[^<]*?([A-Z][a-zA-Z\s]+)',
        pricing_html
    )
    if not plan_names:
        # Fallback: ищем common plan names
        common_plans = ["Free", "Starter", "Basic", "Pro", "Professional",
                        "Business", "Enterprise", "Premium", "Plus", "Team"]
        for plan in common_plans:
            if plan.lower() in html_lower:
                plan_names.append(plan)

    result["plans"] = list(dict.fromkeys(plan_names))[:6]

    # Free tier detection
    result["has_free_tier"] = any(
        kw in html_lower
        for kw in ["free plan", "free tier", "start free", "$0", "get started free",
                    "no credit card"]
    )

    # Enterprise detection
    result["has_enterprise"] = any(
        kw in html_lower
        for kw in ["enterprise", "contact sales", "custom pricing", "contact us"]
    )

    # Currency detection
    if "€" in pricing_html:
        result["currency"] = "EUR"
    elif "£" in pricing_html:
        result["currency"] = "GBP"

    return result


def main():
    args = sys.argv[1:]
    save_md = "--save" in args

    print("\n" + "=" * 60)
    print("  💲 PRICING MONITOR — Phase 10 Agent #38")
    print("=" * 60)

    all_pricing = {}

    for project, comps in COMPETITORS.items():
        print(f"\n  📂 {project}:")
        pricings = []

        for comp in comps:
            print(f"    💲 {comp['name']}...", end=" ", flush=True)
            pricing = scan_pricing(comp)
            pricings.append(pricing)

            prices = pricing["prices_found"]
            plans = pricing["plans"]
            has_free = "🆓" if pricing["has_free_tier"] else ""
            has_ent = "🏢" if pricing["has_enterprise"] else ""
            print(f"${min(prices) if prices else 0:.0f}-${max(prices) if prices else 0:.0f} "
                  f"| {len(plans)} plans {has_free}{has_ent}")
            time.sleep(SCRAPE_DELAY_SECONDS)

        all_pricing[project] = pricings

    # Detailed view
    for project, pricings in all_pricing.items():
        print(f"\n  ── {project} Pricing ──")
        for p in pricings:
            print(f"\n    {p['name']}")
            if p["pricing_url"]:
                print(f"      🔗 {p['pricing_url']}")
            if p["plans"]:
                print(f"      📋 Plans: {', '.join(p['plans'])}")
            if p["prices_found"]:
                print(f"      💰 Prices: {', '.join(f'${x}' for x in p['prices_found'][:6])}")
            flags = []
            if p["has_free_tier"]:
                flags.append("🆓 Free tier")
            if p["has_enterprise"]:
                flags.append("🏢 Enterprise")
            if flags:
                print(f"      🏷️ {' | '.join(flags)}")

    # Compare with previous
    if PRICING_CACHE.exists():
        try:
            prev = json.loads(PRICING_CACHE.read_text(encoding="utf-8"))
            changes = []
            for project, pricings in all_pricing.items():
                prev_pricings = {p["name"]: p for p in prev.get(project, [])}
                for p in pricings:
                    pp = prev_pricings.get(p["name"])
                    if pp:
                        old_prices = set(pp.get("prices_found", []))
                        new_prices = set(p.get("prices_found", []))
                        if old_prices != new_prices:
                            changes.append(
                                f"  ⚠️ {p['name']}: prices changed "
                                f"{sorted(old_prices)} → {sorted(new_prices)}"
                            )
            if changes:
                print("\n  🔄 Price changes detected:")
                for c in changes:
                    print(f"    {c}")
        except (json.JSONDecodeError, OSError):
            pass

    if save_md:
        PRICING_CACHE.parent.mkdir(parents=True, exist_ok=True)
        PRICING_CACHE.write_text(json.dumps({
            "scanned_at": datetime.now().isoformat(),
            **all_pricing,
        }, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"\n  💾 Сохранено: {PRICING_CACHE}")

    print("\n" + "=" * 60 + "\n")


if __name__ == "__main__":
    main()
