"""
📝 Documentation Agent — автогенерация документации.
Level 1-2. Использует Claude Haiku (дёшево).
Генерирует docstrings, README, API docs.
"""
from datetime import datetime
from .base import BaseAgent
from .config import config


class DocumentationAgent(BaseAgent):
    """Агент документации. Генерирует docstrings, README, API reference."""

    def __init__(self):
        super().__init__(config.preflight)  # Uses Haiku-class model (cheap)
        self.system_prompt = """You are a technical documentation specialist.
You generate clear, concise documentation for Python code.

Your documentation must include:
1. **Docstrings** — Google-style docstrings for all public functions/classes
2. **Type hints** — Proper typing for parameters and return values
3. **Usage examples** — Quick code examples showing how to use each function
4. **Edge cases** — Document non-obvious behavior and gotchas

Rules:
- Use Russian for descriptions, English for code
- Keep docstrings concise but complete
- Include Args, Returns, Raises sections
- Add module-level docstring explaining purpose

Output format:
## 📝 Documentation

For each function/class, provide the complete docstring.
Then provide a README section for the module.
"""

    async def generate_docstrings(self, code: str, filepath: str = "") -> str:
        """Generate docstrings for code."""
        prompt = f"""## Файл: {filepath or "unknown"}

## Код без документации
```python
{code}
```

Сгенерируй Google-style docstrings для КАЖДОЙ функции и класса.
Выдай полный код с добавленными docstrings. Ничего не удаляй, только добавляй."""

        response = await self.call(prompt)

        report = f"""# 📝 Documentation Report
**Файл**: {filepath}
**Дата**: {datetime.now().strftime("%Y-%m-%d %H:%M")}
**Стоимость**: ${response.cost_estimate:.4f}

---

{response.content}
"""
        return report

    async def generate_readme(self, project_structure: str, context: str = "") -> str:
        """Generate README.md for a project."""
        prompt = f"""## Структура проекта
```
{project_structure}
```

## Контекст
{context if context else "Python проект"}

Сгенерируй полный README.md:
- Заголовок + описание
- Установка
- Использование (с примерами команд)
- Структура проекта
- API Reference (если есть)
- License
"""
        response = await self.call(prompt)
        return response.content

    async def check_coverage(self, code: str, filepath: str = "") -> str:
        """Check documentation coverage of existing code."""
        prompt = f"""## Файл: {filepath}

```python
{code}
```

Оцени покрытие документацией:
1. Сколько функций/классов БЕЗ docstring?
2. Сколько БЕЗ type hints?
3. Оценка покрытия X% 
4. Список того, что нужно задокументировать (по приоритету)
"""
        response = await self.call(prompt)
        return response.content
