# Changelog — METAai

Формат: `[Дата] - [Кто] - [Суть]`

---

## [2026-04-29] - AI Agent - v1.5: 10-Agent Complete + Scientific Analytics

### Новые агенты (5→10)
- **🏗️ Architect Agent** — архитектурный анализ, проектирование интерфейсов
- **📊 Performance Agent** — N+1 queries, memory leaks, async bottlenecks
- **📝 Documentation Agent** — auto-docstrings, README генерация, coverage check
- **💰 Business Logic Agent** — аудит подписок, платежей, прав доступа
- **🌍 i18n/UX Agent** — проверка текстов, опечаток, UX-копирайтинга

### Научная аналитика (Shannon/Pareto/Bayes/Kolmogorov)
- **📐 Shannon Entropy Analyzer** — информационная энтропия кода → auto Level routing
- **🕸️ Impact Graph** — граф зависимостей, blast radius при изменениях
- **🎯 Pareto Hot Files** — 80/20 правило, отслеживание проблемных файлов
- **🧠 Bayesian Bug Predictor** — P(bug) на основе истории review
- **🧬 Kolmogorov NCD** — поиск дубликатов через compression distance
- **🧾 Review History** — Information Gain dedup, не ревьюить неизменённые файлы

### CLI команды (12 total)
- `review`, `preflight`, `test-gen`, `fix` (v1.3)
- `entropy`, `impact`, `pareto`, `dupes` (v1.4)  
- `architect`, `perf`, `docs`, `business`, `ux` (v1.5)

---

## [2026-04-28] - AI Agent - v1.3: Test Generator + Refactor Agent

### Новое
- **🧪 Test Generator Agent** (`test_gen_agent.py`) — 4-й агент, auto-генерация pytest тестов
  - CLI: `python review.py test-gen --file path/to/code.py`
  - Сгенерировано 25 тестов для Sylectus subscription + ONYX payments
  - AsyncMock, pytest.mark.asyncio, parametrize — enterprise grade
- **🔧 Refactor Agent** (`refactor_agent.py`) — 5-й агент, генерация конкретных фиксов
  - CLI: `python review.py fix --review reviews/report.md`
  - Auto mode: `python review.py fix` (берёт последний отчёт)
  - Точечный фикс: `python review.py fix --file code.py --issue "описание"`
- **🔄 GitHub Actions** (`.github/workflows/review.yml`) — auto-review при PR
  - Авто-определение complexity level (payment/auth = Level 3)
  - Постинг результата как комментарий к PR

### Исправлено
- **Watch mode** — чистый выход по Ctrl+C (без traceback)
- **TestGenAgent** — fix `response.content` вместо `response`, fix `logger.info` вместо `self.log`

### Статистика за сессию
- 56 багов найдено (51 critical) → 5 проектов
- 25 тестов сгенерировано → 3 файла
- $0.12 потрачено → 14 коммитов → GitHub public repo

---

## [2026-04-28] - AI Agent - v1.2: Full Pipeline + Dashboard

### Новое
- **🛡️ Security Agent** — третий агент, аудит безопасности кода
  - Находит SQL injection, secrets, auth bypass, payload tampering
  - Протестирован: ONYX payments 45/100, Sylectus handlers 45/100
- **🔄 Batch Review** (`batch_review.py`) — прогон нескольких файлов одной командой
  - `--critical-only` — автофильтр по payment/auth/crypto/handler файлам
  - `--max-files` — лимит количества файлов
  - Автосохранение отчёта + рейтинг файлов по баллам
- **💰 Cost Tracker** (`costs.py`) — подсчёт затрат по review-логам
  - Breakdown по дням, средняя стоимость, прогноз на месяц
- **🐛 Fix Tracker** (`fix_tracker.py`) — агрегатор всех найденных багов
  - Парсит все review-отчёты, экспорт в `FIXES.md`
  - 47 багов найдено (28 critical, 5 high)
- **📊 HTML Dashboard** (`dashboard.py`) — визуальная сводка
  - Dark theme, метрики, рейтинг проектов, история review'ов
- **🪝 Git Pre-Push Hook** (`deploy/pre-push`) — auto-review при push
- **🔁 Retry Logic** — auto-retry при 429 (5s → 10s → 15s)

### Исправлено
- **Model IDs** — все агенты на `anthropic/claude-3.5-haiku` (стабильно)
- **Project naming** — review'ы подписываются реальным именем проекта (не CWD)
- **Preflight format** — Preflight отчёт теперь readable markdown, не raw JSON

