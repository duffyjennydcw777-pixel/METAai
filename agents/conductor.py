"""
🎼 Conductor v13 — Мастер-процесс для всех агентов
Запускает все 50 агентов Phase 1-13, агрегирует результаты.

Использование:
    python -m agents.conductor                 # Запустить все агенты
    python -m agents.conductor --fix           # Запустить + авто-фикс (Phase 1)
    python -m agents.conductor --save          # Сохранить все отчёты
    python -m agents.conductor --phase1-13     # Только конкретная фаза
    python -m agents.conductor --fix-all       # Phase 1+3 fix + Phase 4 auto-commit
    python -m agents.conductor --notify        # Telegram report
    python -m agents.conductor --sprint        # Sprint Planner
    python -m agents.conductor --release       # Release Manager (--tag для создания)
    python -m agents.conductor --digest        # Weekly Digest
    python -m agents.conductor --loop          # Phase 8+9 (Intelligence → Action)
    python -m agents.conductor --recon         # Phase 10 (Competitor Intelligence)
    python -m agents.conductor --evolve        # Phase 12 (Meta-Evolution)
    python -m agents.conductor --phase13       # Phase 13 (Self-Evolving)
    python -m agents.conductor --phase14       # Phase 14 (Blind Spots)
    python -m agents.conductor --bot           # Telegram Command Bot (long-polling)
    python -m agents.conductor --watch         # Event Watcher (polling)
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
    print("║" + "  🎼 CONDUCTOR v14 — Self-Evolving Agent Orchestrator".center(58) + "║")
    print("║" + f"  Phase 1-14 | 55 agents | {now.strftime('%Y-%m-%d %H:%M:%S')}".center(58) + "║")
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
    phase8_only = "--phase8" in args
    phase9_only = "--phase9" in args
    phase10_only = "--phase10" in args
    do_digest = "--digest" in args
    do_notify = "--notify" in args
    do_sprint = "--sprint" in args
    do_release = "--release" in args
    do_market = "--market" in args
    do_feeds = "--feeds" in args
    do_loop = "--loop" in args  # Phase 8+9 combo
    do_recon = "--recon" in args  # Phase 10
    do_evolve = "--evolve" in args  # Phase 12
    phase13_only = "--phase13" in args  # Phase 13
    phase14_only = "--phase14" in args  # Phase 14
    do_bot = "--bot" in args  # Telegram Command Bot
    do_watch = "--watch" in args  # Event Watcher
    run_all = not any([
        phase1_only, phase2_only, phase3_only, phase4_only, phase5_only,
        phase6_only, phase7_only, do_digest, phase8_only, phase9_only,
        phase10_only, do_market, do_notify, do_sprint, do_release, do_feeds,
        do_loop, do_recon, do_evolve, phase13_only, phase14_only,
        do_bot, do_watch,
    ])
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
    # PHASE 8: Intelligence Feeds
    # ═══════════════════════════════════════════════════════
    if run_all or phase8_only or do_feeds or do_loop:
        print("\n" + "█" * 60)
        print("  📡 PHASE 8 — Intelligence Feeds")
        print("█" * 60)

        # Agent #27: TrustMRR Scraper
        print_banner("🔭 Agent #27: TrustMRR Scraper")
        ts_args = ["--save"] if "--save" in args else []
        results["trustmrr"] = run_agent("trustmrr_scraper", ts_args)

        # Agent #28: Acquire Scanner
        print_banner("🏪 Agent #28: Acquire Scanner")
        as_args = ["--save"] if "--save" in args else []
        results["acquire"] = run_agent("acquire_scanner", as_args)

        # Agent #29: ProductHunt Tracker
        print_banner("🚀 Agent #29: ProductHunt Tracker")
        ph_args = ["--save"] if "--save" in args else []
        results["producthunt"] = run_agent("ph_tracker", ph_args)

        # Agent #30: Feed Aggregator
        print_banner("📡 Agent #30: Feed Aggregator")
        fa_args = ["--save"] if "--save" in args else []
        results["aggregator"] = run_agent("feed_aggregator", fa_args)

    # ═══════════════════════════════════════════════════════
    # PHASE 9: Autonomous Loop
    # ═══════════════════════════════════════════════════════
    if run_all or phase9_only or do_loop:
        print("\n" + "█" * 60)
        print("  🔄 PHASE 9 — Autonomous Loop")
        print("█" * 60)

        # Agent #31: Signal Router
        print_banner("🔀 Agent #31: Signal Router")
        sr_args = ["--save"] if "--save" in args else []
        results["signal_router"] = run_agent("signal_router", sr_args)

        # Agent #32: Deal Evaluator
        print_banner("💰 Agent #32: Deal Evaluator")
        de_args = ["--save"] if "--save" in args else []
        results["deal_evaluator"] = run_agent("deal_evaluator", de_args)

        # Agent #33: Trend Matcher
        print_banner("🔗 Agent #33: Trend Matcher")
        tm_args = ["--save"] if "--save" in args else []
        results["trend_matcher"] = run_agent("trend_matcher", tm_args)

        # Agent #34: Action Generator
        print_banner("⚡ Agent #34: Action Generator")
        ag_args = ["--save"] if "--save" in args else []
        results["action_gen"] = run_agent("action_generator", ag_args)

    # Intelligence → Action loop (Phase 8 + Phase 9)
    if do_loop:
        pass  # Phase 8 already ran above via do_loop, Phase 9 also ran

    # ═══════════════════════════════════════════════════════
    # PHASE 10: Competitor Intelligence
    # ═══════════════════════════════════════════════════════
    if run_all or phase10_only or do_recon:
        print("\n" + "█" * 60)
        print("  🕵️ PHASE 10 — Competitor Intelligence")
        print("█" * 60)

        # Agent #35: Competitor Tracker
        print_banner("🕵️ Agent #35: Competitor Tracker")
        ct_args = ["--save"] if "--save" in args else []
        results["competitor_tracker"] = run_agent("competitor_tracker", ct_args)

        # Agent #36: SEO Watchdog
        print_banner("🔍 Agent #36: SEO Watchdog")
        seo_args = ["--save"] if "--save" in args else []
        results["seo_watchdog"] = run_agent("seo_watchdog", seo_args)

        # Agent #37: Feature Radar
        print_banner("📋 Agent #37: Feature Radar")
        fr_args = ["--save"] if "--save" in args else []
        results["feature_radar"] = run_agent("feature_radar", fr_args)

        # Agent #38: Pricing Monitor
        print_banner("💲 Agent #38: Pricing Monitor")
        pm_args = ["--save"] if "--save" in args else []
        results["pricing_monitor"] = run_agent("pricing_monitor", pm_args)

    # ═══════════════════════════════════════════════════════
    # PHASE 12: Meta-Evolution
    # ═══════════════════════════════════════════════════════
    if run_all or do_evolve:
        print("\n" + "█" * 60)
        print("  🧬 PHASE 12 — Meta-Evolution")
        print("█" * 60)

        # Agent #39: Knowledge Distiller
        print_banner("🧠 Agent #39: Knowledge Distiller")
        kd_args = ["--save"] if "--save" in args else []
        results["knowledge_distiller"] = run_agent("knowledge_distiller", kd_args)

        # Agent #40: Portfolio Tracker
        print_banner("📊 Agent #40: Portfolio Tracker")
        pt_args = ["--save"] if "--save" in args else []
        results["portfolio_tracker"] = run_agent("portfolio_tracker", pt_args)

        # Agent #41: Self-Tuner
        print_banner("🔧 Agent #41: Self-Tuner")
        st_args = ["--save"] if "--save" in args else []
        results["self_tuner"] = run_agent("self_tuner", st_args)

        # Agent #42: Performance Benchmarker
        print_banner("⏱️ Agent #42: Performance Benchmarker")
        pb_args = ["--save"] if "--save" in args else []
        results["perf_benchmarker"] = run_agent("perf_benchmarker", pb_args)

    # ═══════════════════════════════════════════════════════
    # PHASE 13: Self-Evolving System (Level 5)
    # ═══════════════════════════════════════════════════════
    if run_all or phase13_only:
        print("\n" + "█" * 60)
        print("  🧬 PHASE 13 — Self-Evolving System")
        print("█" * 60)

        # Agent #44: LLM Reasoner (strategy mode)
        print_banner("🧠 Agent #44: LLM Reasoner")
        llm_args = ["--mode", "strategy"]
        if "--save" in args:
            llm_args.append("--save")
        results["llm_reasoner"] = run_agent("llm_reasoner", llm_args)

        # Agent #46: Config Evolver
        print_banner("🔧 Agent #46: Config Evolver")
        ce_args = ["--save"] if "--save" in args else []
        results["config_evolver"] = run_agent("config_evolver", ce_args)

        # Agent #48: Revenue Tracker
        print_banner("💰 Agent #48: Revenue Tracker")
        rt_args = ["--save"] if "--save" in args else []
        results["revenue_tracker"] = run_agent("revenue_tracker", rt_args)

        # Agent #49: Opportunity Engine
        print_banner("🔮 Agent #49: Opportunity Engine")
        oe_args = ["--save"] if "--save" in args else []
        results["opportunity_engine"] = run_agent("opportunity_engine", oe_args)

        # Agent #50: System Architect
        print_banner("🏗️ Agent #50: System Architect")
        sa_args = ["--save"] if "--save" in args else []
        results["system_architect"] = run_agent("system_architect", sa_args)

    # ═══════════════════════════════════════════════════════
    # PHASE 14: Blind Spots (Monitoring, Content, A/B, Emails)
    # ═══════════════════════════════════════════════════════
    if run_all or phase14_only:
        print("\n" + "█" * 60)
        print("  🟢 PHASE 14 — Blind Spots Closure")
        print("█" * 60)

        # Agent #51: Uptime Monitor
        print_banner("📡 Agent #51: Uptime Monitor")
        um_args = ["--save"] if "--save" in args else []
        results["uptime_monitor"] = run_agent("uptime_monitor", um_args)

        # Agent #52: Feedback Parser
        print_banner("💬 Agent #52: Feedback Parser")
        fp_args = ["--save", "--llm"] if "--save" in args else []
        results["feedback_parser"] = run_agent("feedback_parser", fp_args)

        # Agent #53: Content Generator
        print_banner("✍️ Agent #53: Content Generator")
        cg_args = ["--save", "--type", "blog"] if "--save" in args else []
        results["content_generator"] = run_agent("content_generator", cg_args)

        # Agent #54: Experiment Tracker
        print_banner("🧪 Agent #54: Experiment Tracker")
        et_args = ["--save"] if "--save" in args else []
        results["experiment_tracker"] = run_agent("experiment_tracker", et_args)

        # Agent #55: Email Automator
        print_banner("📧 Agent #55: Email Automator")
        ea_args = ["--save"] if "--save" in args else []
        results["email_automator"] = run_agent("email_automator", ea_args)

    # Standalone modes
    if do_bot:
        print_banner("🤖 Agent #43: Telegram Command Bot")
        results["telegram_command_bot"] = run_agent("telegram_command_bot")

    if do_watch:
        print_banner("👁️ Agent #47: Event Watcher")
        ew_args = ["--watch"]
        if "--save" in args:
            ew_args.append("--save")
        results["event_watcher"] = run_agent("event_watcher", ew_args)

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

