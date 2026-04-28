"""
🧪 METAai Test Generator Agent.
Auto-generates pytest unit tests for Python code.
"""
from pathlib import Path
from .base import BaseAgent
from .config import config


SYSTEM_PROMPT = """Ты — опытный QA-инженер. Твоя задача — генерировать pytest тесты для Python кода.

## Правила
1. Генерируй РЕАЛЬНЫЕ, РАБОЧИЕ pytest тесты
2. Каждый тест должен быть самодостаточным
3. Используй pytest fixtures и parametrize где уместно
4. Мокай внешние зависимости (БД, API, файловая система) через unittest.mock
5. Покрывай: happy path, error cases, edge cases
6. Добавляй docstring к каждому тесту
7. Если код асинхронный — используй pytest-asyncio

## Формат ответа
Отвечай ТОЛЬКО кодом Python (pytest тесты). Никакого markdown, никаких пояснений.
Начни с импортов, потом fixtures, потом тесты.

## Naming Convention
- Файл: test_{module_name}.py
- Функции: test_{method}_{scenario}_{expected}
- Пример: test_create_invoice_valid_plan_returns_link

## Обязательные тесты
Для каждой публичной функции:
1. test_*_happy_path — основной сценарий
2. test_*_invalid_input — невалидные данные  
3. test_*_edge_case — граничные значения

Для классов:
1. test_init — создание экземпляра
2. test_*_method — каждый публичный метод
"""


class TestGenAgent(BaseAgent):
    """Generates pytest tests for Python code."""

    def __init__(self):
        super().__init__(config.test_gen, SYSTEM_PROMPT)

    async def generate_tests(self, filepath: Path, context: str = "") -> str:
        """Generate tests for a given Python file."""
        code = filepath.read_text(encoding="utf-8")
        module_name = filepath.stem

        prompt = f"""Сгенерируй pytest тесты для следующего Python модуля.

## Модуль: {module_name}.py
## Контекст: {context}

```python
{code}
```

Сгенерируй максимально полный набор тестов. Мокай все внешние зависимости.
Каждый тест должен быть независимым и самодостаточным.
"""
        response = await self.call(prompt)
        
        # Clean response — remove markdown code blocks if present
        cleaned = response.strip()
        if cleaned.startswith("```python"):
            cleaned = cleaned[len("```python"):].strip()
        if cleaned.startswith("```"):
            cleaned = cleaned[3:].strip()
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3].strip()

        # Save test file
        test_dir = Path("generated_tests")
        test_dir.mkdir(exist_ok=True)
        test_file = test_dir / f"test_{module_name}.py"
        test_file.write_text(cleaned, encoding="utf-8")

        self.log(f"Tests saved: {test_file}")
        return cleaned

    async def generate_for_diff(self, diff: str, context: str = "") -> str:
        """Generate tests based on a code diff."""
        prompt = f"""На основе следующего diff сгенерируй pytest тесты, которые покрывают ВСЕ изменённые функции.

## Diff
```diff
{diff}
```

## Контекст: {context}

Сгенерируй тесты для каждой изменённой функции. Мокай внешние зависимости.
"""
        response = await self.call(prompt)
        
        cleaned = response.strip()
        if cleaned.startswith("```python"):
            cleaned = cleaned[len("```python"):].strip()
        if cleaned.startswith("```"):
            cleaned = cleaned[3:].strip()
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3].strip()

        return cleaned
