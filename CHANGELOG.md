# Changelog — METAai

Формат: `[Дата] - [Кто] - [Суть]`

---

## [2026-05-13] - AI Agent - v2.1: Meta-Engineering OS — Системный Синтез 🧠

### Новые подсистемы

- **MODES.md** — 9 формализованных режимов мышления (Разведка, Штаб, Архитектор, Кузница, Клиника, Детектив, Шахматы, Запуск, Торговец). Каждый режим = промпт + формат ответа + scope. Размещён в `.agent/rules/`.
- **Detective-First Protocol** — правило в GLOBAL.md: при баге СНАЧАЛА режим Детектив (факты → гипотезы → проверка → минимальный фикс → регрессия). Запрещено переписывать код без гипотезы.
- **Клиника** — формализованный протокол диагностики системных проблем (симптомы → причины → срочное/плановое лечение).
- **REFLEXION_LOG.md** — лог стратегических решений, которые не сработали (3 начальных записи: checkout, free-подписки, scoring без feedback). Уровень выше Anti-Pattern Registry.
- **EXPERIMENTS.md** — A/B testing framework (гипотеза → варианты → метрика → длительность → результат). 3 начальных эксперимента: GO-alert формат, trial длительность, ценообразование.

### Chess Mode (Conductor Playbook)
- Добавлен `/chess` — стратегический прогон: позиция → сильные фигуры → слабые поля → блундеры → лучший ход
- Шахматные фазы: дебют (MVP) → миттельшпиль (удержание) → эндшпиль (масштабирование)

