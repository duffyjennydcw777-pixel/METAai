"""
🔬 Full Project Audit — METAai × FamilyQuest.
Runs all 10 agents against the FamilyQuest codebase.
Generates docs/AUDIT_REPORT.md with scorecard.

Usage:
    cd C:\\Users\\Gigabyte\\.gemini\\antigravity\\scratch\\METAai
    python audit_project.py --project C:\\Users\\Gigabyte\\.gemini\\antigravity\\scratch\\FamilyQuest
"""
import asyncio
import argparse
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

# Ensure METAai src is importable
sys.path.insert(0, str(Path(__file__).parent.parent))  # METAai root

from src.agents.review_agent import ReviewAgent
from src.agents.architect_agent import ArchitectAgent
from src.agents.business_agent import BusinessLogicAgent
from src.agents.performance_agent import PerformanceAgent
from src.agents.docs_agent import DocumentationAgent
from src.agents.test_gen_agent import TestGenAgent
from src.agents.refactor_agent import RefactorAgent
from src.agents.ux_agent import UXAgent
from src.agents.preflight_agent import PreflightAgent

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(name)s | %(message)s")
logger = logging.getLogger("audit-familyquest")

# ── FamilyQuest AUDIT MAP ──────────────────────────────────────────

PROJECT_CONTEXT = (
    "FamilyQuest — Telegram Mini App для геймификации домашних обязанностей детей. "
    "Backend: Python 3.11 + FastAPI + aiogram 3 + SQLAlchemy 2.0 async + PostgreSQL. "
    "Frontend: Vite + TailwindCSS v4 + Lucide + Vanilla JS. "
    "Пользователи: 1 родитель (admin) + 3 ребёнка (Арсамат 12, Урузмаг 10, Айсана 7). "
    "HMAC auth через Telegram initData. Двойной UI mode: standard и kid-friendly. "
    "Сервер: ONYX (92.246.137.35:2222), единый systemd service для bot+API."
)

