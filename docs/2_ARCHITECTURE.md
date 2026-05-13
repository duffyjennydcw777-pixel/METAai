# 🏗️ METAai — Архитектура

## Технический стек

| Слой | Технология | Версия | Обоснование |
|------|-----------|--------|-------------|
| Runtime | Python | 3.10+ | Async, типизация, богатая экосистема |
| HTTP Client | httpx + asyncio | 0.27+ | Async-first, retry logic, streaming |
| AI API | OpenRouter | v1 | Multi-model, единый API для всех моделей |
| Config | python-dotenv | 1.0+ | Стандарт, .env изоляция |
| CLI | argparse (stdlib) | — | Без зависимостей, достаточно для CLI |
| Analytics | stdlib (math, zlib) | — | Shannon/Kolmogorov без внешних зависимостей |
| Dashboard | Python → HTML | — | Генерация статичного HTML, dark theme |
| CI/CD | GitHub Actions | — | Auto-review при PR |

---

## Структура кода

```
METAai/
├── src/
│   └── agents/                  # 10 AI-агентов
│       ├── base.py              # BaseAgent: httpx, retry, cost tracking
│       ├── config.py            # Модели, цены, OpenRouter settings
│       ├── orchestrator.py      # Диспетчер: Level → агенты → вердикт
│       ├── review_agent.py      # Code Review (Claude Haiku 3.5)
│       ├── security_agent.py    # Security Audit (Claude Sonnet)
│       ├── architect_agent.py   # Architecture Analysis (Claude Sonnet)
│       ├── preflight_agent.py   # Pre-deploy checks (Gemini Flash)
│       ├── test_gen_agent.py    # Test Generation (GPT-4o-mini)
│       ├── refactor_agent.py    # Refactor suggestions (Claude Haiku)
│       ├── performance_agent.py # Performance Analysis (Claude Haiku)
│       ├── docs_agent.py        # Documentation generation
│       ├── business_agent.py    # Business Logic audit
│       └── ux_agent.py          # UX/i18n check
│
├── review.py                    # CLI entry point (12 команд)
├── batch_review.py              # Батч-прогон нескольких файлов
├── entropy.py                   # Shannon Entropy Analyzer
├── impact.py                    # Impact Graph (blast radius)
├── pareto.py                    # Pareto Hot Files (80/20)
├── bayes.py                     # Bayesian Bug Predictor
├── kolmogorov.py                # NCD duplicate detector
├── review_history.py            # Information Gain dedup
├── dashboard.py                 # HTML Dashboard generator
├── costs.py                     # Cost Tracker
├── fix_tracker.py               # Bug aggregator → FIXES.md
├── watch.py                     # File watcher (auto-review on save)
│
├── products/
│   ├── build_package.py         # ZIP packaging для Gumroad
│   └── prompt-kit/              # SoloCTO Prompt Kit (продаётся)
│       ├── rules/               # 5 rule files
│       ├── templates/           # 3 project templates
│       ├── docs/                # 3 doc templates
│       ├── PROMPT_LIBRARY.md    # 25 промптов
│       ├── GUMROAD_PAGE.md      # Текст для страницы продажи
│       ├── setup.py             # Install script для покупателя
│       └── README.md
│
├── docs/                        # Documentation 2.0
│   ├── 1_PRODUCT.md
│   ├── 2_ARCHITECTURE.md        # этот файл
│   ├── 3_INFRASTRUCTURE.md
│   └── 4_DEPLOY_RUNBOOK.md
│
├── .agent/
│   ├── rules/                   # AI agent rules (5 файлов)
│   └── context_manifest.yaml    # TODO: создать
│
├── reviews/                     # Сохранённые review-отчёты
├── generated_fixes/             # Авто-сгенерированные фиксы
├── generated_tests/             # Авто-сгенерированные тесты
└── deploy/                      # CI/CD: pre-push hook, GitHub Actions
```

---

## Architecture Decision Records (ADR)

### ADR-001: Стандартная проектная структура
- **Дата**: 2026-04-26
- **Решение**: Использовать `.agent/rules/` + Documentation 2.0
- **Почему**: Единообразие с ONYX, Sylectus. Проверено в бою.

### ADR-002: Raw OpenRouter API вместо фреймворков
- **Дата**: 2026-04-28
- **Решение**: httpx + asyncio, без CrewAI/LangGraph
- **Почему**: Запускается за 30 минут, 0 фреймворк-зависимостей, полный контроль над retry/cost.
- **Пересмотреть**: При необходимости stateful графа (> 5 агентов с памятью)

### ADR-003: Разные модели для разных агентов
- **Дата**: 2026-04-28
- **Решение**: Sonnet (Architect/Security), Haiku (Review/Refactor/Perf), GPT-4o-mini (TestGen), Flash (Preflight)
- **Почему**: $15-30/мес за 10 агентов. Дешёвые модели справляются с рутиной.

### ADR-004: Prompt Kit как отдельный продукт
- **Дата**: 2026-04-28
- **Решение**: Вынести rules + промпты в `products/prompt-kit/` и продавать через Gumroad
- **Почему**: Zero additional cost, монетизация существующих артефактов

---

## Диаграмма: Multi-Agent Pipeline

```
                    review.py (CLI)
                         │
                    orchestrator.py
                    /     |      \
              Level 1  Level 2  Level 3
                 │        │        │
            Preflight  Review  Review
                       Security Security
                                Architect
                                TestGen
                                Refactor
                         │
                    Markdown Report
                    HTML Dashboard
                    FIXES.md
```

---

## Диаграмма: Prompt Kit Distribution

```
prompt-kit/          →  build_package.py  →  dist/
  rules/ (5)                                  starter.zip ($9)
  templates/ (3)                              pro.zip     ($19)
  docs/ (3)                                   team.zip    ($49)
  PROMPT_LIBRARY.md                                │
  setup.py                                   Gumroad
                                             покупатель запускает setup.py
```
