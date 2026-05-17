"""
📋 Agent #37: Feature Radar
Парсит changelogs/update-страницы конкурентов — что нового.
Детектит ключевые фичи: pricing changes, new integrations, AI features.

    python -m agents.feature_radar                 # Сканировать фичи
    python -m agents.feature_radar --save          # + сохранить
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
    FEATURE_CACHE, COMPETITORS,
    SCRAPE_DELAY_SECONDS, SCRAPE_USER_AGENT,
)

# Страницы для поиска changelogs / updates
CHANGELOG_PATHS = [
    "/changelog", "/updates", "/blog", "/whats-new",
    "/release-notes", "/news",
]

# Ключевые слова фичей для детекта
FEATURE_KEYWORDS = {
    "pricing": {"pricing", "price", "plan", "free", "premium", "enterprise", "discount"},
    "ai": {"ai", "artificial", "gpt", "llm", "machine learning", "copilot", "automation"},
    "integration": {"integration", "api", "webhook", "zapier", "slack", "plugin", "sdk"},
    "security": {"security", "encryption", "privacy", "2fa", "sso", "compliance"},
    "performance": {"speed", "performance", "fast", "optimize", "cache", "cdn"},
    "mobile": {"mobile", "app", "ios", "android", "responsive"},
}


def scan_features(comp):
    """Сканирует страницы конкурента на фичи и обновления."""
    base_url = comp["url"].rstrip("/")
    result = {
        "name": comp["name"],
        "url": base_url,
        "features_found": [],
        "changelog_url": None,
        "recent_updates": [],
        "feature_categories": {},
        "scanned_at": datetime.now().isoformat(),
    }

    # Попробовать каждый changelog path
    for path in CHANGELOG_PATHS:
        url = base_url + path
        req = urllib.request.Request(url, headers={
            "User-Agent": SCRAPE_USER_AGENT,
            "Accept": "text/html",
        })

        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                if resp.status == 200:
                    html = resp.read().decode("utf-8", errors="ignore")
                    if len(html) > 1000:  # Не пустая страница
                        result["changelog_url"] = url
                        _extract_features(html, result)
                        break
        except (urllib.error.URLError, urllib.error.HTTPError):
            continue

        time.sleep(1)

    # Fallback: анализируем главную страницу
    if not result["features_found"]:
        req = urllib.request.Request(base_url, headers={
            "User-Agent": SCRAPE_USER_AGENT,
            "Accept": "text/html",
        })
        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                html = resp.read().decode("utf-8", errors="ignore")
                _extract_features(html, result)
        except (urllib.error.URLError, urllib.error.HTTPError):
            pass

    return result


def _extract_features(html, result):
    """Извлекает фичи из HTML."""
    html_lower = html.lower()

    # Находим заголовки (h2, h3) — возможные фичи
    headings = re.findall(r'<h[23][^>]*>(.*?)</h[23]>', html, re.IGNORECASE | re.DOTALL)
    for h in headings[:20]:
        clean = re.sub(r'<[^>]+>', '', h).strip()
        if 5 < len(clean) < 100:
            result["features_found"].append(clean)

    # Категоризация
    for category, keywords in FEATURE_KEYWORDS.items():
        found = []
        for kw in keywords:
            count = html_lower.count(kw)
            if count > 0:
                found.append(f"{kw}({count})")
        if found:
            result["feature_categories"][category] = found

    # Recent updates: ищем даты
    date_patterns = re.findall(
        r'(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\w*\s+\d{1,2},?\s+\d{4}',
        html
    )
    result["recent_updates"] = date_patterns[:5]


def main():
    args = sys.argv[1:]
    save_md = "--save" in args

    print("\n" + "=" * 60)
    print("  📋 FEATURE RADAR — Phase 10 Agent #37")
    print("=" * 60)

    all_scans = {}

    for project, comps in COMPETITORS.items():
        print(f"\n  📂 {project}:")
        scans = []

        for comp in comps:
            print(f"    🔍 {comp['name']}...", end=" ", flush=True)
            scan = scan_features(comp)
            scans.append(scan)

            features_n = len(scan["features_found"])
            cats = ", ".join(scan["feature_categories"].keys()) or "—"
            cl = "✅" if scan["changelog_url"] else "❌"
            print(f"{features_n} features | changelog:{cl} | {cats}")
            time.sleep(SCRAPE_DELAY_SECONDS)

        all_scans[project] = scans

    # Detailed view
    for project, scans in all_scans.items():
        print(f"\n  ── {project} Features ──")
        for scan in scans:
            print(f"\n    {scan['name']}")
            if scan["changelog_url"]:
                print(f"      📰 Changelog: {scan['changelog_url']}")
            if scan["features_found"]:
                print("      📋 Топ фичи:")
                for f in scan["features_found"][:5]:
                    print(f"        • {f[:60]}")
            if scan["feature_categories"]:
                print("      🏷️ Категории:")
                for cat, kws in scan["feature_categories"].items():
                    print(f"        {cat}: {', '.join(kws[:3])}")
            if scan["recent_updates"]:
                print(f"      📅 Updates: {', '.join(scan['recent_updates'][:3])}")

    if save_md:
        FEATURE_CACHE.parent.mkdir(parents=True, exist_ok=True)
        FEATURE_CACHE.write_text(json.dumps({
            "scanned_at": datetime.now().isoformat(),
            **all_scans,
        }, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"\n  💾 Сохранено: {FEATURE_CACHE}")

    print("\n" + "=" * 60 + "\n")


if __name__ == "__main__":
    main()
