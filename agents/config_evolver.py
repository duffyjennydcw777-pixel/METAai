"""
🔧 Agent #46: Config Evolver
Анализирует метрики Self-Tuner и предлагает изменения config.py.
Через Telegram approve → применяет изменения.

    python -m agents.config_evolver               # Предложить изменения
    python -m agents.config_evolver --save         # + сохранить
"""

import json
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from agents.config import (
    EVOLUTION_DIR, CONFIG_EVOLUTION_LOG,
    CONFIG_EVOLVER_MAX_CHANGES,
)


def load_json(path):
    if Path(path).exists():
        try:
            return json.loads(Path(path).read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            pass
    return {}


def analyze_signal_noise(metrics):
    """Анализирует signal/noise ratio и предлагает изменения."""
    proposals = []
    snr = metrics.get("signal_noise", {})
    ratio = snr.get("ratio", 0)
    quality = snr.get("quality", "ok")

    if quality == "low" and ratio < 0.02:
        proposals.append({
            "param": "SIGNAL_RULES.cheap_deal.threshold_mult",
            "current": 6,
            "proposed": 8,
            "reason": f"Signal/noise ratio слишком низкий ({ratio}). "
                      "Ослабить порог дешёвых сделок: 6× → 8× MRR",
            "severity": "medium",
        })
    elif ratio > 0.4:
        proposals.append({
            "param": "SIGNAL_RULES.cheap_deal.threshold_mult",
            "current": 6,
            "proposed": 4,
            "reason": f"Слишком много сигналов ({ratio}). "
                      "Ужесточить порог: 6× → 4× MRR",
            "severity": "medium",
        })

    return proposals


def analyze_deal_accuracy(metrics):
    """Анализирует точность Deal Evaluator."""
    proposals = []
    deals = metrics.get("deal_accuracy", {})

    if deals.get("total_evaluated", 0) > 5 and deals.get("selectivity", 0) == 0:
        proposals.append({
            "param": "DEAL_MAX_MULTIPLIER",
            "current": 8,
            "proposed": 10,
            "reason": "0 BUY сделок из >5 оценённых. "
                      "Порог мультипликатора слишком жёсткий: 8× → 10×",
            "severity": "high",
        })
    elif deals.get("selectivity", 0) > 0.5:
        proposals.append({
            "param": "DEAL_MAX_MULTIPLIER",
            "current": 8,
            "proposed": 6,
            "reason": f"Слишком много BUY ({deals.get('selectivity', 0)*100:.0f}%). "
                      "Ужесточить: 8× → 6×",
            "severity": "low",
        })

    return proposals


def analyze_scrape_success(metrics):
    """Анализирует успешность скрейпинга."""
    proposals = []
    scrape = metrics.get("scrape_success", {})

    if scrape.get("quality") == "degraded":
        # Check which feeds are failing
        feeds = scrape.get("feeds", {})
        failing = [name for name, info in feeds.items() if not info.get("ok")]
        if failing:
            proposals.append({
                "param": "SCRAPE_DELAY_SECONDS",
                "current": 2,
                "proposed": 3,
                "reason": f"Фиды {', '.join(failing)} падают. "
                          "Увеличить задержку: 2s → 3s для избежания rate-limit",
                "severity": "high",
            })

    return proposals


def analyze_action_completion(metrics):
    """Анализирует completion rate."""
    proposals = []
    actions = metrics.get("action_completion", {})

    if actions.get("pending", 0) > 10:
        proposals.append({
            "param": "MAX_ACTIONS_PER_RUN",
            "current": 5,
            "proposed": 3,
            "reason": f"Бэклог растёт ({actions.get('pending', 0)} pending). "
                      "Уменьшить генерацию: 5 → 3 задачи за цикл",
            "severity": "medium",
        })

    return proposals


def main():
    args = sys.argv[1:]
    save_md = "--save" in args

    print("\n" + "=" * 60)
    print("  🔧 CONFIG EVOLVER — Phase 13 Agent #46")
    print("=" * 60)

    # Load metrics from Self-Tuner
    tuner = load_json(EVOLUTION_DIR / "tuner.json")
    metrics = tuner.get("metrics", {})

    if not metrics:
        print("\n  ⚠️ Нет метрик. Запусти Self-Tuner: python -m agents.self_tuner --save")
        return

    # Analyze all areas
    all_proposals = []
    all_proposals.extend(analyze_signal_noise(metrics))
    all_proposals.extend(analyze_deal_accuracy(metrics))
    all_proposals.extend(analyze_scrape_success(metrics))
    all_proposals.extend(analyze_action_completion(metrics))

    # Limit
    proposals = all_proposals[:CONFIG_EVOLVER_MAX_CHANGES]

    if not proposals:
        print("\n  ✅ Все параметры оптимальны — изменений не требуется")
    else:
        print(f"\n  📊 Предложения ({len(proposals)}):")
        for i, p in enumerate(proposals, 1):
            sev_icon = "🔴" if p["severity"] == "high" else "🟡" if p["severity"] == "medium" else "🟢"
            print(f"\n  {i}. {sev_icon} {p['param']}")
            print(f"     Текущее: {p['current']} → Предложено: {p['proposed']}")
            print(f"     Причина: {p['reason']}")

    # Summary
    print("\n  📈 Системные метрики:")
    snr = metrics.get("signal_noise", {})
    print(f"    Signal/Noise: {snr.get('ratio', 0)} [{snr.get('quality', '?')}]")
    scrape = metrics.get("scrape_success", {})
    print(f"    Scrape Rate: {scrape.get('success_rate', 0)*100:.0f}% [{scrape.get('quality', '?')}]")
    actions = metrics.get("action_completion", {})
    print(f"    Action Completion: {actions.get('completion_rate', 0)*100:.0f}%")
    deals = metrics.get("deal_accuracy", {})
    print(f"    Deal Selectivity: {deals.get('selectivity', 0)*100:.0f}%")

    if save_md and proposals:
        EVOLUTION_DIR.mkdir(parents=True, exist_ok=True)
        history = load_json(CONFIG_EVOLUTION_LOG)
        if not isinstance(history, list):
            history = []

        history.append({
            "timestamp": datetime.now().isoformat(),
            "proposals": proposals,
            "applied": False,
        })
        history = history[-30:]

        Path(CONFIG_EVOLUTION_LOG).write_text(
            json.dumps(history, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        print(f"\n  💾 Сохранено: {CONFIG_EVOLUTION_LOG}")

    print("\n" + "=" * 60 + "\n")


if __name__ == "__main__":
    main()
