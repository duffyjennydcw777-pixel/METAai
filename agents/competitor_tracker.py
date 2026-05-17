"""
🕵️ Agent #35: Competitor Tracker
Мониторит конкурентов по проектам (ONYX, Sylectus).
Проверяет доступность, заголовки, мета-данные, технологии.

    python -m agents.competitor_tracker            # Проверить конкурентов
    python -m agents.competitor_tracker --save     # + сохранить
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
    COMPETITOR_CACHE, COMPETITORS,
    SCRAPE_DELAY_SECONDS, SCRAPE_USER_AGENT,
)


def check_competitor(comp):
    """Проверяет конкурента: доступность, title, meta, tech stack."""
    url = comp["url"]
    result = {
        "name": comp["name"],
        "url": url,
        "status": "unknown",
        "title": "",
        "description": "",
        "tech_hints": [],
        "response_time_ms": 0,
        "checked_at": datetime.now().isoformat(),
    }

    req = urllib.request.Request(url, headers={
        "User-Agent": SCRAPE_USER_AGENT,
        "Accept": "text/html",
        "Accept-Language": "en-US,en;q=0.9",
    })

    import time as t
    start = t.time()
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            elapsed = int((t.time() - start) * 1000)
            html = resp.read().decode("utf-8", errors="ignore")
            result["status"] = "online"
            result["response_time_ms"] = elapsed
            result["html_size"] = len(html)

            # Title
            title_match = re.search(r'<title[^>]*>([^<]+)</title>', html, re.IGNORECASE)
            if title_match:
                result["title"] = title_match.group(1).strip()[:100]

            # Meta description
            desc_match = re.search(
                r'<meta[^>]*name=["\']description["\'][^>]*content=["\']([^"\']+)',
                html, re.IGNORECASE
            )
            if desc_match:
                result["description"] = desc_match.group(1).strip()[:200]

            # Tech hints
            techs = []
            if "next" in html.lower() or "__next" in html:
                techs.append("Next.js")
            if "react" in html.lower():
                techs.append("React")
            if "vue" in html.lower():
                techs.append("Vue")
            if "wordpress" in html.lower() or "wp-content" in html:
                techs.append("WordPress")
            if "shopify" in html.lower():
                techs.append("Shopify")
            if "cloudflare" in html.lower():
                techs.append("Cloudflare")
            if "tailwind" in html.lower():
                techs.append("Tailwind")
            if "stripe" in html.lower():
                techs.append("Stripe")
            if "intercom" in html.lower():
                techs.append("Intercom")
            if "hotjar" in html.lower():
                techs.append("Hotjar")
            if "ga4" in html.lower() or "gtag" in html:
                techs.append("Google Analytics")

            # Pricing page hint
            if re.search(r'href=["\'][^"\']*pric', html, re.IGNORECASE):
                techs.append("Has pricing page")

            result["tech_hints"] = techs

    except urllib.error.HTTPError as exc:
        elapsed = int((t.time() - start) * 1000)
        result["status"] = f"HTTP {exc.code}"
        result["response_time_ms"] = elapsed
    except urllib.error.URLError as exc:
        result["status"] = f"error: {exc.reason}"
    except Exception as exc:
        result["status"] = f"error: {exc}"

    return result


def load_cache():
    if COMPETITOR_CACHE.exists():
        try:
            return json.loads(COMPETITOR_CACHE.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            pass
    return {}


def save_cache(data):
    COMPETITOR_CACHE.parent.mkdir(parents=True, exist_ok=True)
    COMPETITOR_CACHE.write_text(
        json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8"
    )


def main():
    args = sys.argv[1:]
    save_md = "--save" in args

    print("\n" + "=" * 60)
    print("  🕵️ COMPETITOR TRACKER — Phase 10 Agent #35")
    print("=" * 60)

    all_results = {}
    total = 0

    for project, comps in COMPETITORS.items():
        print(f"\n  📂 {project} ({len(comps)} конкурентов):")
        project_results = []

        for comp in comps:
            print(f"    🔍 {comp['name']}...", end=" ", flush=True)
            result = check_competitor(comp)
            project_results.append(result)

            status_icon = "✅" if result["status"] == "online" else "❌"
            ms = result["response_time_ms"]
            print(f"{status_icon} {ms}ms | {result['title'][:40]}")
            total += 1
            time.sleep(SCRAPE_DELAY_SECONDS)

        all_results[project] = project_results

    # Summary
    print(f"\n  📊 Итого: {total} конкурентов проверено")

    # Detailed view
    for project, results in all_results.items():
        print(f"\n  ── {project} ──")
        for r in results:
            status = r["status"]
            name = r["name"]
            tech = ", ".join(r.get("tech_hints", [])[:5]) or "—"
            desc = (r.get("description", "") or "")[:50]
            print(f"    {name:<20s} [{status}] tech: {tech}")
            if desc:
                print(f"    {'':20s} {desc}")

    # Compare with previous
    prev = load_cache()
    if prev:
        changes = []
        for project, results in all_results.items():
            prev_results = {r["name"]: r for r in prev.get(project, [])}
            for r in results:
                prev_r = prev_results.get(r["name"])
                if prev_r:
                    if prev_r.get("title") != r.get("title"):
                        changes.append(f"  ⚠️ {r['name']}: title changed → '{r['title'][:40]}'")
                    if prev_r.get("status") != r.get("status"):
                        changes.append(f"  ⚠️ {r['name']}: status {prev_r['status']} → {r['status']}")
        if changes:
            print("\n  🔄 Изменения с прошлой проверки:")
            for c in changes:
                print(f"    {c}")

    if save_md:
        save_data = {
            "checked_at": datetime.now().isoformat(),
            "total": total,
        }
        save_data.update(all_results)
        save_cache(save_data)
        print(f"\n  💾 Сохранено: {COMPETITOR_CACHE}")

    print("\n" + "=" * 60 + "\n")


if __name__ == "__main__":
    main()
