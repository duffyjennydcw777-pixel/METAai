"""
📲 Agent #15: Telegram Reporter
Отправляет daily summary и critical alerts в Telegram.

    python -m agents.telegram_reporter              # Отправить daily
    python -m agents.telegram_reporter --dry-run    # Только показать
    python -m agents.telegram_reporter --critical   # Только критические
"""

import json
import os
import re
import sys
import urllib.request
import urllib.parse
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from agents.config import (
    REPORTS_DIR, HISTORY_FILE,
    TELEGRAM_BOT_TOKEN_ENV, TELEGRAM_CHAT_ID_ENV,
    HEALTH_CRITICAL_THRESHOLD, HEALTH_WARNING_THRESHOLD,
)


def get_telegram_creds():
    token = os.environ.get(TELEGRAM_BOT_TOKEN_ENV, "")
    chat_id = os.environ.get(TELEGRAM_CHAT_ID_ENV, "")
    return token, chat_id


def send_telegram(token, chat_id, text):
    """Отправляет сообщение через Telegram Bot API."""
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    data = urllib.parse.urlencode({
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML",
    }).encode("utf-8")
    try:
        req = urllib.request.Request(url, data=data)
        with urllib.request.urlopen(req, timeout=10) as resp:
            return resp.status == 200
    except Exception as e:
        print(f"  ❌ Telegram error: {e}")
        return False


def parse_health():
    reports = sorted(REPORTS_DIR.glob("health_*.md"), reverse=True)
    if not reports:
        return {}
    content = reports[0].read_text(encoding="utf-8", errors="ignore")
    scores = {}
    for m in re.finditer(r"## [🟢🟡🔴]\s+(\w+)\s+—\s+(\d+)%", content):
        scores[m.group(1)] = int(m.group(2))
    return scores


def parse_todos():
    reports = sorted(REPORTS_DIR.glob("todos_*.md"), reverse=True)
    if not reports:
        return 0, {}
    content = reports[0].read_text(encoding="utf-8", errors="ignore")
    total_match = re.search(r"Всего маркеров:\s*\*\*(\d+)\*\*", content)
    total = int(total_match.group(1)) if total_match else 0
    per_project = {}
    for m in re.finditer(r"\|\s+(\w+)\s+\|.*\|\s+(\d+)\s+\|$", content, re.MULTILINE):
        per_project[m.group(1)] = int(m.group(2))
    return total, per_project


def get_velocity():
    if not HISTORY_FILE.exists():
        return {}
    try:
        history = json.loads(HISTORY_FILE.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}
    dates = sorted(history.keys(), reverse=True)
    if len(dates) < 2:
        return {}
    latest = history[dates[0]]
    prev = history[dates[1]]
    return {p: latest.get(p, 0) - prev.get(p, 0) for p in latest}


def build_daily_message(health, todo_total, todo_per, velocity):
    now = datetime.now().strftime("%Y-%m-%d")
    avg = round(sum(health.values()) / len(health)) if health else 0

    lines = [f"🎼 <b>METAai Daily Report</b> — {now}", ""]

    # Health
    lines.append(f"📊 <b>Health: {avg}% avg</b>")
    for name, score in sorted(health.items(), key=lambda x: -x[1]):
        if score >= 90:
            icon = "🟢"
        elif score >= HEALTH_WARNING_THRESHOLD:
            icon = "🟡"
        else:
            icon = "🔴"
        vel = velocity.get(name)
        vel_str = f" {'↗️' if vel and vel > 0 else '↘️' if vel and vel < 0 else ''}" if vel else ""
        lines.append(f"  {icon} {name} {score}%{vel_str}")

    # TODOs
    if todo_total:
        lines.append(f"\n📌 <b>TODOs: {todo_total}</b>")
        top = sorted(todo_per.items(), key=lambda x: -x[1])[:3]
        for name, count in top:
            if count > 0:
                lines.append(f"  {name}: {count}")

    # Alerts
    critical = [p for p, s in health.items() if s < HEALTH_CRITICAL_THRESHOLD]
    if critical:
        lines.append(f"\n⚠️ <b>CRITICAL</b>: {', '.join(critical)} < {HEALTH_CRITICAL_THRESHOLD}%")

    return "\n".join(lines)


def build_critical_message(health):
    critical = {p: s for p, s in health.items() if s < HEALTH_CRITICAL_THRESHOLD}
    if not critical:
        return None
    lines = ["🚨 <b>METAai CRITICAL ALERT</b>", ""]
    for name, score in critical.items():
        lines.append(f"🔴 {name}: health {score}% (порог: {HEALTH_CRITICAL_THRESHOLD}%)")
    return "\n".join(lines)


def main():
    args = sys.argv[1:]
    dry_run = "--dry-run" in args
    critical_only = "--critical" in args

    health = parse_health()
    if not health:
        print("⚠️ Нет health данных")
        return

    todo_total, todo_per = parse_todos()
    velocity = get_velocity()

    if critical_only:
        message = build_critical_message(health)
        if not message:
            print("  ✅ Нет критических алертов")
            return
    else:
        message = build_daily_message(health, todo_total, todo_per, velocity)

    print("\n" + "=" * 60)
    print("  📲 TELEGRAM REPORTER — Phase 5 Agent #15")
    print("=" * 60)

    if dry_run:
        print("\n  [DRY-RUN] Сообщение:\n")
        # Strip HTML for console
        clean = message.replace("<b>", "").replace("</b>", "")
        for line in clean.split("\n"):
            print(f"  {line}")
        print("\n" + "=" * 60)
        return

    token, chat_id = get_telegram_creds()
    if not token or not chat_id:
        print("  ⚠️ Нет Telegram credentials")
        print(f"  Установи {TELEGRAM_BOT_TOKEN_ENV} и {TELEGRAM_CHAT_ID_ENV} в .env")
        print("\n  [FALLBACK] Сообщение:\n")
        clean = message.replace("<b>", "").replace("</b>", "")
        for line in clean.split("\n"):
            print(f"  {line}")
        print("\n" + "=" * 60)
        return

    if send_telegram(token, chat_id, message):
        print("  ✅ Отправлено в Telegram")
    else:
        print("  ❌ Ошибка отправки")

    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
