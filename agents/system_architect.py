"""
🏗️ Agent #50: System Architect
Анализирует архитектуру METAai, находит blind spots, предлагает новых агентов.

    python -m agents.system_architect               # Анализ
    python -m agents.system_architect --save        # + сохранить
"""

import json
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from agents.config import (
    EVOLUTION_DIR,
)

AGENTS_DIR = Path(__file__).parent


def scan_agents():
    """Сканирует все .py файлы агентов, извлекает docstrings."""
    agents = []
    for py in sorted(AGENTS_DIR.glob("*.py")):
        if py.name.startswith("_") or py.name in ("config.py", "__init__.py"):
            continue

        content = py.read_text(encoding="utf-8", errors="replace")
        lines = content.split("\n")

        # Extract docstring
        docstring = ""
        if len(lines) > 1 and '"""' in lines[0]:
            for i, line in enumerate(lines):
                docstring += line + "\n"
                if i > 0 and '"""' in line:
                    break
        elif len(lines) > 1 and '"""' in lines[1]:
            for i, line in enumerate(lines[1:], 1):
                docstring += line + "\n"
                if i > 1 and '"""' in line:
                    break

        # Extract agent number from docstring
        agent_num = ""
        for line in docstring.split("\n"):
            if "Agent #" in line:
                start = line.find("Agent #") + 7
                end = line.find(":", start) if ":" in line[start:] else start + 3
                agent_num = line[start:end].strip()
                break

        # Count lines
        loc = len([line for line in lines if line.strip() and not line.strip().startswith("#")])

        agents.append({
            "file": py.name,
            "module": py.stem,
            "agent_num": agent_num,
            "docstring": docstring.replace('"""', "").strip()[:100],
            "loc": loc,
            "size_kb": round(py.stat().st_size / 1024, 1),
        })

    return agents


# Coverage domains
BUSINESS_DOMAINS = {
    "code_quality": {
        "name": "Качество кода",
        "agents": ["health_monitor", "changelog_enforcer", "dependency_scanner",
                    "compliance_checker", "git_analytics", "todo_harvester"],
    },
    "deployment": {
        "name": "Деплой и релизы",
        "agents": ["release_manager", "auto_committer", "setup_scheduler"],
    },
    "market_intelligence": {
        "name": "Рыночная разведка",
        "agents": ["trustmrr_scraper", "acquire_scanner", "ph_tracker",
                    "feed_aggregator", "market_scanner"],
    },
    "competitor_intel": {
        "name": "Конкурентная разведка",
        "agents": ["competitor_tracker", "seo_watchdog", "feature_radar",
                    "pricing_monitor"],
    },
    "decision_making": {
        "name": "Принятие решений",
        "agents": ["signal_router", "deal_evaluator", "trend_matcher",
                    "idea_scorer", "opportunity_radar", "action_generator"],
    },
    "reporting": {
        "name": "Отчётность и уведомления",
        "agents": ["telegram_reporter", "weekly_digest", "obsidian_pulse",
                    "sprint_planner"],
    },
    "self_awareness": {
        "name": "Самосознание и эволюция",
        "agents": ["self_tuner", "perf_benchmarker", "knowledge_distiller",
                    "portfolio_tracker", "config_evolver", "system_architect"],
    },
    "intelligence": {
        "name": "AI/LLM интеллект",
        "agents": ["llm_reasoner", "opportunity_engine", "agent_generator"],
    },
    "interface": {
        "name": "Интерфейс пользователя",
        "agents": ["telegram_command_bot"],
    },
    "revenue": {
        "name": "Финансы и платежи",
        "agents": ["revenue_tracker", "cost_monitor", "revenue_forecaster"],
    },
    # === BLIND SPOTS — то, чего нет ===
    "server_monitoring": {
        "name": "Мониторинг серверов",
        "agents": [],  # BLIND SPOT
        "gap": "Нет агента для мониторинга uptime серверов ONYX (6 нод)",
    },
    "customer_feedback": {
        "name": "Обратная связь клиентов",
        "agents": [],  # BLIND SPOT
        "gap": "Нет парсинга отзывов клиентов из Telegram, AppStore, etc.",
    },
    "content_marketing": {
        "name": "Контент-маркетинг",
        "agents": [],  # BLIND SPOT
        "gap": "Нет генерации SEO-контента, блога, social media",
    },
    "ab_testing": {
        "name": "A/B тестирование",
        "agents": [],  # BLIND SPOT
        "gap": "Нет инфраструктуры для экспериментов с ценами/фичами",
    },
    "email_automation": {
        "name": "Email-автоматизация",
        "agents": [],  # BLIND SPOT
        "gap": "Нет cold outreach, re-engagement, onboarding emails",
    },
}


