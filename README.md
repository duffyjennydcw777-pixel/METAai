# 🧠 METAai — AI Team OS for Solo Developers

> Мульти-агентная система code review и quality assurance.
> Один разработчик + 10 AI-агентов = команда уровня enterprise.

## 🚀 Статус: v1.1 LIVE

```
✅ Preflight Agent — статические проверки (secrets, .env, git status)
✅ Review Agent — AI code review через OpenRouter ($0.01/review)
⬜ Security Agent — security audit (код готов, нужна интеграция в pipeline)
⬜ Test Generator — auto-генерация тестов
⬜ Architect — design review
⬜ Remaining 5 agents
```

## ⚡ Quick Start

```bash
# 1. Клонировать
git clone [URL] && cd METAai

# 2. Зависимости
pip install httpx python-dotenv

# 3. Настройка
cp .env.example .env
# Добавить OPENROUTER_API_KEY в .env

# 4. Запуск
python review.py review --level 2 --file path/to/your/code.py
python review.py preflight --dir path/to/project
```

## 🔧 Команды

```bash
# Code review (Level 1-3)
python review.py review --level 2 --file src/handler.py
python review.py review --level 3 --last-commit
python review.py review --staged

# Preflight (pre-deploy check)
python review.py preflight --dir /path/to/project

# Pipe diff
git diff | python review.py review --stdin --level 2
```

## 📊 Code Complexity Levels (CCL)

| Level | Тип | Тесты | Примеры |
|-------|-----|-------|---------|
| 🟢 1 | Trivial | 0 | README, CSS, логирование |
| 🟡 2 | Standard | 3 | Новый endpoint, баг-фикс |
| 🔴 3 | Complex | 85%+ | Платежи, auth, миграции |

## 💰 Стоимость

| Модель | Роль | ~$/review |
|--------|------|-----------|
| Claude 3.5 Haiku | Review | $0.01 |
| Claude 3.5 Sonnet | Architect, Security | $0.03 |
| GPT-4o Mini | Test Generator | $0.005 |
| Gemini 2.0 Flash | Preflight | $0.002 |

**Типичный месяц:** 100 review × $0.01 = **$1/мес**

## 📦 Продукты

- `products/prompt-kit/` — SoloCTO Prompt Kit (правила, промпты, шаблоны)
- Будущее: SoloCTO Template, Курс, AgentForge SaaS

## 📁 Структура

```
METAai/
├── review.py              # CLI entry point
├── src/agents/
│   ├── config.py          # Модели, API keys, paths
│   ├── base.py            # OpenRouter HTTP client
│   ├── review_agent.py    # Code review agent
│   ├── preflight_agent.py # Pre-deploy checks
│   └── orchestrator.py    # Level → agents → verdict
├── products/prompt-kit/   # Первый продукт
├── .agent/rules/          # AI правила проекта
├── docs/                  # Documentation 2.0
└── DECISIONS.md           # Архитектурные решения
```

## 📝 Лицензия

Проприетарный. © 2026.
