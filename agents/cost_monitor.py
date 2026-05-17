"""
💲 Agent #20: Cost Monitor
Трекает расходы на AI API из логов review-агентов.

    python -m agents.cost_monitor             # Анализ
    python -m agents.cost_monitor --save      # + отчёт
"""

import json
import re
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from agents.config import (
    REPORTS_DIR, COST_LOG_FILE, COST_ALERT_DAILY, ROOT,
)

REVIEWS_DIR = ROOT / "reviews"


def parse_review_costs():
    """Парсит стоимость из review отчётов."""
    if not REVIEWS_DIR.exists():
        return []
    costs = []
    for f in sorted(REVIEWS_DIR.glob("*.md")):
        content = f.read_text(encoding="utf-8", errors="ignore")
        for m in re.finditer(r"\*\*Стоимость\*\*:\s*\$([0-9.]+)", content):
            cost = float(m.group(1))
            # Extract date from filename: 2026-05-17_150441_review_...
            date_match = re.match(r"(\d{4}-\d{2}-\d{2})", f.stem)
            date = date_match.group(1) if date_match else "unknown"
            costs.append({"date": date, "cost": cost, "file": f.name})
    return costs


def load_cost_log():
    if COST_LOG_FILE.exists():
        try:
            return json.loads(COST_LOG_FILE.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return {}
    return {}


def save_cost_log(log):
    COST_LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    COST_LOG_FILE.write_text(
        json.dumps(log, indent=2, ensure_ascii=False), encoding="utf-8"
    )


def aggregate_by_date(costs):
    daily = {}
    for c in costs:
        d = c["date"]
        daily[d] = daily.get(d, 0) + c["cost"]
    return daily


def main():
    args = sys.argv[1:]
    save_md = "--save" in args or "--md" in args

    costs = parse_review_costs()
    daily = aggregate_by_date(costs)

    # Update cost log
    log = load_cost_log()
    log.update({d: round(v, 4) for d, v in daily.items()})
    save_cost_log(log)

    total = sum(daily.values())
    today = datetime.now().strftime("%Y-%m-%d")
    today_cost = daily.get(today, 0)

    print("\n" + "=" * 60)
    print("  💲 COST MONITOR — Phase 6 Agent #20")
    print("=" * 60)

    print(f"  📊 Всего review-файлов: {len(costs)}")
    print(f"  💰 Общие расходы: ${total:.4f}")
    print(f"  📅 Сегодня: ${today_cost:.4f}")

    if today_cost > COST_ALERT_DAILY:
        print(f"  🔴 ALERT: превышен лимит ${COST_ALERT_DAILY}/день!")
    elif today_cost > COST_ALERT_DAILY * 0.8:
        print(f"  🟡 WARNING: {today_cost/COST_ALERT_DAILY*100:.0f}% от лимита")
    else:
        print(f"  🟢 В пределах нормы ({today_cost/COST_ALERT_DAILY*100:.0f}% лимита)")

    # Daily breakdown
    print("\n  📋 По дням:")
    for d in sorted(daily.keys(), reverse=True)[:7]:
        bar = "█" * int(daily[d] / max(daily.values()) * 20) if daily.values() else ""
        print(f"    {d}: ${daily[d]:.4f} {bar}")

    print("=" * 60 + "\n")

    if save_md:
        lines = [
            f"# 💲 Cost Monitor — {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            "",
            f"Total: ${total:.4f} | Today: ${today_cost:.4f}",
            "",
            "| Дата | Расход | % лимита |",
            "|------|:------:|:--------:|",
        ]
        for d in sorted(daily.keys(), reverse=True):
            pct = daily[d] / COST_ALERT_DAILY * 100
            lines.append(f"| {d} | ${daily[d]:.4f} | {pct:.0f}% |")

        REPORTS_DIR.mkdir(parents=True, exist_ok=True)
        path = REPORTS_DIR / f"costs_{datetime.now().strftime('%Y%m%d')}.md"
        path.write_text("\n".join(lines), encoding="utf-8")
        print(f"📄 Сохранено: {path}")


if __name__ == "__main__":
    main()
