"""
👁️ Agent #47: Event Watcher
Отслеживает файловую систему и триггерит агентов при событиях.
Режим: сессия (5мин polling) / фон (1 час через Task Scheduler).

    python -m agents.event_watcher                # Одна проверка
    python -m agents.event_watcher --watch        # Polling loop (5 мин)
    python -m agents.event_watcher --save         # + сохранить
"""

import hashlib
import json
import os
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from agents.config import (
    REPORTS_DIR, EVOLUTION_DIR,
    WATCH_POLL_SESSION,
)

PROJECT_ROOT = str(Path(__file__).resolve().parent.parent)
STATE_FILE = EVOLUTION_DIR / "watcher_state.json"


def load_json(path):
    if Path(path).exists():
        try:
            return json.loads(Path(path).read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            pass
    return {}


def save_json(path, data):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(
        json.dumps(data, indent=2, ensure_ascii=False, default=str),
        encoding="utf-8",
    )


def file_hash(path):
    """MD5 hash файла."""
    try:
        return hashlib.md5(Path(path).read_bytes()).hexdigest()
    except (OSError, PermissionError):
        return ""


def scan_directory(dir_path, patterns=None):
    """Сканирует директорию, возвращает {path: hash}."""
    if patterns is None:
        patterns = ["*.json", "*.md", "*.py"]

    result = {}
    dp = Path(dir_path)
    if not dp.exists():
        return result

    for pattern in patterns:
        for f in dp.rglob(pattern):
            if "__pycache__" in str(f) or ".git" in str(f):
                continue
            result[str(f)] = file_hash(f)

    return result


# ═══════════════════════════════════════════════════════════
# EVENT HANDLERS
# ═══════════════════════════════════════════════════════════

TRIGGER_RULES = [
    {
        "name": "New Feed Data",
        "watch_dir": str(REPORTS_DIR / "feeds"),
        "patterns": ["*.json"],
        "action": "signal_router",
        "args": ["--save"],
    },
    {
        "name": "Config Changed",
        "watch_dir": str(Path(PROJECT_ROOT) / "agents"),
        "patterns": ["config.py"],
        "action": "self_tuner",
        "args": ["--save"],
    },
    {
        "name": "New Review",
        "watch_dir": str(Path(PROJECT_ROOT) / "reviews"),
        "patterns": ["*.md"],
        "action": "notify",
        "args": [],
    },
    {
        "name": "Evolution Data Changed",
        "watch_dir": str(EVOLUTION_DIR),
        "patterns": ["*.json"],
        "action": "perf_benchmarker",
        "args": [],
    },
]


def run_triggered_agent(module, extra_args=None):
    """Запускает агент при событии."""
    cmd = [sys.executable, "-m", f"agents.{module}"]
    if extra_args:
        cmd.extend(extra_args)

    env = dict(os.environ)
    env["PYTHONUTF8"] = "1"
    env["PYTHONIOENCODING"] = "utf-8"

    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=120,
            cwd=PROJECT_ROOT, env=env, encoding="utf-8", errors="replace",
        )
        return result.returncode == 0
    except Exception:
        return False


def notify_telegram(message):
    """Отправить уведомление через Telegram."""
    try:
        from agents.telegram_reporter import get_telegram_creds, send_telegram
        token, chat_id = get_telegram_creds()
        if token and chat_id:
            send_telegram(token, chat_id, message)
    except ImportError:
        pass