def calculate_coverage(agents):
    """Считает процент покрытия бизнес-доменов."""
    existing = {a["module"] for a in agents}
    total_domains = len(BUSINESS_DOMAINS)
    covered = 0
    gaps = []

    for domain_id, domain in BUSINESS_DOMAINS.items():
        domain_agents = domain["agents"]
        if not domain_agents:
            gaps.append({
                "domain": domain["name"],
                "domain_id": domain_id,
                "gap": domain.get("gap", "Нет агентов"),
            })
        else:
            found = [a for a in domain_agents if a in existing]
            if found:
                covered += 1
            else:
                gaps.append({
                    "domain": domain["name"],
                    "domain_id": domain_id,
                    "gap": f"Агенты запланированы, но не найдены: {domain_agents}",
                })

    coverage_pct = round(covered / total_domains * 100) if total_domains else 0
    return coverage_pct, gaps


def suggest_new_agents(gaps):
    """Предлагает новых агентов для закрытия пробелов."""
    suggestions = []

    for gap in gaps:
        domain = gap["domain_id"]
        if domain == "server_monitoring":
            suggestions.append({
                "name": "Uptime Monitor",
                "module": "uptime_monitor",
                "description": "Пингует серверы ONYX, проверяет HTTP статус, "
                               "трекит response time, алертит при даунтайме",
                "priority": "P0",
                "complexity": "medium",
            })
        elif domain == "customer_feedback":
            suggestions.append({
                "name": "Feedback Parser",
                "module": "feedback_parser",
                "description": "Парсит Telegram @mention'ы, отзывы в ботах, "
                               "sentiment analysis через LLM",
                "priority": "P1",
                "complexity": "high",
            })
        elif domain == "content_marketing":
            suggestions.append({
                "name": "Content Generator",
                "module": "content_generator",
                "description": "SEO-статьи, social media посты, email рассылки "
                               "на основе трендов и competitor intel",
                "priority": "P2",
                "complexity": "high",
            })
        elif domain == "ab_testing":
            suggestions.append({
                "name": "Experiment Tracker",
                "module": "experiment_tracker",
                "description": "Трекинг A/B экспериментов: гипотеза, метрика, "
                               "результат, значимость",
                "priority": "P2",
                "complexity": "medium",
            })
        elif domain == "email_automation":
            suggestions.append({
                "name": "Email Automator",
                "module": "email_automator",
                "description": "Cold outreach, re-engagement, onboarding sequences. "
                               "Через Telegram approve",
                "priority": "P1",
                "complexity": "high",
            })

    return suggestions


def main():
    args = sys.argv[1:]
    save_md = "--save" in args

    print("\n" + "=" * 60)
    print("  🏗️ SYSTEM ARCHITECT — Phase 13 Agent #50")
    print("=" * 60)

    # Scan agents
    agents = scan_agents()
    total_loc = sum(a["loc"] for a in agents)
    total_size = sum(a["size_kb"] for a in agents)

    print("\n  📊 Кодовая база:")
    print(f"    Агенты: {len(agents)}")
    print(f"    LOC: {total_loc:,}")
    print(f"    Размер: {total_size:.0f} KB")

    # Domain coverage
    coverage_pct, gaps = calculate_coverage(agents)
    covered_domains = len(BUSINESS_DOMAINS) - len(gaps)

    print(f"\n  🎯 Покрытие доменов: {coverage_pct}% ({covered_domains}/{len(BUSINESS_DOMAINS)})")

    # Covered domains
    existing = {a["module"] for a in agents}
    print("\n  ✅ Покрытые домены:")
    for domain_id, domain in BUSINESS_DOMAINS.items():
        if domain["agents"]:
            found = [a for a in domain["agents"] if a in existing]
            if found:
                print(f"    🟢 {domain['name']} ({len(found)} агентов)")

    # Blind spots
    if gaps:
        print(f"\n  ❌ Blind Spots ({len(gaps)}):")
        for gap in gaps:
            print(f"    🔴 {gap['domain']}: {gap['gap']}")

    # Suggest new agents
    suggestions = suggest_new_agents(gaps)
    if suggestions:
        print(f"\n  💡 Предложения ({len(suggestions)}):")
        for s in suggestions:
            print(f"\n    🚀 {s['name']} ({s['module']}.py)")
            print(f"       {s['description']}")
            print(f"       Приоритет: {s['priority']} | Сложность: {s['complexity']}")

    # Agent size analysis
    largest = sorted(agents, key=lambda x: -x["loc"])[:5]
    print("\n  📐 Топ-5 по размеру:")
    for a in largest:
        print(f"    {a['module']}: {a['loc']} LOC ({a['size_kb']} KB)")

    if save_md:
        EVOLUTION_DIR.mkdir(parents=True, exist_ok=True)
        report = {
            "timestamp": datetime.now().isoformat(),
            "total_agents": len(agents),
            "total_loc": total_loc,
            "total_size_kb": total_size,
            "coverage_pct": coverage_pct,
            "covered_domains": covered_domains,
            "total_domains": len(BUSINESS_DOMAINS),
            "gaps": gaps,
            "suggestions": suggestions,
            "agents": [
                {"module": a["module"], "loc": a["loc"], "size_kb": a["size_kb"]}
                for a in agents
            ],
        }

        report_path = EVOLUTION_DIR / "architecture.json"
        report_path.write_text(
            json.dumps(report, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        print(f"\n  💾 Сохранено: {report_path}")

    print("\n" + "=" * 60 + "\n")


if __name__ == "__main__":
    main()
