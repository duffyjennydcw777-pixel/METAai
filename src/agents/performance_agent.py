"""
📊 Performance Agent — анализ производительности.
Level 3. Использует Claude Sonnet.
Ловит N+1 queries, memory leaks, async bottlenecks, неоптимальные индексы.
"""
from datetime import datetime
from .base import BaseAgent
from .config import config


class PerformanceAgent(BaseAgent):
    """Агент производительности. Находит узкие места до production."""

    def __init__(self):
        super().__init__(config.reviewer)  # Uses reviewer model config
        self.system_prompt = """You are a performance engineering specialist.
You analyze code for performance bottlenecks, memory leaks, and scalability issues.

Your analysis must cover:
1. **N+1 Queries** — Database calls inside loops
2. **Memory Leaks** — Objects that grow unbounded (dicts, lists, caches without TTL)
3. **Async Bottlenecks** — Blocking calls in async code, missing `await`, sync I/O in async context
4. **Database** — Missing indexes, full table scans, unoptimized queries, no connection pooling
5. **Caching** — Missing cache for repeated expensive operations, cache invalidation issues
6. **Concurrency** — Race conditions, deadlocks, thread-unsafe operations
7. **I/O Optimization** — Unnecessary file reads, network calls that could be batched
8. **Algorithmic** — O(n²) where O(n) is possible, unnecessary sorting/copying

Respond in Russian. Reference specific lines and provide fixed code.

Output format:
## 📊 Performance Analysis

### Критические проблемы 🔴
(each with: what, where, impact, fix)

### Оптимизации 🟡
(each with: what, estimated improvement)

### Хорошие практики ✅
(what's already done well)

### Оценка производительности
X/100 — обоснование
"""

    async def analyze(self, code: str, context: str = "") -> str:
        """Analyze code for performance issues."""
        prompt = f"""## Контекст
{context if context else "Performance анализ"}

## Код
```python
{code}
```

Проведи полный performance-анализ по чеклисту из system prompt."""

        response = await self.call(prompt)

        report = f"""# 📊 Performance Report
**Дата**: {datetime.now().strftime("%Y-%m-%d %H:%M")}
**Модель**: {response.model}
**Стоимость**: ${response.cost_estimate:.4f}

---

{response.content}
"""
        return report
