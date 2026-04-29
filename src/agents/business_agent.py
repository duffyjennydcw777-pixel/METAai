"""
💰 Business Logic Agent — проверка бизнес-правил.
Level 3. Использует Claude Sonnet.
Проверяет: подписки, биллинг, права доступа, бизнес-инварианты.
"""
from datetime import datetime
from .base import BaseAgent
from .config import config


class BusinessLogicAgent(BaseAgent):
    """Агент бизнес-логики. Проверяет корректность бизнес-правил в коде."""

    def __init__(self):
        super().__init__(config.reviewer)  # Uses reviewer model
        self.system_prompt = """You are a business logic auditor specializing in SaaS and payment systems.
You verify that code correctly implements business rules.

Your analysis must cover:
1. **Subscription Logic** — Correct state transitions (trial→active→expired→cancelled)
2. **Payment Validation** — Amount checks, currency handling, refund flows, double-charge prevention
3. **Access Control** — Permissions enforced at every entry point, not just UI
4. **Rate Limiting** — Free vs paid tier limits properly enforced
5. **Data Integrity** — Transactions used for multi-step operations, no partial writes
6. **Edge Cases** — Concurrent subscriptions, timezone issues, expiry at midnight, leap years
7. **Audit Trail** — Are financial operations logged? Can you trace every transaction?
8. **Regulatory** — GDPR data handling, payment data not logged in plaintext

Respond in Russian. Be specific about which business rule is violated and why.

Output format:
## 💰 Business Logic Audit

### Нарушения бизнес-правил 🔴
(each: rule violated, where, consequence, fix)

### Потенциальные потери 🟡
(scenarios where money could be lost/stolen)

### Корректные правила ✅
(what's done right)

### Финансовый риск
LOW / MEDIUM / HIGH / CRITICAL
"""

    async def audit(self, code: str, context: str = "") -> str:
        """Audit business logic in code."""
        prompt = f"""## Контекст
{context if context else "Аудит бизнес-логики SaaS-приложения"}

## Код
```python
{code}
```

Проведи аудит бизнес-логики по чеклисту из system prompt.
Обрати особое внимание на: подписки, платежи, доступ."""

        response = await self.call(prompt)

        report = f"""# 💰 Business Logic Report
**Дата**: {datetime.now().strftime("%Y-%m-%d %H:%M")}
**Модель**: {response.model}
**Стоимость**: ${response.cost_estimate:.4f}

---

{response.content}
"""
        return report

    async def verify_subscription_flow(self, code: str) -> str:
        """Specifically verify subscription state machine."""
        prompt = f"""Проверь реализацию подписочной модели:

```python
{code}
```

Верифицируй:
1. Все состояния подписки (trial, active, past_due, cancelled, expired)
2. Все переходы между состояниями
3. Что происходит при неудачном платеже
4. Есть ли grace period
5. Правильно ли считается дата следующего платежа
6. Обработка upgrade/downgrade

Выдай state diagram и список найденных проблем."""

        response = await self.call(prompt)
        return response.content
