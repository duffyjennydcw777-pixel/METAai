"""
🎼 Conductor — Мастер-процесс для всех агентов
Запускает все агенты Фазы 1, агрегирует результаты.

Использование:
    python -m agents.conductor                 # Запустить все агенты
    python -m agents.conductor --fix           # Запустить + авто-фикс
    python -m agents.conductor --save          # Сохранить все отчёты
    python -m agents.conductor --kill-all      # Ничего не делать (заглушка для будущих фоновых агентов)
"""

import sys
import subprocess
from datetime import datetime
from pathlib import Path

AGENTS_DIR = Path(__file__).parent


def run_agent(module: str, extra_args: list[str] = None):
    """Запускает агент как subprocess."""
    cmd = [sys.executable, "-m", f"agents.{module}"]
    if extra_args:
        cmd.extend(extra_args)

    try:
        result = subprocess.run(
            cmd,
            cwd=str(AGENTS_DIR.parent),
            timeout=60,
            encoding="utf-8",
            errors="replace",
        )
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        print(f"  ⏱️ {module}: таймаут (60с)")
        return False
    except Exception as e:
        print(f"  ❌ {module}: {e}")
        return False


def main():
    args = sys.argv[1:]

    if "--kill-all" in args:
        print("🛑 Kill switch активирован. Все агенты остановлены.")
        return

    print("\n" + "╔" + "═" * 58 + "╗")
    print("║" + "  🎼 CONDUCTOR — Meta-Engineering Agent Orchestrator".center(58) + "║")
    print("║" + f"  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}".center(58) + "║")
    print("╚" + "═" * 58 + "╝")

    extra = []
    if "--fix" in args:
        extra.append("--fix")
    if "--save" in args:
        extra.append("--md")

    # Agent #1: Compliance Checker
    print("\n" + "─" * 60)
    print("  🔍 Запуск Agent #1: Compliance Checker...")
    print("─" * 60)
    run_agent("compliance_checker", extra)

    # Agent #2: Decision Watchdog
    print("\n" + "─" * 60)
    print("  🐕 Запуск Agent #2: Decision Watchdog...")
    print("─" * 60)
    watchdog_args = ["--detail"] if "--save" in args else []
    run_agent("decision_watchdog", watchdog_args)

    # Agent #3: Auto-Reflection
    print("\n" + "─" * 60)
    print("  🪞 Запуск Agent #3: Auto-Reflection...")
    print("─" * 60)
    reflection_args = []
    if "--save" in args:
        reflection_args.extend(["--save"])
    run_agent("auto_reflection", reflection_args)

    # Финал
    print("\n" + "╔" + "═" * 58 + "╗")
    print("║" + "  ✅ Все агенты завершили работу".center(58) + "║")
    print("╚" + "═" * 58 + "╝" + "\n")


if __name__ == "__main__":
    main()
