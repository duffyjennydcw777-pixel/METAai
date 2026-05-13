"""
🔬 Full Project Audit — METAai × Sylectus.
Runs all 10 agents against the Sylectus Bid Assistant.
Generates docs/AUDIT_REPORT.md with scorecard.

Usage:
    cd C:\\Users\\Gigabyte\\.gemini\\antigravity\\scratch\\METAai
    python audit_project.py --project C:\\Users\\Gigabyte\\Sylectus
"""
import asyncio
import argparse
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

# Ensure METAai src is importable
sys.path.insert(0, str(Path(__file__).parent))

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
logger = logging.getLogger("audit")

# ── File groups per agent ──────────────────────────────────────────

AUDIT_MAP = {
    "ReviewAgent": {
        "files": [
            "src/app/pipeline.py",
            "src/app/scheduler.py",
            "src/bot/handlers.py",
            "src/webapp/api.py",
        ],
        "context": "Sylectus Bid Assistant v0.15.4. Automated freight bidding. "
                   "Pipeline: parse HTML → validate → score → DB → notify Telegram. "
                   "2 active users, 23 orders/cycle. Production on Hetzner VPS.",
    },
    "SecurityAgent": {
        "files": [
            "src/utils/crypto.py",
            "src/bot/onboarding.py",
            "src/webapp/api.py",
        ],
        "context": "SaaS freight bidding bot. Stores Sylectus credentials encrypted (Fernet AES-256). "
                   "Auth: Telegram initData HMAC-SHA256. RBAC: admin/dispatcher/viewer. "
                   "DEV_MODE must be OFF in production.",
    },
    "ArchitectAgent": {
        "files": [
            "src/app/pipeline.py",
            "src/app/scheduler.py",
            "src/app/use_case.py",
            "src/engine/scoring.py",
            "src/engine/rules.py",
            "src/db/repo.py",
            "src/db/tables.py",
            "src/domain/models.py",
        ],
        "context": "Layered architecture: domain/ → engine/ → app/ → bot/webapp/. "
                   "SQLAlchemy 2.0 async, SQLite + aiosqlite. "
                   "ADRs: fail-loud parser, shadow-first, explainable decisions.",
    },
    "BusinessAgent": {
        "files": [
            "src/app/subscription.py",
            "src/engine/scoring.py",
            "src/engine/rules.py",
        ],
        "context": "Freemium SaaS: 3/7/14/30 day plans ($5-25). Points system. Referral codes. "
                   "Shadow Mode (log only) → Assist Mode (human confirms) → Autopilot. "
                   "Transition at accuracy >= 70% on 100+ orders.",
    },
    "PerformanceAgent": {
        "files": [
            "src/db/repo.py",
            "src/app/scheduler.py",
            "src/bot/notifier.py",
        ],
        "context": "Production polling: 3 min intervals, 23 orders/cycle. "
                   "SQLite single-writer. In-memory dedup cache. "
                   "Session reuse for Sylectus HTTP client (cached per user).",
    },
    "DocsAgent": {
        "files": [
            "docs/1_PRODUCT.md",
            "docs/2_ARCHITECTURE.md",
            "docs/3_INFRASTRUCTURE.md",
            "CHANGELOG.md",
        ],
        "context": "Project documentation. Check: accuracy vs real code, "
                   "completeness, outdated sections (infra docs say 'TODO' for production). "
                   "ROADMAP compliance check.",
    },
    "TestGenAgent": {
        "files": [
            "src/app/pipeline.py",
            "src/engine/scoring.py",
        ],
        "context": "Most critical paths: pipeline (dedup + scoring + DB + notify) "
                   "and scoring engine (cost breakdown + confidence + GO/REVIEW/NO_GO). "
                   "Need comprehensive test coverage before selling.",
    },
    "RefactorAgent": {
        "files": [
            "src/app/scheduler.py",
            "src/webapp/api.py",
            "src/bot/handlers.py",
        ],
        "context": "Largest files: scheduler(551L), api(1327L), handlers(738L). "
                   "Known patterns: inline imports to avoid circular deps, "
                   "30+ lazy imports inside functions. Check for dead code, DRY violations.",
    },
    "UXAgent": {
        "files": [
            "src/bot/locales.py",
            "src/bot/handlers.py",
        ],
        "context": "Telegram bot for Russian-speaking freight operators. "
                   "User-facing: order cards, bid/skip buttons, subscription prompts, "
                   "onboarding flow. Primary language: Russian.",
    },
    "PreflightAgent": {
        "files": [
            "src/app/pipeline.py",
            "src/bot/app.py",
        ],
        "context": "Pre-sale readiness check. Production on 65.109.58.108 (Hetzner). "
                   "CI/CD via GitHub webhook. systemd services: sylectus-bot, sylectus-web. "
                   "SQLite DB. Docker-compose available but not primary.",
    },
}


def collect_code(project_dir: Path, files: list[str]) -> str:
    """Collect code from multiple files into a single string."""
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
    """Build a simple project tree string."""
    lines = []
    for p in sorted(project_dir.rglob("*.py")):
        if ".venv" in str(p) or "__pycache__" in str(p) or ".git" in str(p):
            continue
        rel = p.relative_to(project_dir)
        lines.append(f"  {rel}")
    return "\n".join(lines[:100])  # Cap at 100 files


async def run_agent(
    agent_name: str,
    agent,
    code: str,
    context: str,
    project_dir: Path,
) -> tuple[str, str]:
    """Run a single agent and return (name, report)."""
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
            result = await agent.check_diff(code, "", "Sylectus")
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
    """Run full audit pipeline."""
    start = datetime.now()
    logger.info(f"🔬 Starting full audit of {project_dir}")

    # Initialize agents
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

    # Run agents in strategic order:
    # Phase 1 (parallel): Review, Security, Performance — independent
    # Phase 2 (parallel): Architect, Business, UX — independent
    # Phase 3 (sequential): Docs, TestGen, Refactor, Preflight — may benefit from context

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

    # Phase 3: Completeness (sequential to manage rate limits)
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

    report_md = f"""# 🔬 Sylectus Bid Assistant — Full Audit Report

**Дата**: {datetime.now().strftime("%Y-%m-%d %H:%M")}
**Версия**: v0.15.4
**Агенты**: {len(all_reports)}/10
**Время**: {duration}s
**Стоимость**: см. итого в каждом разделе

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

    # Add each agent report
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
- **Project**: Sylectus Bid Assistant v0.15.4
- **Purpose**: Pre-sale readiness audit
"""

    # Save report
    if output_path is None:
        output_path = project_dir / "docs" / "AUDIT_REPORT.md"

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(report_md, encoding="utf-8")
    logger.info(f"📄 Report saved: {output_path}")

    # Also save to METAai reviews/
    reviews_dir = Path("reviews")
    reviews_dir.mkdir(exist_ok=True)
    ts = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    backup = reviews_dir / f"{ts}_full_audit_sylectus.md"
    backup.write_text(report_md, encoding="utf-8")
    logger.info(f"📄 Backup saved: {backup}")

    print(f"\n{'='*60}")
    print(f"🔬 AUDIT COMPLETE — {len(all_reports)}/10 agents, {duration}s")
    print(f"📄 Report: {output_path}")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="METAai Full Project Audit")
    parser.add_argument(
        "--project",
        type=Path,
        required=True,
        help="Path to project root",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Output report path (default: PROJECT/docs/AUDIT_REPORT.md)",
    )
    args = parser.parse_args()

    asyncio.run(main(args.project, args.output))
