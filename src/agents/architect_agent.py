"""
🏗️ Architect Agent — анализ архитектуры и проектирование.
Level 3. Использует Claude Sonnet.
Анализирует код на архитектурные паттерны, интерфейсы, зависимости.
"""
from datetime import datetime

from .base import BaseAgent
from .config import config


class ArchitectAgent(BaseAgent):
    """Агент-архитектор. Анализирует структуру проекта, предлагает интерфейсы."""

    def __init__(self):
        super().__init__(config.architect)
        self.system_prompt = """You are a senior software architect with 15+ years of experience.
Your job is to analyze code/projects and provide architectural assessment.

Your analysis must cover:
1. **Architecture Pattern** — What pattern is used? (MVC, Clean Architecture, Layered, etc.)
2. **Separation of Concerns** — Are responsibilities properly separated?
3. **Dependency Direction** — Do dependencies flow correctly? (from high to low level)
4. **Abstractions** — Are interfaces/protocols used? Or is everything tightly coupled?
5. **Scalability** — Will this architecture handle 10x load? 100x?
6. **Single Points of Failure** — What breaks everything if it goes down?
7. **Technical Debt** — Shortcuts that will hurt later

Respond in Russian. Be specific — reference file names and line numbers.

Output format:
## 🏗️ Architectural Analysis

### Паттерн
(identified architecture pattern)

### Сильные стороны 💪
(list)

### Архитектурный долг 🏚️
(list with severity: CRITICAL/HIGH/MEDIUM)

### Рекомендации 📐
(specific actionable items)

### Оценка зрелости
X/10 — обоснование
"""

    async def analyze_project(self, code: str, context: str = "") -> str:
        """Analyze project architecture."""
        prompt = f"""## Контекст
{context if context else "Архитектурный анализ проекта"}

## Код для анализа
```python
{code}
```

Проведи архитектурный анализ по чеклисту из system prompt."""

        response = await self.call(prompt)

        report = f"""# 🏗️ Architect Report
**Дата**: {datetime.now().strftime("%Y-%m-%d %H:%M")}
**Модель**: {response.model}
**Стоимость**: ${response.cost_estimate:.4f}

---

{response.content}
"""
        return report

    async def design_interface(self, requirements: str) -> str:
        """Design interfaces/contracts for a new feature."""
        prompt = f"""Спроектируй интерфейсы и контракты для:

{requirements}

Выдай:
1. Абстрактные классы / Protocol'ы
2. Типизацию (dataclasses / TypedDict)
3. Диаграмму зависимостей
4. Точки расширения
"""
        response = await self.call(prompt)
        return response.content
