"""
🔧 Agent #41: Self-Tuner
Анализирует эффективность системы и корректирует параметры.
Замеряет: signal-to-noise ratio, scrape success rate, action completion.

    python -m agents.self_tuner                    # Анализ
    python -m agents.self_tuner --save             # + сохранить
"""

import json
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from agents.config import (
    TUNER_CACHE, REPORTS_DIR, EVOLUTION_DIR,
)


def load_json(path):
    if path.exists():
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            pass
    return {}


def measure_signal_noise():
    """Измеряет signal-to-noise ratio."""
    signals_path = REPORTS_DIR / "signals" / "routed.json"
    data = load_json(signals_path)
    signals = data.get("signals", [])

    # Общее кол-во входных данных
    feeds = {
        "trustmrr": REPORTS_DIR / "feeds" / "trustmrr.json",
        "acquire": REPORTS_DIR / "feeds" / "acquire.json",
        "producthunt": REPORTS_DIR / "feeds" / "producthunt.json",
    }

    total_items = 0
    for feed_path in feeds.values():
        fd = load_json(feed_path)
        items = fd.get("listings", fd.get("products", []))
        total_items += len(items)

    ratio = len(signals) / total_items if total_items > 0 else 0
    return {
        "total_feed_items": total_items,
        "signals_routed": len(signals),
        "ratio": round(ratio, 3),
        "quality": "good" if ratio > 0.05 else "low" if ratio < 0.01 else "ok",
    }


def measure_action_completion():
    """Измеряет сколько задач выполнено vs сгенерировано."""
    actions_path = REPORTS_DIR / "signals" / "actions.json"
    data = load_json(actions_path)
    actions = data.get("actions", [])

    total = len(actions)
    completed = len([a for a in actions if a.get("status") == "done"])
    pending = len([a for a in actions if a.get("status") == "pending"])

    rate = completed / total if total > 0 else 0
    return {
        "total_actions": total,
        "completed": completed,
        "pending": pending,
        "completion_rate": round(rate, 3),
        "quality": "good" if rate > 0.5 else "starting" if total < 5 else "behind",
    }


def measure_scrape_success():
    """Измеряет успешность скрейпинга."""
    feeds = {
        "trustmrr": REPORTS_DIR / "feeds" / "trustmrr.json",
        "acquire": REPORTS_DIR / "feeds" / "acquire.json",
        "producthunt": REPORTS_DIR / "feeds" / "producthunt.json",
    }

    results = {}
    success = 0
    total = 0

    for name, path in feeds.items():
        total += 1
        data = load_json(path)
        items = data.get("listings", data.get("products", []))
        ok = len(items) > 0
        if ok:
            success += 1
        results[name] = {
            "items": len(items),
            "ok": ok,
            "scraped_at": data.get("scraped_at", "never"),
        }

    rate = success / total if total > 0 else 0
    return {
        "feeds": results,
        "success_rate": round(rate, 3),
        "quality": "good" if rate >= 0.8 else "degraded",
    }


def measure_deal_accuracy():
    """Измеряет точность оценки сделок."""
    deals_path = REPORTS_DIR / "signals" / "deal_evaluations.json"
    data = load_json(deals_path)
    evaluations = data.get("evaluations", [])

    buy_count = len([e for e in evaluations if "BUY" in e.get("verdict", "")])
    watch_count = len([e for e in evaluations if "WATCH" in e.get("verdict", "")])
    skip_count = len([e for e in evaluations if "SKIP" in e.get("verdict", "")])

    return {
        "total_evaluated": len(evaluations),
        "buy": buy_count,
        "watch": watch_count,
        "skip": skip_count,
        "selectivity": round(buy_count / len(evaluations), 3) if evaluations else 0,
    }


