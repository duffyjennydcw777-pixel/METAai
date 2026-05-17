"""
🧠 Agent #39: Knowledge Distiller
Агрегирует insights из всех отчётов системы в единую базу знаний.
Выявляет паттерны, тренды, аномалии.

    python -m agents.knowledge_distiller           # Дистиллировать знания
    python -m agents.knowledge_distiller --save    # + сохранить
"""

import json
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from agents.config import (
    KNOWLEDGE_CACHE, KNOWLEDGE_MAX_INSIGHTS,
    REPORTS_DIR, EVOLUTION_DIR,
)


def load_json(path):
    """Безопасная загрузка JSON."""
    if path.exists():
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            pass
    return {}


def distill_signals():
    """Извлекает insights из сигналов."""
    insights = []
    signals_path = REPORTS_DIR / "signals" / "routed.json"
    data = load_json(signals_path)

    signals = data.get("signals", [])
    if not signals:
        return insights

    # Топ сигнал
    by_type = {}
    for s in signals:
        by_type.setdefault(s["type"], []).append(s)

    for sig_type, items in by_type.items():
        insights.append({
            "source": "signal_router",
            "type": "summary",
            "insight": f"{len(items)} сигналов типа '{sig_type}'",
            "priority": len(items),
        })

    return insights


def distill_deals():
    """Извлекает insights из оценок сделок."""
    insights = []
    deals_path = REPORTS_DIR / "signals" / "deal_evaluations.json"
    data = load_json(deals_path)

    evaluations = data.get("evaluations", [])
    for ev in evaluations:
        if ev.get("verdict") == "🟢 BUY":
            insights.append({
                "source": "deal_evaluator",
                "type": "opportunity",
                "insight": f"BUY рекомендация: {ev['name']} — {ev['total']}/10, "
                           f"${ev.get('mrr', 0):,}/мес за ${ev.get('price', 0):,}",
                "priority": ev.get("total", 0) * 10,
            })

    return insights


def distill_trends():
    """Извлекает insights из трендов."""
    insights = []
    trends_path = REPORTS_DIR / "signals" / "trend_matches.json"
    data = load_json(trends_path)

    matches = data.get("matches", [])
    # Подсчёт горячих ниш
    niche_counts = {}
    for m in matches:
        for n in m.get("niches", []):
            niche_counts[n] = niche_counts.get(n, 0) + 1

    for niche, count in sorted(niche_counts.items(), key=lambda x: -x[1]):
        if count >= 2:
            insights.append({
                "source": "trend_matcher",
                "type": "hot_niche",
                "insight": f"Горячая ниша: '{niche}' — {count} пересечений PH↔TrustMRR",
                "priority": count * 5,
            })

    return insights


def distill_competitors():
    """Извлекает insights из разведки конкурентов."""
    insights = []

    # SEO данные
    seo_path = REPORTS_DIR / "competitors" / "seo.json"
    seo_data = load_json(seo_path)

    for project in ["ONYX", "Sylectus"]:
        for audit in seo_data.get(project, []):
            if isinstance(audit, dict):
                score = audit.get("score", 0)
                name = audit.get("name", "")
                if score <= 5:
                    insights.append({
                        "source": "seo_watchdog",
                        "type": "weakness",
                        "insight": f"Слабый SEO у конкурента {name}: {score}/10 — "
                                   f"возможность обойти",
                        "priority": (10 - score) * 3,
                    })

    # Pricing данные
    pricing_path = REPORTS_DIR / "competitors" / "pricing.json"
    pricing_data = load_json(pricing_path)

    for project in ["ONYX", "Sylectus"]:
        for pricing in pricing_data.get(project, []):
            if isinstance(pricing, dict) and pricing.get("prices_found"):
                name = pricing.get("name", "")
                prices = pricing["prices_found"]
                min_p = min(prices)
                max_p = max(prices)
                insights.append({
                    "source": "pricing_monitor",
                    "type": "competitive_intel",
                    "insight": f"{name}: ценовой диапазон ${min_p}-${max_p}",
                    "priority": 5,
                })

    return insights


def distill_actions():
    """Извлекает insights из очереди задач."""
    insights = []
    actions_path = REPORTS_DIR / "signals" / "actions.json"
    data = load_json(actions_path)

    actions = data.get("actions", [])
    pending = [a for a in actions if a.get("status") == "pending"]

    if pending:
        insights.append({
            "source": "action_generator",
            "type": "backlog",
            "insight": f"{len(pending)} задач в очереди ожидают выполнения",
            "priority": len(pending) * 2,
        })

    return insights


def main():
    args = sys.argv[1:]
    save_md = "--save" in args

    print("\n" + "=" * 60)
    print("  🧠 KNOWLEDGE DISTILLER — Phase 12 Agent #39")
    print("=" * 60)

    all_insights = []

    # Собираем insights из всех источников
    sources = [
        ("Signals", distill_signals),
        ("Deals", distill_deals),
        ("Trends", distill_trends),
        ("Competitors", distill_competitors),
        ("Actions", distill_actions),
    ]

    for name, fn in sources:
        insights = fn()
        all_insights.extend(insights)
        print(f"\n  📂 {name}: {len(insights)} insights")

    # Сортировка по приоритету
    all_insights.sort(key=lambda x: -x.get("priority", 0))

    # Лимит
    all_insights = all_insights[:KNOWLEDGE_MAX_INSIGHTS]

    # Display
    print(f"\n  🧠 Всего insights: {len(all_insights)}")
    if all_insights:
        print("\n  📊 Топ-10 insights:")
        for i, ins in enumerate(all_insights[:10], 1):
            src = ins["source"][:15]
            typ = ins["type"][:12]
            text = ins["insight"][:60]
            prio = ins.get("priority", 0)
            print(f"    {i:2d}. [{src:15s}] [{typ:12s}] P{prio:>3.0f} | {text}")

    # Мета-анализ
    by_source = {}
    by_type = {}
    for ins in all_insights:
        by_source[ins["source"]] = by_source.get(ins["source"], 0) + 1
        by_type[ins["type"]] = by_type.get(ins["type"], 0) + 1

    print("\n  📈 По источникам:")
    for src, count in sorted(by_source.items(), key=lambda x: -x[1]):
        print(f"    {src:20s}: {count}")

    print("\n  🏷️ По типам:")
    for typ, count in sorted(by_type.items(), key=lambda x: -x[1]):
        print(f"    {typ:20s}: {count}")

    if save_md:
        EVOLUTION_DIR.mkdir(parents=True, exist_ok=True)
        KNOWLEDGE_CACHE.write_text(json.dumps({
            "distilled_at": datetime.now().isoformat(),
            "total": len(all_insights),
            "insights": all_insights,
            "by_source": by_source,
            "by_type": by_type,
        }, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"\n  💾 Сохранено: {KNOWLEDGE_CACHE}")

    print("\n" + "=" * 60 + "\n")


if __name__ == "__main__":
    main()