AUDIT_MAP = {
    "ReviewAgent": {
        "files": [
            "backend/main.py",
            "backend/api.py",
            "backend/handlers/parent_handlers.py",
            "backend/handlers/child_handlers.py",
        ],
        "context": PROJECT_CONTEXT + " Review the code quality, error handling, and maintainability.",
    },
    "SecurityAgent": {
        "files": [
            "backend/api.py",
            "backend/config.py",
            "backend/database.py",
            "webapp/src/api.js",
        ],
        "context": PROJECT_CONTEXT + (
            " Auth: Telegram initData HMAC-SHA256 validation. "
            "Header: X-Init-Data. Bot token used as HMAC secret. "
            "PostgreSQL with asyncpg. No user passwords (Telegram auth only). "
            "Check: HMAC validation correctness, SQL injection, XSS, CSRF, secrets exposure."
        ),
    },
    "ArchitectAgent": {
        "files": [
            "backend/main.py",
            "backend/api.py",
            "backend/models.py",
            "backend/database.py",
            "backend/config.py",
            "backend/services/quest_service.py",
            "backend/services/xp_service.py",
            "backend/services/streak_service.py",
            "backend/services/reward_service.py",
        ],
        "context": PROJECT_CONTEXT + (
            " ADR-001: bot+API in single process (asyncio.gather). "
            "Models: User, Quest, XPLog, Reward, RewardClaim, DailyActivity, Achievement. "
            "All Telegram IDs use BigInteger (PY-004). All datetimes timezone-aware (PY-007)."
        ),
    },
    "BusinessAgent": {
        "files": [
            "backend/services/quest_service.py",
            "backend/services/xp_service.py",
            "backend/services/streak_service.py",
            "backend/services/reward_service.py",
        ],
        "context": PROJECT_CONTEXT + (
            " Quest flow: parent creates → child submits → parent approves/rejects → XP awarded. "
            "Streak system: daily activity tracking, freeze (1/week), bonuses at 3/7/14/30 days. "
            "Reward shop: child spends XP on rewards (phone time, treats, activities). "
            "Level system: 10 levels, kid-friendly XP multiplier (1.5x for Айсана)."
        ),
    },
    "PerformanceAgent": {
        "files": [
            "backend/database.py",
            "backend/services/xp_service.py",
            "backend/services/streak_service.py",
            "backend/api.py",
        ],
        "context": PROJECT_CONTEXT + (
            " 4 users total (1 parent + 3 children). PostgreSQL async pool_size=5. "
            "No heavy queries expected. Check: N+1 queries, session management, pool leaks."
        ),
    },
    "DocsAgent": {
        "files": [
            "docs/1_PRODUCT.md",
            "docs/2_ARCHITECTURE.md",
            "docs/3_INFRASTRUCTURE.md",
            "docs/4_DEPLOY_RUNBOOK.md",
            "CHANGELOG.md",
        ],
        "context": PROJECT_CONTEXT + " Check documentation completeness, accuracy vs real code.",
    },
    "TestGenAgent": {
        "files": [
            "backend/services/quest_service.py",
            "backend/services/xp_service.py",
            "backend/api.py",
        ],
        "context": PROJECT_CONTEXT + (
            " Critical paths: quest submission+approval flow, XP calculation+leveling, "
            "HMAC auth validation, streak calculation. Generate pytest-asyncio tests."
        ),
    },
    "RefactorAgent": {
        "files": [
            "backend/handlers/parent_handlers.py",
            "backend/api.py",
            "webapp/src/main.js",
            "webapp/src/screens/Quests.js",
        ],
        "context": PROJECT_CONTEXT + (
            " parent_handlers.py is 551 lines (largest file). "
            "Check: dead code, DRY violations, overly large functions, magic numbers."
        ),
    },
    "UXAgent": {
        "files": [
            "backend/handlers/child_handlers.py",
            "backend/handlers/parent_handlers.py",
            "webapp/src/screens/Dashboard.js",
            "webapp/src/screens/Shop.js",
        ],
        "context": PROJECT_CONTEXT + (
            " Telegram bot + Mini App for Russian-speaking family. "
            "Users: father (admin, creates quests) + 3 kids (complete quests, earn XP). "
            "Kid-friendly UI for 7-year-old (Айсана). Primary language: Russian."
        ),
    },
    "PreflightAgent": {
        "files": [
            "backend/main.py",
            "backend/config.py",
            "deploy/deploy.ps1",
            "deploy/familyquest.service",
        ],
        "context": PROJECT_CONTEXT + (
            " Deploy target: ONYX server 92.246.137.35:2222 (shared with ONYX VPN bot). "
            "systemd service: familyquest.service. Nginx reverse proxy. "
            "PostgreSQL 15 on same server. Domain: fq.ironyx.tech via Cloudflare."
        ),
    },
}


def collect_code(project_dir: Path, files: list[str]) -> str:
    parts = []
    for rel in files:
        fp = project_dir / rel
        if not fp.exists():
            parts.append(f"# === FILE NOT FOUND: {rel} ===\n")
            continue
        try:
            content = fp.read_text(encoding="utf-8", errors="replace")
        except Exception as e:
            parts.append(f"# === ERROR reading {rel}: {e} ===\n")
            continue
        parts.append(f"# === FILE: {rel} ({len(content.splitlines())} lines) ===\n{content}\n")
    return "\n".join(parts)


def build_tree(project_dir: Path) -> str:
    lines = []
    for ext in ("*.py", "*.js", "*.css", "*.html", "*.md", "*.json"):
        for p in sorted(project_dir.rglob(ext)):
            skip = any(s in str(p) for s in [".venv", "venv", "__pycache__", ".git", "node_modules", "dist"])
            if skip:
                continue
            rel = p.relative_to(project_dir)
            lines.append(f"  {rel}")
    return "\n".join(sorted(set(lines))[:100])


