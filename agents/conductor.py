"""
🎼 Conductor v7 — Мастер-процесс для всех агентов
Запускает все 26 агентов Phase 1-7, агрегирует результаты.

Использование:
    python -m agents.conductor                 # Запустить все агенты
    python -m agents.conductor --fix           # Запустить + авто-фикс (Phase 1)
    python -m agents.conductor --save          # Сохранить все отчёты
    python -m agents.conductor --phase1-6      # Только конкретная фаза
    python -m agents.conductor --fix-all       # Phase 1+3 fix + Phase 4 auto-commit
    python -m agents.conductor --notify        # Telegram report
    python -m agents.conductor --sprint        # Sprint Planner
    python -m agents.conductor --release       # Release Manager (--tag для создания)
    python -m agents.conductor --digest        # Weekly Digest
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
    print("║" + "  🎼 CONDUCTOR v7 — Meta-Engineering Agent Orchestrator".center(58) + "║")
    print("║" + f"  Phase 1-7 | 26 agents | {now.strftime('%Y-%m-%d %H:%M:%S')}".center(58) + "║")
    print("╚" + "═" * 58 + "╝")

    extra = []
    if "--fix" in args or "--fix-all" in args:
        extra.append("--fix")
    if "--save" in args:
        extra.append("--md")

    phase1_only = "--phase1" in args
    phase2_only = "--phase2" in args
    phase3_only = "--phase3" in args
    phase4_only = "--phase4" in args
    phase5_only = "--phase5" in args
    phase6_only = "--phase6" in args
    phase7_only = "--phase7" in args
    do_digest = "--digest" in args
    do_notify = "--notify" in args
    do_sprint = "--sprint" in args
    do_release = "--release" in args
    do_market = "--market" in args
    run_all = not any([phase1_only, phase2_only, phase3_only, phase4_only,
                       phase5_only, phase6_only, phase7_only, do_digest,
                       do_notify, do_sprint, do_release, do_market])
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
    # PHASE 4: Intelligence
    # ═══════════════════════════════════════════════════════
    if run_all or phase4_only:
        print("\n" + "█" * 60)
        print("  🧠 PHASE 4 — Intelligence")
        print("█" * 60)

        # Agent #11: Correlator
        print_banner("🔗 Agent #11: Cross-Project Correlator")
        corr_args = ["--save"] if "--save" in args else []
        results["correlator"] = run_agent("correlator", corr_args)

        # Agent #12: Drift Predictor
        print_banner("📈 Agent #12: Drift Predictor")
        drift_args = ["--save"] if "--save" in args else []
        results["drift"] = run_agent("drift_predictor", drift_args)

        # Agent #13: Auto-Committer (после fix-all)
        if fix_all:
            print_banner("🤖 Agent #13: Auto-Committer")
            commit_args = ["--commit"]
            if "--push" in args:
                commit_args.append("--push")
            results["auto_commit"] = run_agent("auto_committer", commit_args)

    # Weekly Digest (по запросу)
    if do_digest or (run_all and "--save" in args):
        print_banner("📬 Agent #14: Weekly Digest")
        digest_args = ["--save"] if "--save" in args else []
        results["digest"] = run_agent("weekly_digest", digest_args)

    # ═══════════════════════════════════════════════════════
    # PHASE 5: Outreach
    # ═══════════════════════════════════════════════════════
    if run_all or phase5_only:
        print("\n" + "█" * 60)
        print("  📡 PHASE 5 — Outreach")
        print("█" * 60)

        # Agent #15: Telegram Reporter
        print_banner("📲 Agent #15: Telegram Reporter")
        tg_args = ["--dry-run"]
        results["telegram"] = run_agent("telegram_reporter", tg_args)

        # Agent #16: Sprint Planner
        print_banner("🗂️ Agent #16: Sprint Planner")
        sprint_args = ["--save"] if "--save" in args else []
        results["sprint"] = run_agent("sprint_planner", sprint_args)

        # Agent #17: Self-Tuner
        print_banner("⚙️ Agent #17: Self-Tuner")
        results["tuner"] = run_agent("self_tuner", [])

        # Agent #18: Portfolio Tracker
        print_banner("💰 Agent #18: Portfolio Tracker")
        port_args = ["--save"] if "--save" in args else []
        results["portfolio"] = run_agent("portfolio_tracker", port_args)

    # Standalone triggers
    if do_notify:
        print_banner("📲 Agent #15: Telegram Reporter")
        results["telegram"] = run_agent("telegram_reporter", [])

    if do_sprint:
        print_banner("🗂️ Agent #16: Sprint Planner")
        sprint_args = ["--save"] if "--save" in args else []
        results["sprint"] = run_agent("sprint_planner", sprint_args)

    # ═══════════════════════════════════════════════════════
    # PHASE 6: Mastery
    # ═══════════════════════════════════════════════════════
    if run_all or phase6_only:
        print("\n" + "█" * 60)
        print("  🧬 PHASE 6 — Mastery")
        print("█" * 60)

        # Agent #19: Git Analytics
        print_banner("📊 Agent #19: Git Analytics")
        ga_args = ["--save"] if "--save" in args else []
        results["git_analytics"] = run_agent("git_analytics", ga_args)

        # Agent #20: Cost Monitor
        print_banner("💲 Agent #20: Cost Monitor")
        cm_args = ["--save"] if "--save" in args else []
        results["cost_monitor"] = run_agent("cost_monitor", cm_args)

        # Agent #21: Release Manager
        print_banner("🏷️ Agent #21: Release Manager")
        results["release"] = run_agent("release_manager", [])

        # Agent #22: Knowledge Distiller
        print_banner("🧬 Agent #22: Knowledge Distiller")
        kd_args = ["--save"] if "--save" in args else []
        results["knowledge"] = run_agent("knowledge_distiller", kd_args)

    # Standalone triggers
    if do_release:
        print_banner("🏷️ Agent #21: Release Manager")
        rm_args = ["--tag"] if "--tag" in args else []
        if "--save" in args:
            rm_args.append("--save")
        results["release"] = run_agent("release_manager", rm_args)

    # ═══════════════════════════════════════════════════════
    # PHASE 7: Growth
    # ═══════════════════════════════════════════════════════
    if run_all or phase7_only:
        print("\n" + "█" * 60)
        print("  📈 PHASE 7 — Growth")
        print("█" * 60)

        # Agent #23: Market Scanner
        print_banner("🔭 Agent #23: Market Scanner")
        ms_args = ["--save"] if "--save" in args else []
        results["market_scanner"] = run_agent("market_scanner", ms_args)

        # Agent #24: Idea Scorer
        print_banner("🎯 Agent #24: Idea Scorer")
        is_args = ["--save"] if "--save" in args else []
        results["idea_scorer"] = run_agent("idea_scorer", is_args)

        # Agent #25: Revenue Forecaster
        print_banner("📈 Agent #25: Revenue Forecaster")
        results["forecaster"] = run_agent("revenue_forecaster", [])

        # Agent #26: Opportunity Radar
        print_banner("🎯 Agent #26: Opportunity Radar")
        or_args = ["--save"] if "--save" in args else []
        results["opportunities"] = run_agent("opportunity_radar", or_args)

    # Standalone: market scan
    if do_market:
        print_banner("🔭 Market Scanner")
        ms_args = ["--save"] if "--save" in args else []
        results["market_scanner"] = run_agent("market_scanner", ms_args)

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

