# 📐 CONVENTIONS — Конвенции METAai

> Единый источник правды по стилю кода, файловой структуре и процессам.

---

## 📁 Структура проекта

```
METAai/
├── .agent/
│   ├── rules/          # Правила AI-агента
│   │   ├── GLOBAL.md       # Глобальные правила (все проекты)
│   │   ├── PROJECT.md      # Проектные правила (METAai)
│   │   ├── CONVENTIONS.md  # Этот файл
│   │   └── MAKER_PROFILE.md # Профиль создателя
│   └── scripts/        # Утилиты агента (чеклисты и т.д.)
├── docs/               # Documentation 2.0
│   ├── 1_PRODUCT.md
│   ├── 2_ARCHITECTURE.md
│   ├── 3_INFRASTRUCTURE.md
│   └── 4_DEPLOY_RUNBOOK.md
├── src/                # Исходный код
├── tests/              # Тесты
├── deploy/             # Скрипты деплоя
├── .env.example        # Шаблон переменных окружения
├── CHANGELOG.md        # Журнал изменений
└── README.md           # Точка входа документации
```

---

## 📝 Коммиты (Conventional Commits)

```
feat: добавить авторизацию через Telegram
fix: исправить утечку сессий в polling цикле
refactor: вынести crypto в отдельный модуль
docs: обновить ARCHITECTURE.md с ADR-005
chore: обновить зависимости
perf: оптимизировать N+1 запрос нотификаций
security: убрать хардкод токена из api.py
```

---

## 🔤 Именование

| Контекст | Стиль | Пример |
|----------|-------|--------|
| Python переменные/функции | snake_case | `get_user_by_id` |
| Python классы | PascalCase | `UserService` |
| Python константы | UPPER_SNAKE | `MAX_RETRY_COUNT` |
| JS/TS переменные/функции | camelCase | `getUserById` |
| JS/TS компоненты | PascalCase | `UserProfile` |
| CSS классы | kebab-case | `user-profile-card` |
| Файлы Python | snake_case | `user_service.py` |
| Файлы JS/TS | camelCase / PascalCase (компоненты) | `userService.ts` |
| Env переменные | UPPER_SNAKE | `DATABASE_URL` |
| API endpoints | kebab-case | `/api/user-profile` |

---

## 📄 Файлы

- **Максимум строк**: 300 для модулей, 500 для основных файлов. Больше → рефакторить.
- **Один модуль = одна ответственность** (SRP).
- **Нет дублирования**: Если логика используется >2 раз → вынести в утилиту.

---

## 🧪 Тесты

- Тесты рядом с кодом: `tests/test_<module>.py`
- Fixture-based (pytest)
- Минимум: happy path + 1 edge case + 1 error case
- Моки только для внешних сервисов (Telegram, X-UI, etc.)

---

## 🔐 Переменные окружения

- **Формат**: `.env` для локальной разработки, `.env.production` на сервере
- **Шаблон**: `.env.example` — ВСЕГДА актуален, БЕЗ реальных значений
- **Доступ**: через `python-dotenv` или `pydantic-settings`
- **НИКОГДА**: не коммитить `.env` в Git

---

## 💡 Code Review Checklist (для AI)

При каждом изменении файла проверить:
1. [ ] Не сломан ли существующий функционал?
2. [ ] Нет ли дублирования кода?
3. [ ] Правильное именование?
4. [ ] Обработка ошибок (try/except с конкретными исключениями)?
5. [ ] Нет ли хардкода (магические числа, строки)?
6. [ ] Логирование добавлено для значимых операций?