async def run_agent(agent_name, agent, code, context, project_dir):
    logger.info(f"▶ Starting {agent_name}...")
    try:
        if agent_name == "ReviewAgent":
            report = await agent.review_diff(code, context)
        elif agent_name == "SecurityAgent":
            report = await agent.audit_diff(code, context)
        elif agent_name == "ArchitectAgent":
            report = await agent.analyze_project(code, context)
        elif agent_name == "BusinessAgent":
            report = await agent.audit(code, context)
        elif agent_name == "PerformanceAgent":
            report = await agent.analyze(code, context)
        elif agent_name == "DocsAgent":
            report = await agent.check_coverage(code, "docs/")
        elif agent_name == "TestGenAgent":
            report = await agent.generate_for_diff(code, context)
        elif agent_name == "RefactorAgent":
            report = await agent.fix_issue(
                "Find code smells, DRY violations, dead code, and overly large functions",
                code,
                "multiple files",
            )
        elif agent_name == "UXAgent":
            report = await agent.review_text(code, "ru", context)
        elif agent_name == "PreflightAgent":
            result = await agent.check_diff(code, "", "FamilyQuest")
            pf = result.get("result", {})
            report = (
                f"## 🚀 Preflight Check\n"
                f"**Safe to Deploy**: {'✅' if pf.get('safe_to_deploy') else '❌'}\n"
                f"**Recommendation**: {pf.get('recommendation', 'N/A')}\n"
                f"**Confidence**: {pf.get('confidence', 0)}%\n"
            )
            for issue in pf.get("issues", []):
                icon = {"critical": "🔴", "warning": "🟡", "info": "🟢"}.get(
                    issue.get("severity"), "❓"
                )
                report += f"\n{icon} [{issue['severity']}] {issue['message']}"
        else:
            report = f"Unknown agent: {agent_name}"

        logger.info(f"✅ {agent_name} complete")
        return agent_name, report

    except Exception as e:
        logger.error(f"❌ {agent_name} failed: {e}")
        return agent_name, f"## ❌ {agent_name} — ERROR\n\n```\n{e}\n```"