### GLOBAL.md v2 — расширение конституции
- Добавлено правило #4: MODES.md обязателен, режим указывается в каждом ответе
- Добавлено правило #5: REFLEXION_LOG.md при стратегических решениях
- Добавлена секция «Протокол расследования» (#16-18)
- Добавлена секция «Эксперименты» (#19-20)
- Добавлено правило Feedback Loop: scoring без обратной связи = гадание

### Deploy Script v2 (`deploy_rules_everywhere.py`)
- Обновлён список проектов: 12 проектов из `C:\Dev` (было 4 из HOME)
- Добавлено распространение: MODES.md, REFLEXION_LOG.md, EXPERIMENTS.md
- MODES.md читается из master copy (METAai) и деплоится во все проекты

### Sylectus: alert_feedback спецификация
- SQL: таблица `alert_feedback` (user_feedback: useful/not_useful/booked/ignored/spam)
- Telegram: inline-кнопки 👍/👎/📞/⏭ после каждого GO-alert
- Метрики: precision/recall queries
- Target: precision > 75%

### Источник
- 80KB сессия Meta-Engineering OS (Claude) проанализирована и синтезирована с нашей production-системой
- 17/17 концепций уже были реализованы, 7 ценных дополнений интегрированы

---


### Payment Service v2
- **Unified service** — delivery_bot объединён с payment_service, один процесс
- **Auto-delivery** — webhook получает оплату → ZIP автоматически отправляется в TG админу для пересылки
- **Идемпотентность** — `processed_orders.json` предотвращает повторную обработку webhook'ов
- **`secrets.token_hex(8)`** — замена `os.urandom(4)` для генерации order_id
- **Per-invoice webhook URL** — `url_callback` передаётся в каждом API-вызове (dashboard CryptoCloud read-only)
- **Success/Fail redirect** — `url_success` / `url_return` в payload инвойса

### Инфраструктура
- **HTTPS через nginx proxy** — `location /pay/` → `:8002` на `ironyx.tech`, mixed content решён
- **URL миграция** — `http://92.246.137.35:8002/api/v1/` → `https://api.ironyx.tech/pay/`
- **systemd v2** — обновлён unit файл, auto-restart
- **ZIP на сервере** — `solocto-os-pro-v1.0.zip` рядом с `main.py` для auto-delivery

### Лендинг
- **Кнопки Buy** — HTTPS URL вместо HTTP (mixed content fix)
- **success.html** — обновлён текст (убрано "check email", добавлен реальный flow)
- **Pushed** — GitHub Pages обновлён

### Ожидание
- ⏳ CryptoCloud production mode (заявка на рассмотрении)

---

## [2026-05-07] - AI Agent - v1.9: Payment Service Hardening 🔒

### Безопасность
- **Секреты вынесены из кода** — API_KEY, TG_BOT_TOKEN из `main.py` → `.env`
- **python-dotenv** — загрузка конфигурации с fallback (local `.env` → project `.env`)
- **CORS middleware** — разрешены только GitHub Pages и localhost

### Инфраструктура
- **Порт 8001 → 8002** — 8001 занят Sylectus webapp, payment service переехал на 8002
- **UFW firewall** — открыт порт 8002/tcp (был закрыт!)
- **Python venv** — Debian 12 PEP 668, создан `/root/payment_service/venv/`
- **systemd** — `payment-service.service` (auto-restart, выживает ребут)
- **start.sh** — обход PowerShell `>` redirect перехвата (PS-006)

### Кнопка Buy Now
- **Починена!** Причины поломки: (1) порт 8001 занят Sylectus, (2) порт 8002 закрыт файрволлом
- **CryptoCloud checkout** — инвойс создаётся, страница оплаты открывается ✅
- **Тестовый режим** — заявка на production отправлена (ожидание до 24ч)

### Anti-Patterns
- **PS-006** добавлен: PowerShell перехватывает `>` / `>>` в SSH-командах

---

## [2026-05-05] - AI Agent - v1.8: Solo CTO OS — LAUNCHED 🚀

### Монетизация
- **Продукт**: Solo CTO OS Pro — $149 (launch) / $249 (full)
- **Лэндинг**: https://duffyjennydcw777-pixel.github.io/solocto-os/ (live)
- **Оплата**: USDT TRC-20 → `TE18CRGjhC5Woag4gKjH8VUTDaN7iDxr4W`
- **Поддержка**: Telegram `@IrattaRazma`
- **ZIP**: `products/dist/solocto-os-pro-v1.0.zip` (97 KB, 60+ файлов)

### Контент пакета (4 слоя)
- **Layer 1**: AI Rules (5 правил, 25 промптов, 6 шаблонов)
- **Layer 2**: Multi-Agent Pipeline (10 агентов, 6 аналитических модулей)
- **Layer 3**: Meta-Engineering (Anti-Patterns Registry, Context Manifest Spec)
- **Layer 4**: Second Brain Vault (8 папок, Dashboard, VISION, Business, Life OS)

### Инфраструктура
- **`products/solocto-os/`** — полный generic vault template
- **`products/build_full_package.py`** — build script v2 (полный пакет)
- **`products/landing/`** — лэндинг (HTML+CSS, dark premium theme)
- **`github.com/duffyjennydcw777-pixel/solocto-os`** — публичный репо лэндинга

---

## [2026-05-05] - AI Agent - v1.7: Packaging + Docs + Session State

### Монетизация
- **`products/build_package.py`** — скрипт сборки ZIP-архивов для Gumroad
  - 3 тира: Starter ($9), Pro ($19), Team ($49)
  - Генерирует MANIFEST.txt и TEAM_SETUP.md (для Team тира)
  - Output: `products/dist/*.zip`

### Документация
- **`docs/1_PRODUCT.md`** — заполнен реальными данными (продукты, аудитория, метрики, roadmap)
- **`docs/2_ARCHITECTURE.md`** — заполнен (стек, структура кода, ADR, диаграммы pipeline)
- **`session_state.md`** — создан в scratch-директории (контекст между сессиями)

### Следующий шаг
- Запустить `python products/build_package.py` → загрузить dist/*.zip на Gumroad

---

## [2026-05-03] - AI Agent - v1.6: Context Manifest & ADR AI Instructions

### Мета-инженерия
- **Context Manifest Spec v1.0** (`docs/context_manifest_spec.md`) — универсальный стандарт `.agent/context_manifest.yaml`
  - Маршрутизация контекста: `always_load` + `load_when` (по типу задачи)
  - Agent Firewall: `forbidden` секция с жёсткими guardrails
  - Domain Hints: терминология и инварианты для снижения галлюцинаций
  - Обязательная валидация: `before_commit` + `before_deploy` чеклисты
- **Первое внедрение**: Sylectus `.agent/context_manifest.yaml` (8 типов задач, 10 guardrails)
- **ADR + AI Instructions**: все 6 DEC в Sylectus DECISIONS.md получили секцию `AI Instructions`
- **DEC-007**: Context Manifest добавлен как архитектурное решение в Sylectus
- **Knowledge Items**: паттерны #9 (Context Manifest) и #10 (ADR AI Instructions) добавлены в `project-management-patterns`
- **GEMINI.md**: Sylectus agent routing обновлён — manifest читается первым (шаг 0)

### Анализ стратегического документа
- Глубокий анализ `AI_native_products_Telegram_Sylectus_full_chat.docx` (840 параграфов)
- Извлечены: True RPM формула, scoring engine spec, тарифная сетка, GTM-стратегия, продажный скрипт
- Action Items матрица: 13 задач с приоритетами и effort-оценкой

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
