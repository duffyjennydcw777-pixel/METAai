"""
🔍 Agent #36: SEO Watchdog
Мониторит SEO-позиции конкурентов: заголовки, мета, OG-теги, структура.

    python -m agents.seo_watchdog                  # Проверить SEO
    python -m agents.seo_watchdog --save           # + сохранить
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
    COMPETITORS, REPORTS_DIR,
    SCRAPE_DELAY_SECONDS, SCRAPE_USER_AGENT,
)

SEO_CACHE = REPORTS_DIR / "competitors" / "seo.json"


def audit_seo(url, name):
    """SEO аудит одного сайта."""
    result = {
        "name": name,
        "url": url,
        "score": 0,
        "checks": {},
        "issues": [],
        "audited_at": datetime.now().isoformat(),
    }

    req = urllib.request.Request(url, headers={
        "User-Agent": SCRAPE_USER_AGENT,
        "Accept": "text/html",
    })

    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            html = resp.read().decode("utf-8", errors="ignore")
    except (urllib.error.URLError, urllib.error.HTTPError) as exc:
        result["issues"].append(f"Cannot fetch: {exc}")
        return result

    checks = {}
    score = 0
    issues = []

    # 1. Title tag
    title_m = re.search(r'<title[^>]*>([^<]+)</title>', html, re.IGNORECASE)
    title = title_m.group(1).strip() if title_m else ""
    checks["title"] = title[:80]
    if title:
        score += 1
        if len(title) < 30:
            issues.append("Title слишком короткий (<30)")
        elif len(title) > 60:
            issues.append("Title слишком длинный (>60)")
        else:
            score += 1  # Optimal length
    else:
        issues.append("Title отсутствует")

    # 2. Meta description
    desc_m = re.search(
        r'<meta[^>]*name=["\']description["\'][^>]*content=["\']([^"\']+)',
        html, re.IGNORECASE
    )
    desc = desc_m.group(1).strip() if desc_m else ""
    checks["description"] = desc[:160]
    if desc:
        score += 1
        if len(desc) < 70:
            issues.append("Description слишком короткая (<70)")
        elif len(desc) > 160:
            issues.append("Description слишком длинная (>160)")
        else:
            score += 1
    else:
        issues.append("Meta description отсутствует")

    # 3. H1 tag
    h1_m = re.search(r'<h1[^>]*>([^<]+)</h1>', html, re.IGNORECASE)
    h1 = h1_m.group(1).strip() if h1_m else ""
    checks["h1"] = h1[:80]
    if h1:
        score += 1
    else:
        issues.append("H1 отсутствует")

    # 4. Open Graph
    og_title = re.search(
        r'<meta[^>]*property=["\']og:title["\'][^>]*content=["\']([^"\']+)',
        html, re.IGNORECASE
    )
    og_desc = re.search(
        r'<meta[^>]*property=["\']og:description["\'][^>]*content=["\']([^"\']+)',
        html, re.IGNORECASE
    )
    og_image = re.search(
        r'<meta[^>]*property=["\']og:image["\'][^>]*content=["\']([^"\']+)',
        html, re.IGNORECASE
    )
    checks["og_title"] = og_title.group(1)[:60] if og_title else ""
    checks["og_desc"] = og_desc.group(1)[:100] if og_desc else ""
    checks["og_image"] = bool(og_image)

    if og_title:
        score += 1
    else:
        issues.append("OG title отсутствует")
    if og_image:
        score += 1
    else:
        issues.append("OG image отсутствует")

    # 5. Canonical
    canonical = re.search(
        r'<link[^>]*rel=["\']canonical["\'][^>]*href=["\']([^"\']+)',
        html, re.IGNORECASE
    )
    checks["canonical"] = canonical.group(1)[:80] if canonical else ""
    if canonical:
        score += 1
    else:
        issues.append("Canonical отсутствует")

    # 6. robots.txt hint
    robots_m = re.search(
        r'<meta[^>]*name=["\']robots["\'][^>]*content=["\']([^"\']+)',
        html, re.IGNORECASE
    )
    checks["robots"] = robots_m.group(1) if robots_m else "not set"

    # 7. Schema.org / JSON-LD
    has_jsonld = '"@type"' in html or '"@context"' in html
    checks["schema_org"] = has_jsonld
    if has_jsonld:
        score += 1

    # 8. Mobile viewport
    viewport = re.search(
        r'<meta[^>]*name=["\']viewport["\']', html, re.IGNORECASE
    )
    checks["viewport"] = bool(viewport)
    if viewport:
        score += 1
    else:
        issues.append("Viewport не задан (mobile-unfriendly)")

    # 9. HTTPS
    if url.startswith("https://"):
        score += 1
    else:
        issues.append("Не HTTPS")

    # 10. Page size
    size_kb = len(html) / 1024
    checks["page_size_kb"] = round(size_kb, 1)
    if size_kb > 500:
        issues.append(f"Страница тяжёлая ({size_kb:.0f}KB)")

    # Final score out of 10
    result["score"] = min(score, 10)
    result["checks"] = checks
    result["issues"] = issues

    return result


def main():
    args = sys.argv[1:]
    save_md = "--save" in args

    print("\n" + "=" * 60)
    print("  🔍 SEO WATCHDOG — Phase 10 Agent #36")
    print("=" * 60)

    all_audits = {}

    for project, comps in COMPETITORS.items():
        print(f"\n  📂 {project}:")
        audits = []

        for comp in comps:
            print(f"    🔍 {comp['name']}...", end=" ", flush=True)
            audit = audit_seo(comp["url"], comp["name"])
            audits.append(audit)

            score = audit["score"]
            bar = "█" * score + "░" * (10 - score)
            issues_n = len(audit["issues"])
            print(f"{score}/10 {bar} ({issues_n} issues)")
            time.sleep(SCRAPE_DELAY_SECONDS)

        all_audits[project] = audits

    # Detailed report
    for project, audits in all_audits.items():
        print(f"\n  ── {project} SEO Report ──")
        for a in audits:
            print(f"\n    {a['name']} — {a['score']}/10")
            print(f"      Title: {a['checks'].get('title', '—')}")
            print(f"      H1:    {a['checks'].get('h1', '—')}")
            print(f"      OG:    title={'✅' if a['checks'].get('og_title') else '❌'}"
                  f" img={'✅' if a['checks'].get('og_image') else '❌'}"
                  f" schema={'✅' if a['checks'].get('schema_org') else '❌'}")
            if a["issues"]:
                for issue in a["issues"][:3]:
                    print(f"      ⚠️ {issue}")

    if save_md:
        SEO_CACHE.parent.mkdir(parents=True, exist_ok=True)
        SEO_CACHE.write_text(json.dumps({
            "audited_at": datetime.now().isoformat(),
            **all_audits,
        }, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"\n  💾 Сохранено: {SEO_CACHE}")

    print("\n" + "=" * 60 + "\n")


if __name__ == "__main__":
    main()