async def main(project_dir: Path, output_path: Optional[Path] = None):
    start = datetime.now()
    logger.info(f"🔬 Starting FamilyQuest audit of {project_dir}")

    agents = {
        "ReviewAgent": ReviewAgent(),
        "SecurityAgent": __import__("src.agents.security_agent", fromlist=["SecurityAgent"]).SecurityAgent(),
        "ArchitectAgent": ArchitectAgent(),
        "BusinessAgent": BusinessLogicAgent(),
        "PerformanceAgent": PerformanceAgent(),
        "DocsAgent": DocumentationAgent(),
        "TestGenAgent": TestGenAgent(),
        "RefactorAgent": RefactorAgent(),
        "UXAgent": UXAgent(),
        "PreflightAgent": PreflightAgent(),
    }

    all_reports: dict[str, str] = {}

    # Phase 1: Core analysis (parallel)
    phase1 = ["ReviewAgent", "SecurityAgent", "PerformanceAgent"]
    logger.info("═══ Phase 1: Core Analysis ═══")
    phase1_tasks = []
    for name in phase1:
        cfg = AUDIT_MAP[name]
        code = collect_code(project_dir, cfg["files"])
        phase1_tasks.append(run_agent(name, agents[name], code, cfg["context"], project_dir))
    results = await asyncio.gather(*phase1_tasks)
    for name, report in results:
        all_reports[name] = report

    # Phase 2: Domain analysis (parallel)
    phase2 = ["ArchitectAgent", "BusinessAgent", "UXAgent"]
    logger.info("═══ Phase 2: Domain Analysis ═══")
    phase2_tasks = []
    for name in phase2:
        cfg = AUDIT_MAP[name]
        code = collect_code(project_dir, cfg["files"])
        phase2_tasks.append(run_agent(name, agents[name], code, cfg["context"], project_dir))
    results = await asyncio.gather(*phase2_tasks)
    for name, report in results:
        all_reports[name] = report

    # Phase 3: Completeness (sequential for rate limits)
    phase3 = ["DocsAgent", "TestGenAgent", "RefactorAgent", "PreflightAgent"]
    logger.info("═══ Phase 3: Completeness ═══")
    for name in phase3:
        cfg = AUDIT_MAP[name]
        code = collect_code(project_dir, cfg["files"])
        _, report = await run_agent(name, agents[name], code, cfg["context"], project_dir)
        all_reports[name] = report

    # Build final report
    duration = int((datetime.now() - start).total_seconds())
    tree = build_tree(project_dir)

    report_md = f"""# 🔬 FamilyQuest — Full 10-Agent Audit Report

**Дата**: {datetime.now().strftime("%Y-%m-%d %H:%M")}
**Проект**: FamilyQuest (Telegram Mini App)
**Агенты**: {len(all_reports)}/10
**Время**: {duration}s

---

## 📋 Scorecard

| Агент | Область | Статус |
|-------|---------|--------|
| 🔍 Review | Code Quality | {'✅' if 'ReviewAgent' in all_reports else '❌'} |
| 🛡️ Security | Auth & Crypto | {'✅' if 'SecurityAgent' in all_reports else '❌'} |
| 🏗️ Architect | Architecture | {'✅' if 'ArchitectAgent' in all_reports else '❌'} |
| 💰 Business | Business Logic | {'✅' if 'BusinessAgent' in all_reports else '❌'} |
| ⚡ Performance | Speed & Memory | {'✅' if 'PerformanceAgent' in all_reports else '❌'} |
| 📝 Docs | Documentation | {'✅' if 'DocsAgent' in all_reports else '❌'} |
| 🧪 TestGen | Test Coverage | {'✅' if 'TestGenAgent' in all_reports else '❌'} |
| ♻️ Refactor | Code Smells | {'✅' if 'RefactorAgent' in all_reports else '❌'} |
| 🎨 UX | User Experience | {'✅' if 'UXAgent' in all_reports else '❌'} |
| 🚀 Preflight | Deploy Safety | {'✅' if 'PreflightAgent' in all_reports else '❌'} |

---

## 🗂️ Project Structure

```
{tree}
```

---

"""

    agent_order = [
        "ArchitectAgent", "SecurityAgent", "BusinessAgent",
        "ReviewAgent", "PerformanceAgent", "RefactorAgent",
        "DocsAgent", "TestGenAgent", "UXAgent", "PreflightAgent",
    ]
    for name in agent_order:
        if name in all_reports:
            report_md += f"\n---\n\n{all_reports[name]}\n\n"

    report_md += f"""
---

## 📊 Summary

- **Total agents run**: {len(all_reports)}
- **Total duration**: {duration}s
- **Generated at**: {datetime.now().isoformat()}
- **Project**: FamilyQuest
"""

    if output_path is None:
        output_path = project_dir / "docs" / "AUDIT_REPORT.md"

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(report_md, encoding="utf-8")
    logger.info(f"📄 Report saved: {output_path}")

    # Also save to METAai reviews/
    metaai_root = Path(__file__).parent.parent
    reviews_dir = metaai_root / "reviews"
    reviews_dir.mkdir(exist_ok=True)
    ts = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    backup = reviews_dir / f"{ts}_full_audit_familyquest.md"
    backup.write_text(report_md, encoding="utf-8")
    logger.info(f"📄 Backup saved: {backup}")

    print(f"\n{'='*60}")
    print(f"🔬 AUDIT COMPLETE — {len(all_reports)}/10 agents, {duration}s")
    print(f"📄 Report: {output_path}")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="METAai Full Project Audit — FamilyQuest")
    parser.add_argument(
        "--project",
        type=Path,
        default=Path(r"C:\Users\Gigabyte\.gemini\antigravity\scratch\FamilyQuest"),
        help="Path to FamilyQuest root",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Output report path",
    )
    args = parser.parse_args()

    asyncio.run(main(args.project, args.output))