### Результаты Batch Review
| Проект | Score | Файлов | Worst |
|--------|:-----:|:------:|-------|
| Sylectus | 71/100 | 7 | bootstrap_deploy_secret.py (30!) |
| ONYX | 72/100 | 5 | payments.py (65) |

### Бюджет
- Потрачено за сессию: $0.084
- Прогноз: $2.51/мес при 8 reviews/день

---

## [2026-04-28] - AI Agent - v1.1: Live Agents + Prompt Kit

### Исправлено
- **Model IDs** — исправлены на рабочие OpenRouter ID (точки вместо дефисов)
- **Error handling** — base.py теперь показывает тело ошибки от API, а не голой 404
- **Config defaults** — pricing dict синхронизирован с model IDs

### Новое
- **🎉 ПЕРВЫЙ ЖИВОЙ REVIEW!** — `review.py review --level 2 --file handlers.py`
  - Результат: 3 critical + 4 warning за $0.01, 12 секунд
  - Найдены реальные баги в Sylectus (null checks, auth bypass, secret leak)
- **Prompt Kit v1.0** (`products/prompt-kit/`) — первый продукт, готов к продаже
  - 5 правил (GLOBAL, PROJECT, CODE_COMPLEXITY, CONVENTIONS, MAKER_PROFILE)
  - 25 промптов (Arch, Review, Test, Deploy, Refactor, Security)
  - 3 шаблона (DECISIONS, SOLUTION_PATTERNS, CHANGELOG)
  - 3 doc templates (Product, Architecture, Deployment)
  - README + Quick Start

### Obsidian Big Bang
- 3 MOC-хаба (Projects, Business, Meta)
- METAAI.md в 03_Projects
- Dashboard: +METAai, +FamilyQuest, +Co-Evolution items
- VISION.md заполнен (12 вопросов → North Star)
- EVOLUTION_LOG обновлён (Session 12)
- 8+ мостов между кластерами, orphan-фиксы
- 6 цветовых групп в Graph View

---

## [2026-04-28] - AI Agent - Multi-Agent System v1.0

### Новое
- **Code Complexity Levels** (`CODE_COMPLEXITY.md`) — 3 уровня классификации кода (Trivial/Standard/Complex)
  - Распространено на все проекты: METAai, ONYX, Sylectus
  - Создан Knowledge Item для persistence между сессиями
- **Агентная система** (`src/agents/`) — 5 ролей AI-агентов через OpenRouter API
  - `config.py` — конфигурация моделей и API
  - `base.py` — базовый класс с подсчётом стоимости
  - `review_agent.py` — code review с структурированным отчётом
  - `preflight_agent.py` — pre-deploy проверки (.env, secrets, git)
  - `orchestrator.py` — диспетчер: Level → агенты → вердикт
- **CLI** (`review.py`) — точка входа: `python review.py review --level 3`
- **DECISIONS.md** — журнал архитектурных решений (METAai, ONYX, Sylectus)
- **SOLUTION_PATTERNS.md** — библиотека проверенных решений (6 стартовых паттернов)
- **Post-Mortem Protocol** (CCL-XXX) — автоматическое повышение уровня при проскочивших багах

### Стратегия
- Стоимость агентов: $15-30/мес (оптимум), до $90 (максимум)
- Второй компьютер НЕ нужен — всё через API
- Roadmap: Raw API → CrewAI → Zero-Guess Auto-Pipeline



## [2026-04-26] - AI Agent - CI/CD для всех проектов

- GitHub Actions workflows для 3 проектов (Sylectus, AmazonBOT, ONYX)
- Sylectus: test.yml (pytest + ruff) + deploy.yml (backup → SCP → restart → health check → rollback → TG notify)
- AmazonBOT: test.yml (ruff + mypy + pytest + coverage), deploy закомментирован (сервер TBD)
- ONYX: test.yml (backend pytest + lint + frontend build) + deploy.yml (полный pipeline)
- Setup скрипт `deploy/setup_cicd.ps1` (SSH ключи + git remotes)
- Обновлён ONYX `.gitignore` (добавлены .venv, .pytest_cache, *.db)

## [2026-04-26] - AI Agent - Инициализация проекта

- Создана структура `.agent/rules/` (GLOBAL, PROJECT, CONVENTIONS, MAKER_PROFILE)
- Создан README.md, CHANGELOG.md
- Создана структура docs/ (Documentation 2.0)
- Проект готов к определению продукта и стека
