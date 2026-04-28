"""
🔧 METAai Refactor Agent.
Reads FIXES.md and generates concrete fix code for found issues.
"""
import logging
from pathlib import Path
from .base import BaseAgent
from .config import config

logger = logging.getLogger(__name__)


SYSTEM_PROMPT = """Ты — Senior Python Refactoring Engineer. Тебе дают баг-репорт и исходный код.
Твоя задача — предложить КОНКРЕТНЫЙ, РАБОЧИЙ фикс.

## Правила
1. Возвращай ТОЛЬКО исправленный код (diff или полный блок)
2. Сохраняй обратную совместимость
3. Не ломай существующую логику
4. Добавляй комментарии к критическим изменениям
5. Если баг требует архитектурных изменений — опиши план, НЕ пиши весь код

## Формат ответа
```
## Файл: {filename}
## Проблема: {краткое описание}
## Severity: {CRITICAL|HIGH|MEDIUM|LOW}

### Было:
```python
# старый код
```

### Стало:
```python
# исправленный код
```

### Почему:
Объяснение в 1-2 предложениях.
```

Если проблема архитектурная (race condition, требует Redis, и т.д.) — 
предложи план миграции вместо прямого фикса.
"""


class RefactorAgent(BaseAgent):
    """Proposes concrete fixes for found issues."""

    def __init__(self):
        super().__init__(config.reviewer)  # Use reviewer model for cost efficiency
        self.system_prompt = SYSTEM_PROMPT

    async def fix_issue(self, issue_text: str, code: str, filepath: str = "") -> str:
        """Generate a fix for a specific issue."""
        prompt = f"""Предложи конкретный фикс для следующей проблемы.

## Файл: {filepath}
## Проблема:
{issue_text}

## Текущий код:
```python
{code}
```

Предложи минимальный, безопасный фикс. Не переписывай весь файл.
"""
        response = await self.call(prompt)
        return response.content

    async def fix_from_review(self, review_path: Path) -> str:
        """Parse a review report and generate fixes for critical issues."""
        content = review_path.read_text(encoding="utf-8", errors="ignore")

        prompt = f"""Из следующего code review отчёта извлеки ВСЕ критические проблемы
и предложи конкретные фиксы для каждой.

## Review Report:
{content[:6000]}

Для каждой проблемы предложи:
1. Что изменить
2. Как изменить (конкретный код)
3. Почему это важно
"""
        response = await self.call(prompt)
        
        # Save fix report
        fixes_dir = Path("generated_fixes")
        fixes_dir.mkdir(exist_ok=True)
        fix_file = fixes_dir / f"fixes_{review_path.stem}.md"
        fix_file.write_text(response.content, encoding="utf-8")
        
        logger.info(f"Fixes saved: {fix_file}")
        return response.content
