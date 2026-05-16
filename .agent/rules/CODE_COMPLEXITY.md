# Code Complexity Levels — QA стратегия

> AI ОБЯЗАН классифицировать КАЖДОЕ изменение кода перед деплоем.
> Полный файл: `C:\Users\Gigabyte\Second_Brain\10_MetaEngineering\code_complexity_levels.md`

## 3 уровня

| Level | Что | Тесты | Примеры |
|-------|-----|-------|---------|
| 🟢 **1 — Trivial** | Docs, CSS, логи, комменты | Деплой без тестов | README, .gitignore, стили |
| 🟡 **2 — Standard** | Новые функции, баг-фиксы | 3 теста: happy + error + edge | Endpoint, валидация, рефактор |
| 🔴 **3 — Complex** | Платежи, auth, миграции | До 85% уверенности | Billing, crypto, DB migrations |

## Формат вывода

```
📊 Complexity: Level [1/2/3] — [Trivial/Standard/Complex]
🧪 Testing: [план тестирования]
```

## Правила

- ⚠️ Конфиги, меняющие поведение (порты, URL, feature flags) = **Level 2, не Level 1**
- При сомнениях → **выбрать высший уровень**
- Post-Mortem: баг проскочил → тип изменения повышается навсегда (CCL-XXX)
