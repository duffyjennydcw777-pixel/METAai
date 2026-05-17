"""
⚡ Agent #34: Action Generator
Генерирует конкретные задачи из сигналов → Sprint Planner.
Замыкает полный цикл: Scrape → Analyze → Route → Evaluate → ACTION.

    python -m agents.action_generator              # Показать экшены
    python -m agents.action_generator --save       # + сохранить
"""

import json
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from agents.config import (
    ACTION_QUEUE, ACTION_LOG, MAX_ACTIONS_PER_RUN,
    DEAL_EVALUATIONS, TREND_MATCHES,
)


# Шаблоны задач по типу сигнала
ACTION_TEMPLATES = {
    "buy_deal": {
        "prefix": "🏪 M&A",
        "format": "Проанализировать сделку: {name} (${mrr:,}/мес за ${price:,}, {mult}×). "
                  "Зайти на TrustMRR, проверить историю MRR, связаться с продавцом.",
        "priority": "HIGH",
        "sprint_tag": "m&a",
    },
    "watch_deal": {
        "prefix": "👀 Watch",
        "format": "Мониторить: {name} — текущий MRR ${mrr:,}. "
                  "Проверить через 7 дней: MRR стабилен/растёт?",
        "priority": "MEDIUM",
        "sprint_tag": "research",
    },
    "niche_opportunity": {
        "prefix": "💡 Ниша",
        "format": "Тренд на PH: {ph_product} ({votes}▲). "
                  "Существующий игрок: {tm_startup} (${mrr:,}/мес). "
                  "Оценить: можем ли мы конкурировать в нише '{niche}'?",
        "priority": "MEDIUM",
        "sprint_tag": "research",
    },
    "build_mvp": {
        "prefix": "🛠️ Build",
        "format": "MVP: {name} — ниша {niche} горячая (пересечение PH+TrustMRR). "
                  "Benchmark MRR: ${mrr:,}/мес. Оценить MVP за 2-3 недели.",
        "priority": "HIGH",
        "sprint_tag": "build",
    },
}


def generate_from_deals():
    """Генерирует экшены из оценённых сделок."""
    actions = []
    if not DEAL_EVALUATIONS.exists():
        return actions

    try:
        data = json.loads(DEAL_EVALUATIONS.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return actions

    for ev in data.get("evaluations", []):
        verdict = ev.get("verdict", "")
        name = ev.get("name", "")
        mrr = ev.get("mrr", 0)
        price = ev.get("price", 0)
        mult = ev.get("multiplier", 0)
        total = ev.get("total", 0)

        if "BUY" in verdict:
            tpl = ACTION_TEMPLATES["buy_deal"]
            actions.append({
                "type": "buy_deal",
                "priority": tpl["priority"],
                "sprint_tag": tpl["sprint_tag"],
                "title": f"{tpl['prefix']}: {name}",
                "description": tpl["format"].format(
                    name=name, mrr=mrr, price=price, mult=f"{mult}×"
                ),
                "score": total,
                "source": "deal_evaluator",
            })
        elif "WATCH" in verdict and total >= 6.0:
            tpl = ACTION_TEMPLATES["watch_deal"]
            actions.append({
                "type": "watch_deal",
                "priority": tpl["priority"],
                "sprint_tag": tpl["sprint_tag"],
                "title": f"{tpl['prefix']}: {name}",
                "description": tpl["format"].format(name=name, mrr=mrr),
                "score": total,
                "source": "deal_evaluator",
            })

    return actions


def generate_from_trends():
    """Генерирует экшены из trend matches."""
    actions = []
    if not TREND_MATCHES.exists():
        return actions

    try:
        data = json.loads(TREND_MATCHES.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return actions

    for m in data.get("matches", [])[:5]:
        ph = m.get("ph_product", "")
        tm = m.get("tm_startup", "")
        votes = m.get("ph_votes", 0)
        mrr = m.get("tm_mrr", 0)
        niche = m.get("niche_signal", "")
        score = m.get("match_score", 0)

        if score >= 5:
            tpl = ACTION_TEMPLATES["niche_opportunity"]
            actions.append({
                "type": "niche_opportunity",
                "priority": tpl["priority"],
                "sprint_tag": tpl["sprint_tag"],
                "title": f"{tpl['prefix']}: {niche}",
                "description": tpl["format"].format(
                    ph_product=ph, votes=votes, tm_startup=tm, mrr=mrr, niche=niche
                ),
                "score": score,
                "source": "trend_matcher",
            })

    return actions


def load_history():
    """Загружает историю экшенов для дедупликации."""
    if ACTION_LOG.exists():
        try:
            return json.loads(ACTION_LOG.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            pass
    return {"actions": []}


def save_history(history):
    """Сохраняет историю."""
    ACTION_LOG.parent.mkdir(parents=True, exist_ok=True)
    # Keep last 100
    history["actions"] = history["actions"][-100:]
    ACTION_LOG.write_text(
        json.dumps(history, indent=2, ensure_ascii=False), encoding="utf-8"
    )


def main():
    args = sys.argv[1:]
    save_md = "--save" in args

    print("\n" + "=" * 60)
    print("  ⚡ ACTION GENERATOR — Phase 9 Agent #34")
    print("=" * 60)

    # Generate from all sources
    all_actions = []
    all_actions.extend(generate_from_deals())
    all_actions.extend(generate_from_trends())

    # Sort by score
    all_actions.sort(key=lambda x: -x.get("score", 0))

    # Deduplicate against history
    history = load_history()
    past_titles = {a.get("title", "") for a in history.get("actions", [])}
    new_actions = [a for a in all_actions if a["title"] not in past_titles]

    # Limit
    new_actions = new_actions[:MAX_ACTIONS_PER_RUN]

    print(f"\n  📥 Сгенерировано: {len(all_actions)} | Новых: {len(new_actions)}")

    if new_actions:
        print("\n  ⚡ Новые задачи для спринта:")
        for i, action in enumerate(new_actions, 1):
            prio_icon = "🔴" if action["priority"] == "HIGH" else "🟡"
            print(f"  {i}. {prio_icon} [{action['sprint_tag']}] {action['title']}")
            # Wrap description at ~70 chars
            desc = action["description"]
            while desc:
                print(f"     {desc[:70]}")
                desc = desc[70:]
    else:
        print("\n  ✅ Нет новых задач (всё уже в истории)")

    # Stats
    by_type = {}
    for a in all_actions:
        by_type.setdefault(a["type"], []).append(a)
    if by_type:
        print("\n  📊 По типам:")
        for t, items in by_type.items():
            print(f"    {t:20s}: {len(items)} задач")

    if save_md:
        # Save queue
        ACTION_QUEUE.parent.mkdir(parents=True, exist_ok=True)
        ACTION_QUEUE.write_text(json.dumps({
            "generated_at": datetime.now().isoformat(),
            "count": len(new_actions),
            "actions": new_actions,
        }, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"\n  💾 Очередь: {ACTION_QUEUE}")

        # Update history
        for a in new_actions:
            a["added_at"] = datetime.now().isoformat()
            history["actions"].append(a)
        save_history(history)

    print("\n" + "=" * 60 + "\n")


if __name__ == "__main__":
    main()
