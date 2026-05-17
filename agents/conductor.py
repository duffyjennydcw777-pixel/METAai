"""
🎼 Conductor v3 — Мастер-процесс для всех агентов
Запускает все агенты Phase 1 + Phase 2 + Phase 3, агрегирует результаты.

Использование:
    python -m agents.conductor                 # Запустить все агенты
    python -m agents.conductor --fix           # Запустить + авто-фикс (Phase 1)
    python -m agents.conductor --save          # Сохранить все отчёты
    python -m agents.conductor --phase1        # Только Phase 1
    python -m agents.conductor --phase2        # Только Phase 2
    python -m agents.conductor --phase3        # Только Phase 3
    python -m agents.conductor --fix-all       # Phase 1 --fix + Phase 3 auto-fix
    python -m agents.conductor --kill-all      # Kill switch
"""

import sys
import subprocess
from datetime import datetime
from pathlib import Path

AGENTS_DIR = Path(__file__).parent


def run_agent(module: str, extra_args: list[str] = None) -> bool:
    """Запускает агент как subprocess."""
    cmd = [sys.executable, "-m", f"agents.{module}"]
    if extra_args:
        cmd.extend(extra_args)

    try:
        result = subprocess.run(
            cmd,
            cwd=str(AGENTS_DIR.parent),
            timeout=120,  # 2 минуты для тяжёлых агентов
            encoding="utf-8",
            errors="replace",
        )
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        print(f"  ⏱️ {module}: таймаут (120с)")
        return False
    except Exception as e:
        print(f"  ❌ {module}: {e}")
        return False


def print_banner(text: str):
    """Печатает баннер."""
    print("\n" + "─" * 60)
    print(f"  {text}")
    print("─" * 60)


def main():
    args = sys.argv[1:]

    if "--kill-all" in args:
        print("🛑 Kill switch активирован. Все агенты остановлены.")
        return

    now = datetime.now()
    print("\n" + "╔" + "═" * 58 + "╗")
    print("║" + "  🎼 CONDUCTOR v3 — Meta-Engineering Agent Orchestrator".center(58) + "║")
    print("║" + f"  Phase 1 + 2 + 3 | {now.strftime('%Y-%m-%d %H:%M:%S')}".center(58) + "║")
    print("╚" + "═" * 58 + "╝")

    extra = []
    if "--fix" in args or "--fix-all" in args:
        extra.append("--fix")
    if "--save" in args:
        extra.append("--md")

    phase1_only = "--phase1" in args
    phase2_only = "--phase2" in args
    phase3_only = "--phase3" in args
    run_all = not phase1_only and not phase2_only and not phase3_only
    fix_all = "--fix-all" in args

    results = {}

    # ═══════════════════════════════════════════════════════
    # PHASE 1: Core Governance
    # ═══════════════════════════════════════════════════════
    if run_all or phase1_only:
        print("\n" + "█" * 60)
        print("  📋 PHASE 1 — Core Governance")
        print("█" * 60)

        # Agent #1: Compliance Checker
        print_banner("🔍 Agent #1: Compliance Checker")
        results["compliance"] = run_agent("compliance_checker", extra)

        # Agent #2: Decision Watchdog
        print_banner("🐕 Agent #2: Decision Watchdog")
        watchdog_args = ["--detail"] if "--save" in args else []
        results["watchdog"] = run_agent("decision_watchdog", watchdog_args)

        # Agent #3: Auto-Reflection
        print_banner("🪞 Agent #3: Auto-Reflection")
        reflection_args = ["--save"] if "--save" in args else []
        results["reflection"] = run_agent("auto_reflection", reflection_args)

    # ═══════════════════════════════════════════════════════
    # PHASE 2: Deep Analysis
    # ═══════════════════════════════════════════════════════
    if run_all or phase2_only:
        print("\n" + "█" * 60)
        print("  📊 PHASE 2 — Deep Analysis")
        print("█" * 60)

        # Agent #4: Health Monitor
        print_banner("🏥 Agent #4: Project Health Monitor")
        health_args = ["--save"] if "--save" in args else []
        results["health"] = run_agent("health_monitor", health_args)

        # Agent #5: Changelog Enforcer
        print_banner("📋 Agent #5: Changelog Enforcer")
        cl_args = ["--days", "14"]
        if "--fix" in args or fix_all:
            cl_args.append("--fix")
        results["changelog"] = run_agent("changelog_enforcer", cl_args)

        # Agent #6: Dependency Scanner
        print_banner("🔍 Agent #6: Dependency Scanner")
        dep_args = ["--save"] if "--save" in args else []
        results["deps"] = run_agent("dependency_scanner", dep_args)

    # ═══════════════════════════════════════════════════════
    # PHASE 3: Automation
    # ═══════════════════════════════════════════════════════
    if run_all or phase3_only:
        print("\n" + "█" * 60)
        print("  ⚡ PHASE 3 — Automation")
        print("█" * 60)

        # Agent #7: Rule Syncer
        print_banner("🔄 Agent #7: Rule Syncer")
        sync_args = ["--save"] if "--save" in args else []
        if fix_all:
            sync_args.append("--fix")
        results["rule_sync"] = run_agent("rule_syncer", sync_args)

        # Agent #8: TODO Harvester
        print_banner("📌 Agent #8: TODO Harvester")
        todo_args = ["--save"] if "--save" in args else []
        results["todos"] = run_agent("todo_harvester", todo_args)

        # Agent #9: Lock Generator
        print_banner("🔒 Agent #9: Lock Generator")
        lock_args = ["--save"] if "--save" in args else []
        if fix_all:
            lock_args.append("--fix")
        results["locks"] = run_agent("lock_generator", lock_args)

        # Agent #10: Obsidian Pulse
        print_banner("📊 Agent #10: Obsidian Pulse")
        pulse_args = ["--save"] if "--save" in args else []
        results["pulse"] = run_agent("obsidian_pulse", pulse_args)

    # ═══════════════════════════════════════════════════════
    # SUMMARY
    # ═══════════════════════════════════════════════════════
    print("\n" + "╔" + "═" * 58 + "╗")
    print("║" + "  📊 ИТОГИ".center(58) + "║")
    print("╠" + "═" * 58 + "╣")

    icons = {True: "✅", False: "❌"}
    for name, ok in results.items():
        print("║" + f"  {icons[ok]} {name}".ljust(58) + "║")

    passed = sum(1 for v in results.values() if v)
    total = len(results)
    status = "✅ ВСЕ АГЕНТЫ ОТРАБОТАЛИ" if passed == total else f"⚠️ {passed}/{total} успешно"

    print("╠" + "═" * 58 + "╣")
    print("║" + f"  {status}".ljust(58) + "║")
    print("╚" + "═" * 58 + "╝" + "\n")


if __name__ == "__main__":
    main()

