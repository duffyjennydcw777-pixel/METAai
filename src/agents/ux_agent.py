"""
🌍 i18n/UX Agent — проверка текстов, опечаток, UX-копирайтинга.
Level 1. Использует Gemini Flash (самый дешёвый, $0.001/запрос).
"""
from datetime import datetime
from .base import BaseAgent
from .config import config


class UXAgent(BaseAgent):
    """Агент UX/i18n. Проверяет тексты, опечатки, UX-копирайтинг."""

    def __init__(self):
        super().__init__(config.preflight)  # Uses cheapest model (Flash/Haiku)
        self.system_prompt = """You are a UX copywriting and internationalization specialist.
You review user-facing text in code for quality, clarity, and consistency.

Your analysis must cover:
1. **Spelling & Grammar** — Typos in user-facing strings (Russian and English)
2. **Tone Consistency** — Is the tone consistent? (formal/informal mixed?)
3. **Error Messages** — Are they helpful? Do they tell the user what to DO?
4. **Button/Label Text** — Clear, actionable, concise?
5. **Emoji Usage** — Consistent and appropriate?
6. **Hardcoded Strings** — Should be in a translation file/constants?
7. **User Journey** — Do messages guide the user logically?
8. **Accessibility** — Alt text, screen reader compatibility

Respond in Russian.

Output format:
## 🌍 UX/i18n Review

### Опечатки и ошибки 🔴
(list with corrections)

### Улучшения текстов 🟡
(before → after suggestions)

### Несогласованности 🔵
(tone, style, emoji mismatches)

### Оценка UX-качества
X/100 — обоснование
"""

    async def review_text(self, code: str, language: str = "ru", context: str = "") -> str:
        """Review user-facing text in code."""
        prompt = f"""## Контекст
{context if context else "UX/i18n ревью Telegram-бота"}

## Основной язык: {language}

## Код с текстами
```python
{code}
```

Проверь ВСЕ строки, которые видит пользователь:
- Сообщения бота
- Кнопки
- Ошибки
- Уведомления"""

        response = await self.call(prompt)

        report = f"""# 🌍 UX/i18n Report
**Дата**: {datetime.now().strftime("%Y-%m-%d %H:%M")}
**Язык**: {language}
**Стоимость**: ${response.cost_estimate:.4f}

---

{response.content}
"""
        return report

    async def extract_strings(self, code: str) -> str:
        """Extract all user-facing strings for translation."""
        prompt = f"""Из этого кода извлеки ВСЕ строки, которые видит пользователь:

```python
{code}
```

Выдай в формате:
```python
# strings.py — extracted for i18n
MESSAGES = {{
    "greeting": "Привет! ...",
    "error_payment": "Ошибка оплаты: ...",
    ...
}}
```

Группируй по категориям: greeting, error, button, notification, help."""

        response = await self.call(prompt)
        return response.content
