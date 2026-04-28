"""
🛡️ Security Agent — Аудит безопасности кода.
Ищет уязвимости: SQL injection, XSS, secrets, auth bypass.
"""
from pathlib import Path

from .base import BaseAgent
from .config import config


class SecurityAgent(BaseAgent):
    """Агент для security audit. Фокус на уязвимостях."""

    def __init__(self):
        super().__init__(config.security)
        self.system_prompt = """You are a senior security auditor. You perform thorough security reviews of code.

Your audit must cover:
1. **Secrets & Credentials** — Hardcoded API keys, passwords, tokens in code
2. **Injection** — SQL injection, command injection, XSS, template injection
3. **Authentication** — Auth bypass, missing auth checks, session issues
4. **Authorization** — Privilege escalation, IDOR, missing access controls
5. **Data Exposure** — Sensitive data in logs, error messages, responses
6. **Input Validation** — Missing validation, type confusion, buffer overflow
7. **Cryptography** — Weak algorithms, improper key management
8. **Dependencies** — Known vulnerable packages, supply chain risks

Respond in Russian. Be extremely thorough but practical.

Severity levels:
- 🔴 CRITICAL — exploitable now, immediate fix required
- 🟠 HIGH — exploitable with effort, fix before deploy
- 🟡 MEDIUM — potential risk, fix soon
- 🟢 LOW — best practice improvement

Output format:
## 🛡️ Security Audit

### Найденные уязвимости
(table: Severity | Category | Description | Location | Fix)

### Рекомендации по харденингу
(list of hardening steps)

### Вердикт безопасности
PASS ✅ / CONDITIONAL ⚠️ / FAIL 🚫

### Risk Score
X/100 (100 = максимально безопасно)
"""

    async def audit_diff(self, diff: str, context: str = "") -> str:
        """Audit a diff for security issues."""
        prompt = f"""## Контекст
{context if context else "Security audit кода"}

## Код для аудита
```diff
{diff}
```

Проведи полный security audit по чеклисту из system prompt.
Будь максимально конкретным — указывай строки, переменные, паттерны."""

        response = await self.call(prompt)
        from datetime import datetime

        report = f"""## 🛡️ Security Audit Report
**Дата**: {datetime.now().strftime("%Y-%m-%d %H:%M")}
**Модель**: {response.model}
**Токены**: {response.input_tokens}→{response.output_tokens}
**Стоимость**: ${response.cost_estimate:.4f}
**Время**: {response.duration_ms}ms

---

{response.content}
"""
        return report
