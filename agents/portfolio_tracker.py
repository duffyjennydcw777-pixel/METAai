"""
📊 Agent #40: Portfolio Tracker
Отслеживает все наши проекты: стадию, MRR, здоровье, прогресс.
Даёт helicopter view на весь бизнес-портфель.

    python -m agents.portfolio_tracker              # Обзор портфеля
    python -m agents.portfolio_tracker --save       # + сохранить
"""

import json
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from agents.config import (
    PORTFOLIO_CACHE, PORTFOLIO,
    REPORTS_DIR, EVOLUTION_DIR,
)


def load_json(path):
    if path.exists():
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            pass
    return {}


def assess_project(name, config):
    """Оценивает здоровье проекта."""
    assessment = {
        "name": name,
        "type": config["type"],
        "stage": config["stage"],
        "mrr": config["mrr"],
        "url": config["url"],
        "health": 0,
        "health_label": "",
        "actions_pending": 0,
        "competitor_count": 0,
        "insights": [],
        "assessed_at": datetime.now().isoformat(),
    }

    # Кол-во задач в очереди для этого проекта
    actions_path = REPORTS_DIR / "signals" / "actions.json"
    actions_data = load_json(actions_path)
    all_actions = actions_data.get("actions", [])
    assessment["actions_pending"] = len([
        a for a in all_actions
        if a.get("status") == "pending"
    ])

    # Конкуренты
    competitors_path = REPORTS_DIR / "competitors" / "competitors.json"
    comp_data = load_json(competitors_path)
    project_comps = comp_data.get(name, [])
    assessment["competitor_count"] = len(project_comps) if isinstance(project_comps, list) else 0

    # Health score (0-10)
    health = 5  # Базовый
    stage = config["stage"]

    if stage == "growth":
        health += 2
    elif stage == "mvp":
        health += 1
    elif stage == "pre-launch":
        health -= 1

    if config["mrr"] > 0:
        health += 2
    if config["url"]:
        health += 1

    health = max(0, min(10, health))
    assessment["health"] = health

    if health >= 8:
        assessment["health_label"] = "🟢 Healthy"
    elif health >= 5:
        assessment["health_label"] = "🟡 Needs Attention"
    else:
        assessment["health_label"] = "🔴 At Risk"

    # Stage-specific insights
    if stage == "pre-launch":
        assessment["insights"].append("Нужен MVP для валидации идеи")
    elif stage == "mvp":
        assessment["insights"].append("Фокус: первые клиенты и product-market fit")
    elif stage == "growth":
        assessment["insights"].append("Фокус: масштабирование и retention")

    return assessment


def main():
    args = sys.argv[1:]
    save_md = "--save" in args

    print("\n" + "=" * 60)
    print("  📊 PORTFOLIO TRACKER — Phase 12 Agent #40")
    print("=" * 60)

    assessments = []
    total_mrr = 0

    for name, config in PORTFOLIO.items():
        assessment = assess_project(name, config)
        assessments.append(assessment)
        total_mrr += assessment["mrr"]

    # Display
    print(f"\n  {'Проект':<20s} {'Тип':<18s} {'Стадия':<12s} {'MRR':>8s} {'Health':>8s}")
    print(f"  {'─'*20} {'─'*18} {'─'*12} {'─'*8} {'─'*8}")

    for a in assessments:
        mrr_str = f"${a['mrr']:,}" if a["mrr"] > 0 else "—"
        print(f"  {a['name']:<20s} {a['type']:<18s} {a['stage']:<12s} {mrr_str:>8s} "
              f"{a['health']}/10 {a['health_label']}")

    print(f"\n  💰 Общий MRR портфеля: ${total_mrr:,}/мес")
    print(f"  📦 Проектов: {len(assessments)}")

    # Detailed view
    for a in assessments:
        print(f"\n  ── {a['name']} ──")
        print(f"    📋 Тип: {a['type']}")
        print(f"    🎯 Стадия: {a['stage']}")
        print(f"    ⚡ Задач в очереди: {a['actions_pending']}")
        print(f"    🏟️ Конкурентов: {a['competitor_count']}")
        if a["insights"]:
            for ins in a["insights"]:
                print(f"    💡 {ins}")

    # Recommendations
    print("\n  🎯 Рекомендации:")
    for a in assessments:
        if a["stage"] == "pre-launch":
            print(f"    • {a['name']}: запустить MVP для валидации спроса")
        elif a["stage"] == "mvp" and a["mrr"] == 0:
            print(f"    • {a['name']}: подключить монетизацию (Stripe/crypto)")
        elif a["stage"] == "growth":
            print(f"    • {a['name']}: масштабировать маркетинг, retention")

    if save_md:
        EVOLUTION_DIR.mkdir(parents=True, exist_ok=True)
        PORTFOLIO_CACHE.write_text(json.dumps({
            "assessed_at": datetime.now().isoformat(),
            "total_mrr": total_mrr,
            "projects": assessments,
        }, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"\n  💾 Сохранено: {PORTFOLIO_CACHE}")

    print("\n" + "=" * 60 + "\n")


if __name__ == "__main__":
    main()