def check_for_changes():
    """Проверяет изменения и триггерит агентов."""
    state = load_json(STATE_FILE)
    prev_hashes = state.get("hashes", {})
    events = []

    current_hashes = {}

    for rule in TRIGGER_RULES:
        watch_dir = rule["watch_dir"]
        patterns = rule["patterns"]

        # Scan current state
        dir_hashes = scan_directory(watch_dir, patterns)
        current_hashes.update(dir_hashes)

        # Compare with previous
        for fpath, fhash in dir_hashes.items():
            prev_hash = prev_hashes.get(fpath)

            if prev_hash is None:
                # New file
                events.append({
                    "type": "created",
                    "file": fpath,
                    "rule": rule["name"],
                    "action": rule["action"],
                    "args": rule["args"],
                })
            elif prev_hash != fhash:
                # Modified file
                events.append({
                    "type": "modified",
                    "file": fpath,
                    "rule": rule["name"],
                    "action": rule["action"],
                    "args": rule["args"],
                })

    # Check for deleted files
    for fpath in prev_hashes:
        if fpath not in current_hashes:
            events.append({
                "type": "deleted",
                "file": fpath,
                "rule": "File Deleted",
                "action": None,
                "args": [],
            })

    # Save new state
    state["hashes"] = current_hashes
    state["last_check"] = datetime.now().isoformat()
    state["total_files"] = len(current_hashes)
    save_json(STATE_FILE, state)

    return events


def process_events(events, dry_run=False):
    """Обрабатывает события."""
    triggered = set()

    for event in events:
        etype = event["type"]
        fname = Path(event["file"]).name
        rule = event["rule"]
        action = event["action"]

        icon = "🆕" if etype == "created" else "✏️" if etype == "modified" else "🗑️"
        print(f"    {icon} [{rule}] {fname}")

        if action and action not in triggered and not dry_run:
            if action == "notify":
                notify_telegram(
                    f"👁️ METAai Event: {rule}\n"
                    f"{icon} {fname}"
                )
            else:
                print(f"      → Триггер: {action}")
                ok = run_triggered_agent(action, event.get("args"))
                status = "✅" if ok else "❌"
                print(f"      → {status}")
            triggered.add(action)

    return triggered


def main():
    args = sys.argv[1:]
    watch = "--watch" in args
    save_md = "--save" in args
    dry_run = "--dry-run" in args

    print("\n" + "=" * 60)
    print("  👁️ EVENT WATCHER — Phase 13 Agent #47")
    print("=" * 60)

    if watch:
        print(f"\n  🔄 Polling mode (каждые {WATCH_POLL_SESSION}s)")
        print("  Ctrl+C для остановки\n")

        iteration = 0
        while True:
            try:
                iteration += 1
                now = datetime.now().strftime("%H:%M:%S")
                print(f"  [{now}] Проверка #{iteration}...")

                events = check_for_changes()
                if events:
                    print(f"  📢 {len(events)} событий:")
                    triggered = process_events(events, dry_run)
                    print(f"  ⚡ Триггеров: {len(triggered)}")
                else:
                    print("  ✅ Без изменений")

                time.sleep(WATCH_POLL_SESSION)

            except KeyboardInterrupt:
                print("\n  ⏹ Остановлен")
                break
    else:
        # Single check
        print("\n  🔍 Однократная проверка...")

        events = check_for_changes()

        if events:
            print(f"\n  📢 {len(events)} событий:")
            triggered = process_events(events, dry_run)
            print(f"\n  ⚡ Триггеров: {len(triggered)}")
        else:
            print("\n  ✅ Без изменений с последней проверки")

        state = load_json(STATE_FILE)
        print(f"\n  📊 Tracked files: {state.get('total_files', 0)}")
        print(f"  🕐 Last check: {state.get('last_check', 'never')}")

    if save_md:
        state = load_json(STATE_FILE)
        state["events_log"] = state.get("events_log", [])
        if events:
            state["events_log"].extend([
                {
                    "timestamp": datetime.now().isoformat(),
                    "type": e["type"],
                    "file": Path(e["file"]).name,
                    "rule": e["rule"],
                }
                for e in events
            ])
            state["events_log"] = state["events_log"][-100:]
        save_json(STATE_FILE, state)
        print(f"\n  💾 Сохранено: {STATE_FILE}")

    print("\n" + "=" * 60 + "\n")


if __name__ == "__main__":
    main()
