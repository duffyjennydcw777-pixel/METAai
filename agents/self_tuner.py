"""
⚙️ Agent #17: Self-Tuner
Анализирует историю и предлагает обновление порогов.

    python -m agents.self_tuner               # Dry-run (показать)
    python -m agents.self_tuner --apply       # Записать в config
    python -m agents.self_tuner --save        # + отчёт
"""

import json
import statistics
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from agents.config import (
    REPORTS_DIR, HISTORY_FILE,
    HEALTH_CRITICAL_THRESHOLD, HEALTH_WARNING_THRESHOLD,
    TREND_ALERT_DAYS,
)

CONFIG_FILE = Path(__file__).parent / "config.py"


def load_history():
    if not HISTORY_FILE.exists():
        return {}
    try:
        return json.loads(HISTORY_FILE.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}


def analyze_thresholds(history):
    """Анализирует историю и предлагает новые пороги."""
    if len(history) < 3:
        return None, "Недостаточно данных (нужно 3+ снимков)"

    # Собираем все scores
    all_scores = []
    for day_data in history.values():
        all_scores.extend(day_data.values())

    if not all_scores:
        return None, "Нет данных"

    avg = statistics.mean(all_scores)
    stdev = statistics.stdev(all_scores) if len(all_scores) > 1 else 0
    median = statistics.median(all_scores)

    proposals = []

    # Health Warning Threshold
    new_warning = round(avg - stdev)
    new_warning = max(75, min(95, new_warning))  # Clamp
    if abs(new_warning - HEALTH_WARNING_THRESHOLD) >= 3:
        proposals.append({
            "param": "HEALTH_WARNING_THRESHOLD",
            "current": HEALTH_WARNING_THRESHOLD,
            "proposed": new_warning,
            "reason": f"avg={avg:.0f}%, stdev={stdev:.1f}%,"
                      f" предлагаемый порог = avg - stdev",
        })

    # Health Critical Threshold
    new_critical = round(avg - 2 * stdev)
    new_critical = max(50, min(80, new_critical))
    if abs(new_critical - HEALTH_CRITICAL_THRESHOLD) >= 5:
        proposals.append({
            "param": "HEALTH_CRITICAL_THRESHOLD",
            "current": HEALTH_CRITICAL_THRESHOLD,
            "proposed": new_critical,
            "reason": f"avg={avg:.0f}%, предлагаемый = avg - 2×stdev",
        })

    # Trend Alert Days
    # Если все тренды короткие, уменьшить порог
    dates = sorted(history.keys())
    max_decline = 0
    for project in set().union(*[d.keys() for d in history.values()]):
        current_decline = 0
        for i in range(1, len(dates)):
            prev = history[dates[i - 1]].get(project, 0)
            curr = history[dates[i]].get(project, 0)
            if curr < prev:
                current_decline += 1
            else:
                max_decline = max(max_decline, current_decline)
                current_decline = 0
        max_decline = max(max_decline, current_decline)

    if max_decline > 0 and max_decline < TREND_ALERT_DAYS:
        proposals.append({
            "param": "TREND_ALERT_DAYS",
            "current": TREND_ALERT_DAYS,
            "proposed": max(1, max_decline),
            "reason": f"макс. зафиксированное снижение = {max_decline}д,"
                      " текущий порог не срабатывает",
        })

    stats_info = {
        "avg": round(avg, 1),
        "median": round(median, 1),
        "stdev": round(stdev, 1),
        "min": min(all_scores),
        "max": max(all_scores),
        "samples": len(all_scores),
        "days": len(history),
    }

    return proposals, stats_info


def apply_proposals(proposals):
    """Записывает предложенные пороги в config.py."""
    content = CONFIG_FILE.read_text(encoding="utf-8")
    for p in proposals:
        old = f"{p['param']} = {p['current']}"
        new = f"{p['param']} = {p['proposed']}"
        content = content.replace(old, new)
    CONFIG_FILE.write_text(content, encoding="utf-8")


def main():
    args = sys.argv[1:]
    do_apply = "--apply" in args
    save_md = "--save" in args or "--md" in args

    history = load_history()
    proposals, info = analyze_thresholds(history)

    print("\n" + "=" * 60)
    print("  ⚙️ SELF-TUNER — Phase 5 Agent #17")
    print("=" * 60)

    if isinstance(info, str):
        print(f"  ⚠️ {info}")
        print("=" * 60 + "\n")
        return

    print(f"  📊 Stats: avg={info['avg']}%, median={info['median']}%,"
          f" stdev={info['stdev']}%")
    print(f"  📏 Range: {info['min']}% — {info['max']}%"
          f" ({info['samples']} samples, {info['days']} days)")
    print()

    if not proposals:
        print("  ✅ Все пороги оптимальны, изменений не требуется")
    else:
        for p in proposals:
            print(f"  📐 {p['param']}: {p['current']} → {p['proposed']}")
            print(f"      {p['reason']}")

        if do_apply:
            apply_proposals(proposals)
            print("\n  ✅ Пороги обновлены в config.py")
        else:
            print("\n  [DRY-RUN] Добавь --apply для записи")

    print("=" * 60 + "\n")

    if save_md:
        lines = [
            f"# ⚙️ Self-Tuner Report — {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            "",
            f"Stats: avg={info['avg']}%, stdev={info['stdev']}%,"
            f" {info['samples']} samples",
            "",
        ]
        if proposals:
            lines.append("## Proposals")
            for p in proposals:
                lines.append(f"- `{p['param']}`: {p['current']} → {p['proposed']}")
                lines.append(f"  - {p['reason']}")
        else:
            lines.append("Все пороги оптимальны ✅")

        REPORTS_DIR.mkdir(parents=True, exist_ok=True)
        path = REPORTS_DIR / f"tuner_{datetime.now().strftime('%Y%m%d')}.md"
        path.write_text("\n".join(lines), encoding="utf-8")
        print(f"📄 Сохранено: {path}")


if __name__ == "__main__":
    main()