def generate_recommendations(metrics):
    """Генерирует рекомендации по самонастройке."""
    recs = []

    snr = metrics["signal_noise"]
    if snr["quality"] == "low":
        recs.append({
            "area": "signal_routing",
            "action": "Ослабить пороги сигналов — слишком мало проходит",
            "severity": "medium",
        })
    elif snr["ratio"] > 0.3:
        recs.append({
            "area": "signal_routing",
            "action": "Ужесточить пороги — слишком много шума",
            "severity": "medium",
        })

    scrape = metrics["scrape_success"]
    if scrape["quality"] == "degraded":
        recs.append({
            "area": "scrapers",
            "action": "Проверить скрейперы — часть фидов пуста",
            "severity": "high",
        })

    actions = metrics["action_completion"]
    if actions["quality"] == "behind":
        recs.append({
            "area": "execution",
            "action": "Бэклог растёт — нужно приоритизировать задачи",
            "severity": "high",
        })

    deals = metrics["deal_accuracy"]
    if deals["selectivity"] == 0 and deals["total_evaluated"] > 0:
        recs.append({
            "area": "deal_evaluation",
            "action": "Нет BUY сделок — проверить пороги или качество данных",
            "severity": "low",
        })

    return recs


def main():
    args = sys.argv[1:]
    save_md = "--save" in args

    print("\n" + "=" * 60)
    print("  🔧 SELF-TUNER — Phase 12 Agent #41")
    print("=" * 60)

    # Collect metrics
    metrics = {
        "signal_noise": measure_signal_noise(),
        "action_completion": measure_action_completion(),
        "scrape_success": measure_scrape_success(),
        "deal_accuracy": measure_deal_accuracy(),
    }

    # Display
    snr = metrics["signal_noise"]
    print("\n  📡 Signal-to-Noise Ratio:")
    print(f"    Feed items: {snr['total_feed_items']} → Signals: {snr['signals_routed']} "
          f"(ratio: {snr['ratio']}) [{snr['quality']}]")

    scrape = metrics["scrape_success"]
    print(f"\n  🌐 Scrape Success Rate: {scrape['success_rate']*100:.0f}% [{scrape['quality']}]")
    for name, info in scrape["feeds"].items():
        icon = "✅" if info["ok"] else "❌"
        print(f"    {icon} {name}: {info['items']} items")

    actions = metrics["action_completion"]
    print("\n  ⚡ Action Completion:")
    print(f"    Total: {actions['total_actions']} | Done: {actions['completed']} | "
          f"Pending: {actions['pending']} ({actions['completion_rate']*100:.0f}%) "
          f"[{actions['quality']}]")

    deals = metrics["deal_accuracy"]
    print("\n  💰 Deal Accuracy:")
    print(f"    Evaluated: {deals['total_evaluated']} | "
          f"BUY: {deals['buy']} | WATCH: {deals['watch']} | SKIP: {deals['skip']} "
          f"(selectivity: {deals['selectivity']*100:.0f}%)")

    # Recommendations
    recs = generate_recommendations(metrics)
    if recs:
        print("\n  🎯 Рекомендации по настройке:")
        for r in recs:
            sev_icon = "🔴" if r["severity"] == "high" else "🟡" if r["severity"] == "medium" else "🟢"
            print(f"    {sev_icon} [{r['area']}] {r['action']}")
    else:
        print("\n  ✅ Система работает оптимально — корректировки не нужны")

    # Overall health
    health_scores = {
        "good": 3, "ok": 2, "starting": 2,
        "low": 1, "degraded": 0, "behind": 0,
    }
    total_health = sum(
        health_scores.get(m.get("quality", "ok"), 1)
        for m in metrics.values() if isinstance(m, dict)
    )
    max_health = len(metrics) * 3
    health_pct = total_health / max_health * 100 if max_health else 0

    bar = "█" * int(health_pct / 10) + "░" * (10 - int(health_pct / 10))
    print(f"\n  🏥 System Health: {health_pct:.0f}% {bar}")

    if save_md:
        EVOLUTION_DIR.mkdir(parents=True, exist_ok=True)
        TUNER_CACHE.write_text(json.dumps({
            "tuned_at": datetime.now().isoformat(),
            "metrics": metrics,
            "recommendations": recs,
            "system_health_pct": round(health_pct, 1),
        }, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"\n  💾 Сохранено: {TUNER_CACHE}")

    print("\n" + "=" * 60 + "\n")


if __name__ == "__main__":
    main()
