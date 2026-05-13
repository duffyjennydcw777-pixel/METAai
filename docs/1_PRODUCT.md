# 📦 METAai — Продукт

## Что это?

**METAai** — solo-developer framework для AI-powered разработки.

Два продукта под одним зонтиком:

1. **Multi-Agent Code Review Pipeline** — CLI-инструмент, который прогоняет код через 10 AI-агентов (Review, Security, Architect, Perf, Docs, Business, i18n, TestGen, Refactor, Preflight) через OpenRouter API. Стоимость: ~$15-30/мес за всю армию.

2. **SoloCTO Prompt Kit** — готовый пакет правил, промптов и шаблонов для продажи ($9/$19/$49). Plug-and-play система для соло-разработчиков, которые работают с AI (Cursor, Copilot, Claude, Gemini).

---

## Для кого?

| Сегмент | Боль | Решение |
|---------|------|---------|
| Solo-разработчик с AI | AI даёт generic ответы, не знает проект | Prompt Kit — 5 min setup, AI знает правила |
| Небольшие команды (2-5) | Нет стандартов, каждый пишет по-своему | Team тир Prompt Kit |
| Tech lead | Нет time делать code review вручную | Multi-Agent Pipeline |
| Автоматизатор | Рутинные проверки перед деплоем | Preflight + CI/CD интеграция |

---

## Ключевые фичи

### Multi-Agent Pipeline
1. **10 агентов** с разными ролями и моделями (Sonnet / Haiku / GPT-4o-mini / Flash)
2. **Scientific analytics** — Shannon entropy, Pareto hot files, Bayesian bug predictor, Kolmogorov NCD
3. **CLI** — `python review.py review/fix/test-gen/architect/perf/docs/business/ux`
4. **Dashboard** — HTML с историей review'ов, cost tracking, score по проектам
5. **GitHub Actions** — auto-review при PR, complexity detection

### Prompt Kit (продукт на продажу)
1. **5 Rules Files** — GLOBAL, PROJECT, CODE_COMPLEXITY, CONVENTIONS, MAKER_PROFILE
2. **25 Battle-Tested Prompts** — Arch, Review, Test, Deploy, Refactor, Security, Docs
3. **6 Templates** — DECISIONS, SOLUTION_PATTERNS, CHANGELOG, 3 doc templates
4. **Setup script** — `python setup.py /your/project` → 13 файлов за 5 секунд
5. **3 тира** — Starter ($9), Pro ($19), Team ($49)

---

## Конкурентные преимущества

- **Runs on your AI** — никаких новых инструментов, работает в Cursor/VS Code/любом редакторе
- **Language-agnostic** — Python, JS/TS, Go, Rust — неважно
- **Self-improving** — Decision Log + Solution Patterns компаундируются со временем
- **Scientific QA** — не просто "AI посмотрел", а entropy/pareto/bayes метрики
- **Battle-tested** — проверено на реальных проектах (Sylectus, ONYX, AmazonBOT)

---

## Метрики успеха

| Метрика | Цель (3 мес) | Текущее |
|---------|:------------:|:-------:|
| MRR Prompt Kit | $500 | $0 |
| Продажи Prompt Kit | 30 шт | 0 |
| Pipeline API Cost | < $30/мес | ~$12/мес |
| Bugs caught (pipeline) | — | 56+ |
| Tests generated | — | 25+ |

---

## Roadmap

### ✅ v1.0-v1.6 (done)
- Multi-Agent system (10 агентов)
- Scientific analytics
- Prompt Kit v1.0 (25 промптов)
- GitHub Actions CI
- Context Manifest Spec

### 🔜 v2.0 (next)
- Prompt Kit v2.0 (+ Context Manifest + ADR AI Instructions)
- Gumroad публикация
- Telegram Bot-версия pipeline (SaaS)
- Страница-лэндинг для Prompt Kit
