#!/usr/bin/env python3
"""
💰 METAai Cost Tracker
Считает затраты на AI review по логам из reviews/
"""
import re
from pathlib import Path


def parse_reviews(reviews_dir: Path) -> list[dict]:
    """Parse all review reports and extract cost data."""
    entries = []
    for f in sorted(reviews_dir.glob("*.md")):
        content = f.read_text(encoding="utf-8", errors="ignore")

        # Extract cost
        cost_match = re.search(r"\*\*Стоимость\*\*:\s*\$([0-9.]+)", content)
        # Extract tokens
        tokens_match = re.search(r"\*\*Токены\*\*:\s*(\d+)→(\d+)", content)
        # Extract time
        time_match = re.search(r"\*\*Время\*\*:\s*(\d+)ms", content)
        # Extract model
        model_match = re.search(r"\*\*Модель\*\*:\s*(.+)", content)
        # Extract date from filename (2026-04-28_033209_review_METAai.md)
        date_match = re.match(r"(\d{4}-\d{2}-\d{2})_(\d{6})_(\w+)_(.+)\.md", f.name)

        if cost_match:
            entry = {
                "file": f.name,
                "cost": float(cost_match.group(1)),
                "input_tokens": int(tokens_match.group(1)) if tokens_match else 0,
                "output_tokens": int(tokens_match.group(2)) if tokens_match else 0,
                "time_ms": int(time_match.group(1)) if time_match else 0,
                "model": model_match.group(1).strip() if model_match else "unknown",
                "date": date_match.group(1) if date_match else "unknown",
                "type": date_match.group(3) if date_match else "unknown",
                "project": date_match.group(4) if date_match else "unknown",
            }
            entries.append(entry)

    return entries


def print_report(entries: list[dict]):
    """Print cost summary."""
    if not entries:
        print("📊 Нет review-отчётов в reviews/")
        return

    total_cost = sum(e["cost"] for e in entries)
    total_input = sum(e["input_tokens"] for e in entries)
    total_output = sum(e["output_tokens"] for e in entries)
    total_time = sum(e["time_ms"] for e in entries)

    print("\n" + "=" * 60)
    print("💰 METAai Cost Report")
    print("=" * 60)

    # Per-day breakdown
    days: dict[str, list] = {}
    for e in entries:
        days.setdefault(e["date"], []).append(e)

    for day, day_entries in sorted(days.items()):
        day_cost = sum(e["cost"] for e in day_entries)
        print(f"\n📅 {day} — {len(day_entries)} reviews, ${day_cost:.4f}")
        for e in day_entries:
            print(f"   {e['type']:10} {e['project']:15} ${e['cost']:.4f}  {e['model']}")

    # Totals
    print("\n" + "-" * 60)
    print(f"📊 Всего reviews:      {len(entries)}")
    print(f"💰 Потрачено:          ${total_cost:.4f}")
    print(f"🔤 Токены:             {total_input:,}→{total_output:,}")
    print(f"⏱️  Время:              {total_time/1000:.1f}с")
    print(f"📈 Средняя стоимость:  ${total_cost/len(entries):.4f}/review")

    # Projection
    monthly = total_cost / max(len(days), 1) * 30
    print(f"\n🔮 Прогноз на месяц:   ${monthly:.2f}")
    print(f"   (при текущем темпе: {len(entries)/max(len(days),1):.0f} reviews/день)")
    print("=" * 60)


def main():
    reviews_dir = Path(__file__).parent / "reviews"
    if not reviews_dir.exists():
        print("📁 Папка reviews/ не найдена")
        return

    entries = parse_reviews(reviews_dir)
    print_report(entries)


if __name__ == "__main__":
    main()
