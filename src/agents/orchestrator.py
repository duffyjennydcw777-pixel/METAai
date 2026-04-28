"""
🎖️ Agent Orchestrator — Диспетчер агентов.
Определяет уровень сложности → вызывает нужных агентов.
"""
import asyncio
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional

from .config import config
from .review_agent import ReviewAgent, get_git_diff
from .preflight_agent import PreflightAgent

logger = logging.getLogger(__name__)


class AgentOrchestrator:
    """
    Главный координатор. Принимает задачу, классифицирует,
    вызывает нужных агентов, собирает отчёт.
    """

    def __init__(self):
        self.review_agent = ReviewAgent()
        self.preflight_agent = PreflightAgent()
        # Security and Test agents can be added later
        self.total_cost = 0.0
        self.reports: list[str] = []

    async def run_pipeline(
        self,
        complexity_level: int,
        diff: Optional[str] = None,
        project_dir: Optional[Path] = None,
        project_name: str = "",
        context: str = "",
    ) -> dict:
        """
        Run the appropriate agent pipeline based on complexity level.

        Level 1 (Trivial): No agents needed, just local checks
        Level 2 (Standard): Review Agent
        Level 3 (Complex): Review + Preflight + (Security, Test — future)
        """
        start = datetime.now()
        results = {
            "level": complexity_level,
            "project": project_name,
            "timestamp": start.isoformat(),
            "agents_used": [],
            "reports": [],
            "total_cost": 0.0,
            "verdict": "unknown",
        }

        # Get diff if not provided
        if diff is None:
            diff = get_git_diff(staged=True) or get_git_diff()
            if not diff.strip():
                diff = get_git_diff(last_commit=True)

        if not diff.strip():
            results["verdict"] = "⚠️ Нет diff для анализа"
            return results

        # === LEVEL 1: Local checks only ===
        if complexity_level == 1:
            results["verdict"] = "🟢 Level 1 — Trivial. Агенты не нужны. Деплой."
            if project_dir:
                local = await self.preflight_agent.check_project(project_dir)
                results["local_checks"] = local
            return results

        # === LEVEL 2: Review Agent ===
        if complexity_level >= 2:
            logger.info("🔍 Запускаю Review Agent...")
            review_report = await self.review_agent.review_diff(diff, context)
            results["agents_used"].append("ReviewAgent")
            results["reports"].append(review_report)

            # Save report
            self.review_agent.save_report(
                review_report, "review", project_name or "unknown"
            )

        # === LEVEL 3: Full pipeline ===
        if complexity_level >= 3:
            logger.info("🚀 Запускаю Preflight Agent...")

            # Preflight AI check
            env_example = ""
            if project_dir:
                env_example_path = project_dir / ".env.example"
                if env_example_path.exists():
                    env_example = env_example_path.read_text(encoding="utf-8")

            preflight_result = await self.preflight_agent.check_diff(
                diff, env_example, project_name
            )
            results["agents_used"].append("PreflightAgent")

            # Format preflight report
            pf = preflight_result.get("result", {})
            pf_report = f"""## 🚀 Preflight Check
**Рекомендация**: {pf.get('recommendation', 'N/A')}
**Уверенность**: {pf.get('confidence', 0)}%
**Safe to Deploy**: {'✅' if pf.get('safe_to_deploy') else '❌'}
"""
            for issue in pf.get("issues", []):
                icon = {"critical": "🔴", "warning": "🟡", "info": "🟢"}.get(issue.get("severity"), "❓")
                pf_report += f"\n{icon} [{issue.get('severity')}] {issue.get('message')}"

            pf_meta = preflight_result.get("meta", "")
            pf_report += f"\n\n📊 {pf_meta}"
            results["reports"].append(pf_report)

            # Local checks
            if project_dir:
                local = await self.preflight_agent.check_project(project_dir)
                results["local_checks"] = local

            # TODO: Security Agent (Level 3 + auth/crypto)
            # TODO: Test Generator Agent (Level 2-3)

        # Final verdict
        duration = int((datetime.now() - start).total_seconds() * 1000)
        results["duration_ms"] = duration
        results["verdict"] = self._determine_verdict(results)

        # Print summary
        self._print_summary(results)

        return results

    def _determine_verdict(self, results: dict) -> str:
        """Determine final verdict based on all agent reports."""
        reports_text = " ".join(str(r) for r in results.get("reports", []))

        if "DO NOT DEPLOY" in reports_text or "🚫" in reports_text:
            return "🚫 DO NOT DEPLOY — критичные проблемы найдены"
        elif "NEEDS FIXES" in reports_text or "⚠️" in reports_text:
            return "⚠️ NEEDS FIXES — есть замечания, исправить перед деплоем"
        elif "SAFE TO DEPLOY" in reports_text or "✅" in reports_text:
            return "✅ SAFE TO DEPLOY — код проверен, можно деплоить"
        else:
            return "❓ Не удалось определить — проверь отчёты вручную"

    def _print_summary(self, results: dict):
        """Print a human-readable summary."""
        print("\n" + "=" * 60)
        print(f"📊 METAai Agent Pipeline — Level {results['level']}")
        print("=" * 60)
        print(f"🏗️  Проект: {results['project']}")
        print(f"🤖 Агенты: {', '.join(results['agents_used']) or 'Нет'}")
        print(f"⏱️  Время: {results.get('duration_ms', 0)}ms")
        print(f"🏁 Вердикт: {results['verdict']}")
        print("=" * 60 + "\n")
