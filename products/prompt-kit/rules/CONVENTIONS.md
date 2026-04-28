# 🎨 Code Conventions

> Единый стиль кода для проекта. AI следует этим правилам при генерации кода.

---

## Язык и стиль

| Правило | Значение |
|---------|----------|
| **Язык комментариев** | `[Русский / English]` |
| **Язык переменных** | English |
| **Стиль именования** | `snake_case` (Python) / `camelCase` (JS/TS) |
| **Максимальная длина строки** | 120 символов |
| **Отступы** | 4 пробела (Python) / 2 пробела (JS/TS/YAML) |

## Файлы

- Один файл = одна ответственность (SRP)
- Максимум 300 строк на файл (рекомендация)
- Группировка imports: stdlib → third-party → local

## Функции

- Максимум 30 строк на функцию
- Docstring для каждой публичной функции
- Type hints обязательны (Python 3.10+)
- Return early pattern (guard clauses)

```python
# ✅ Хорошо
def process_order(order: Order) -> Result:
    """Process an incoming order."""
    if not order.is_valid():
        return Result.error("Invalid order")
    
    if order.is_duplicate():
        return Result.skip("Duplicate")
    
    return Result.ok(order.execute())

# ❌ Плохо
def process_order(order):
    if order.is_valid():
        if not order.is_duplicate():
            return order.execute()
        else:
            return "Duplicate"
    else:
        return "Invalid"
```

## Обработка ошибок

- Конкретные исключения, не `except Exception`
- Логирование ошибок с контекстом
- User-facing сообщения на языке пользователя

## Git

- Commit message: `[тип]: описание` (feat, fix, refactor, docs, chore)
- Один commit = одна логическая единица
- Не коммитить `.env`, `__pycache__/`, `node_modules/`
