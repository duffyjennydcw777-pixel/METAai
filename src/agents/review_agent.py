"""
🔍 Review Agent — Code Review через AI.
Анализирует git diff и выдаёт структурированный отчёт.
"""
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Optional

from .base import BaseAgent
from .config import config


class ReviewAgent(BaseAgent):
    """Агент для code review. Проверяет diff на баги, стиль, anti-patterns."""

    def __init__(self):
        super().__init__(config.reviewer)
        self.system_prompt = """You are an expert code reviewer. You review diffs with extreme attention to detail.

Your review must cover:
1. **Bugs & Logic Errors** — Will this code work correctly? Edge cases?
2. **Security** — Any hardcoded secrets, injection risks, auth bypasses?
3. **Performance** — N+1 queries, unnecessary loops, memory leaks?
4. **Style & Patterns** — Naming conventions, code duplication, SRP violations?
5. **Error Handling** — Are exceptions caught properly? Missing try/except?
6. **Breaking Changes** — Could this break existing functionality?

Respond in Russian. Be direct and specific. No fluff.

Output format:
## 🔍 Code Review

### Критичные проблемы 🔴
(list or "Нет")

### Предупреждения 🟡
(list or "Нет")

### Замечания 🟢
(list or "Нет")

### Вердикт
✅ SAFE TO DEPLOY / ⚠️ NEEDS FIXES / 🚫 DO NOT DEPLOY

### Оценка уверенности
X/100 — обоснование
"""

    async def review_diff(self, diff: str, context: str = "") -> str:
        """Review a git diff and return structured report."""
        prompt = f"""## Контекст
{context if context else "Нет дополнительного контекста"}

## Diff для review
```diff
{diff}
```

Проведи code review по чеклисту из system prompt."""

        response = await self.call(prompt)

        # Build full report
        report = f"""# 🔍 Code Review Report
**Дата**: {datetime.now().strftime("%Y-%m-%d %H:%M")}
**Модель**: {response.model}
**Токены**: {response.input_tokens}→{response.output_tokens}
**Стоимость**: ${response.cost_estimate:.4f}
**Время**: {response.duration_ms}ms

---

{response.content}
"""
        return report

    async def review_file(self, filepath: Path, context: str = "") -> str:
        """Review an entire file."""
        content = filepath.read_text(encoding="utf-8")
        prompt = f"""## Файл: {filepath.name}
## Контекст
{context if context else "Полный review файла"}

## Код
```python
{content}
```

Проведи code review по чеклисту из system prompt."""

        response = await self.call(prompt)
        return response.content


def get_git_diff(staged: bool = False, last_commit: bool = False) -> str:
    """Get git diff from the current repository."""
    try:
        if last_commit:
            cmd = ["git", "diff", "HEAD~1", "HEAD"]
        elif staged:
            cmd = ["git", "diff", "--cached"]
        else:
            cmd = ["git", "diff"]

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        return result.stdout
    except Exception as e:
        return f"Error getting git diff: {e}"
