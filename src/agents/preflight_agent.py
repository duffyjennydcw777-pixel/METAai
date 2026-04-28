"""
🚀 Preflight Agent — Pre-deploy проверка.
Проверяет конфиги, .env, порты, зависимости перед деплоем.
"""
import subprocess
import os
from pathlib import Path
from datetime import datetime
from typing import Optional

from .base import BaseAgent
from .config import config


class PreflightAgent(BaseAgent):
    """Агент pre-deploy проверки. Самый дешёвый — Gemini Flash."""

    def __init__(self):
        super().__init__(config.preflight)
        self.system_prompt = """You are a deployment safety checker. Your job is to prevent bad deploys.

Check for:
1. **Config issues** — Missing env vars, wrong ports, wrong URLs
2. **File issues** — Missing files, wrong permissions pattern
3. **Dependency issues** — Uninstalled packages, version conflicts
4. **Security issues** — Secrets in code, debug mode in production
5. **Breaking changes** — API contract changes, DB schema changes without migration

Respond in Russian. Be concise.

Output JSON:
{
    "safe_to_deploy": true/false,
    "issues": [
        {"severity": "critical|warning|info", "message": "описание"}
    ],
    "confidence": 0-100,
    "recommendation": "деплоить / исправить сначала / СТОП"
}"""

    async def check_diff(self, diff: str, env_example: str = "", project_name: str = "") -> dict:
        """Check if a diff is safe to deploy."""
        prompt = f"""## Проект: {project_name or "unknown"}

## Diff для деплоя
```diff
{diff}
```

## .env.example (для проверки переменных)
```
{env_example}
```

Проверь безопасность деплоя. Ответь JSON."""

        result = await self.call_json(prompt)
        return result

    async def check_project(self, project_dir: Path) -> dict:
        """Full preflight check of a project directory."""
        checks = []

        # Check .env exists
        env_file = project_dir / ".env"
        env_example = project_dir / ".env.example"
        if not env_file.exists() and env_example.exists():
            checks.append({
                "severity": "critical",
                "message": ".env файл отсутствует, но .env.example существует"
            })

        # Check .env has all keys from .env.example
        if env_file.exists() and env_example.exists():
            example_keys = self._extract_env_keys(env_example)
            actual_keys = self._extract_env_keys(env_file)
            missing = example_keys - actual_keys
            if missing:
                checks.append({
                    "severity": "warning",
                    "message": f"Отсутствуют env переменные: {', '.join(missing)}"
                })

        # Check for hardcoded secrets in Python files
        secret_patterns = ["api_key=", "token=", "password=", "secret="]
        for py_file in project_dir.rglob("*.py"):
            if ".venv" in str(py_file) or "node_modules" in str(py_file):
                continue
            try:
                content = py_file.read_text(encoding="utf-8").lower()
                for pattern in secret_patterns:
                    if pattern in content and "os.getenv" not in content and "os.environ" not in content:
                        # Rough heuristic — might have false positives
                        if "example" not in str(py_file) and "test" not in str(py_file):
                            checks.append({
                                "severity": "warning",
                                "message": f"Возможный хардкод секрета в {py_file.name}: паттерн '{pattern}'"
                            })
            except Exception:
                pass

        # Check git status
        try:
            result = subprocess.run(
                ["git", "status", "--porcelain"],
                capture_output=True, text=True,
                cwd=str(project_dir),
            )
            uncommitted = len(result.stdout.strip().split("\n")) if result.stdout.strip() else 0
            if uncommitted > 5:
                checks.append({
                    "severity": "warning",
                    "message": f"{uncommitted} незакоммиченных файлов. Git-дисциплина!"
                })
        except Exception:
            pass

        # Check CHANGELOG
        changelog = project_dir / "CHANGELOG.md"
        if not changelog.exists():
            checks.append({
                "severity": "warning",
                "message": "CHANGELOG.md отсутствует"
            })

        safe = not any(c["severity"] == "critical" for c in checks)

        return {
            "safe_to_deploy": safe,
            "issues": checks,
            "confidence": 90 if not checks else 60,
            "recommendation": "деплоить" if safe and len(checks) < 2 else "исправить сначала",
            "local_checks_only": True,
        }

    @staticmethod
    def _extract_env_keys(env_path: Path) -> set[str]:
        """Extract variable names from an .env file."""
        keys = set()
        for line in env_path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key = line.split("=", 1)[0].strip()
                keys.add(key)
        return keys
