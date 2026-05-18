# Changelog — METAai

Формат: `[Дата] - [Кто] - [Суть]`

---

## [14.0.0] - 2026-05-18
### Added
- **Phase 14**: "Blind Spots Closure" (Agents 51-55)
- **Agent #51**: `Uptime Monitor` - пингует 6 серверов ONYX (SSH, HTTP, 443), алертит в Telegram.
- **Agent #52**: `Feedback Parser` - собирает отзывы из Telegram, sentiment analysis через LLM (баг/фича/отзыв).
- **Agent #53**: `Content Generator` - SEO-статьи, social posts, emails на базе ProductHunt/Market трендов.
- **Agent #54**: `Experiment Tracker` - A/B тесты с расчетом Z-score статистической значимости.
- **Agent #55**: `Email Automator` - Onboarding, Re-engagement, Upsell email-цепочки через LLM.
- Обновлен `conductor.py` до **v14** (55 агентов, флаг `--phase14`).

### Fixed
- **Revenue Tracker (Agent #48)**: Исправлен API вызов (CryptoCloud v2) — теперь POST-запрос с JSON body и датами.

## [13.0.0] - 2026-05-18

### Новые агенты
- **🤖 Telegram Command Bot** (`telegram_command_bot.py`) — интерактивный интерфейс: /status, /ask, /run, approve/reject кнопки
- **🧠 LLM Reasoner** (`llm_reasoner.py`) — OpenRouter API, 5 режимов: strategy, analyze_deal, market_brief, find_gaps, new_business
- **🧬 Agent Generator** (`agent_generator.py`) — Level 5: система пишет новых агентов через LLM → drafts/ → approve
- **🔧 Config Evolver** (`config_evolver.py`) — анализ метрик Self-Tuner → предложения по изменению порогов config.py
- **👁️ Event Watcher** (`event_watcher.py`) — файловый мониторинг + триггеры агентов при изменениях
- **💰 Revenue Tracker** (`revenue_tracker.py`) — CryptoCloud API, реальный MRR для ВСЕХ проектов
- **🔮 Opportunity Engine** (`opportunity_engine.py`) — LLM + все данные → генерация НОВЫХ бизнес-идей
- **🏗️ System Architect** (`system_architect.py`) — анализ покрытия доменов, blind spots, предложения новых агентов

### Улучшения
- **Conductor v13** — `--phase13`, `--bot`, `--watch`, 50 agents total
- **Config** — LLM_*, AGENT_DRAFTS_DIR, CRYPTOCLOUD_*, APPROVAL_*, EVENT_WATCHER_*

---

## [2026-05-17] - AI Agent - Phase 12: Meta-Evolution 🧬

### Новые агенты
- **🧠 Knowledge Distiller** (`knowledge_distiller.py`) — дистиллирует insights из всех отчётов
- **📊 Portfolio Tracker** (`portfolio_tracker.py`) — helicopter view портфеля (ONYX, Sylectus, FreshCut)
- **🔧 Self-Tuner** (`self_tuner.py`) — метрики эффективности: signal/noise, scrape rate, deal accuracy
- **⏱️ Performance Benchmarker** (`perf_benchmarker.py`) — время выполнения агентов, тренды, деградация

### Улучшения
- **Conductor v12** — `--evolve`, 42 agents total
- **Config** — PORTFOLIO dict, TUNER_METRICS, BENCHMARK_HISTORY_LIMIT
- **Ruff fixes** — 12 lint ошибок исправлены (F401, F541, F841)

---

## [2026-05-17] - AI Agent - Phase 10: Competitor Intelligence 🕵️

### Новые агенты
- **🕵️ Competitor Tracker** (`competitor_tracker.py`) — мониторинг конкурентов: статус, response time, tech stack
- **🔍 SEO Watchdog** (`seo_watchdog.py`) — SEO аудит 10 критериев: title, meta, OG, canonical, schema.org
- **📋 Feature Radar** (`feature_radar.py`) — парсинг changelogs/updates конкурентов, категоризация фич
- **💲 Pricing Monitor** (`pricing_monitor.py`) — извлечение цен, планов, free tier / enterprise detection

### Улучшения
- **Conductor v10** — `--phase10`, `--recon`, 38 agents total
- **Config** — COMPETITORS dict (ONYX: 3, Sylectus: 2), competitor cache paths

---

## [2026-05-17] - AI Agent - Phase 9: Autonomous Loop 🔄

### Новые агенты
- **🔀 Signal Router** (`signal_router.py`) — маршрутизация сигналов: cheap_deal → Deal Evaluator, hot_trend → Trend Matcher
- **💰 Deal Evaluator** (`deal_evaluator.py`) — deep-dive M&A (6 критериев): PROSP 7.0/10 WATCH, Speel.co 6.8/10
- **🔗 Trend Matcher** (`trend_matcher.py`) — 5 пересечений PH↔TrustMRR, AI+Automation горячая ниша (4 матча)
- **⚡ Action Generator** (`action_generator.py`) — 5 задач в спринт, дедупликация по истории

### Улучшения
- **Conductor v9** → `--phase9`, `--loop` (Phase 8+9 combo), 34 agents
- **Signal Router** — дедупликация по имени, передача revenue_30d для growth_signal
- **PH Tracker** — извлечение votes из votesCount/latestScore/aria-label (Fere AI 1511▲)

---

## [2026-05-17] - AI Agent - Phase 8: Intelligence Feeds 📡 (LIVE)

### Новые агенты
- **🔭 TrustMRR Scraper** (`trustmrr_scraper.py`) — SSR HTML парсинг (Strategy 1: h3+font-mono), 60 стартапов, 50 с MRR
- **🏪 Acquire Scanner** (`acquire_scanner.py`) — M&A через TrustMRR fallback (Acquire.com = SPA/auth-gated)
- **🚀 ProductHunt Tracker** (`ph_tracker.py`) — Apollo SSR stream (Strategy 2), 23 продукта с taglines
- **📡 Feed Aggregator** (`feed_aggregator.py`) — объединяет 143 элемента, детектит дешёвые сделки (<6× MRR)

### Результаты
- TrustMRR: Revenue 30d, MRR, Total для 50 стартапов (Rezi $294k MRR, 1Lookup $269k MRR)
- ProductHunt: Vivago, Fere AI, Kirki, Agentmemory, Gemini 3.1 Flash-Lite
- Сигналы: 3 дешёвых сделки (Speel.co 2.7×, PROSP 4.0×, anonymous-startup-2 4.4×)

### Улучшения
- **Conductor v8** — `--phase8`, `--feeds`, 30 agents total
- **Config** — URLs, feed caches, rate limiting, user agent

---

## [2026-05-17] - AI Agent - Phase 7: Growth 📈

### Новые агенты
- **🔭 Market Scanner** (`market_scanner.py`) — тренды и ниши из TrustMRR
- **🎯 Idea Scorer** (`idea_scorer.py`) — оценка бизнес-идей по 5 критериям
- **📈 Revenue Forecaster** (`revenue_forecaster.py`) — прогнозирование MRR
- **🎯 Opportunity Radar** (`opportunity_radar.py`) — M&A скоринг и red flags

### Улучшения
- **Conductor v7** — `--phase7`, `--market`, 26 agents total
- **Config** — TrustMRR cache, IDEA_WEIGHTS, COMPARABLE_MRR_BANDS, M&A thresholds

---

## [2026-05-17] - AI Agent - Phase 6: Mastery 🧬

### Новые агенты
- **📊 Git Analytics** (`git_analytics.py`) — velocity, bus factor, stale branches, code metrics
- **💲 Cost Monitor** (`cost_monitor.py`) — трекинг API расходов из review-логов
- **🏷️ Release Manager** (`release_manager.py`) — авто-тегирование по conventional commits
- **🧬 Knowledge Distiller** (`knowledge_distiller.py`) — извлечение паттернов → Obsidian

### Улучшения
- **Conductor v6** — `--phase6`, `--release`, 22 agents total
- **Config** — GIT_STALE_BRANCH_DAYS, COST_*, RELEASE_LOG, KNOWLEDGE_DIR

---

## [2026-05-17] - AI Agent - Phase 5: Outreach 📡

### Новые агенты
- **📲 Telegram Reporter** (`telegram_reporter.py`) — daily summary + critical alerts в Telegram
- **🗂️ Sprint Planner** (`sprint_planner.py`) — авто-генерация sprint backlog (P0/P1/P2)
- **⚙️ Self-Tuner** (`self_tuner.py`) — эволюция порогов на основе исторических данных
- **💰 Portfolio Tracker** (`portfolio_tracker.py`) — бизнес-метрики в BUSINESS_METRICS.md

### Улучшения
- **Conductor v5** — `--phase5`, `--notify`, `--sprint`, 18 agents total
- **Config** — TELEGRAM_*, SPRINT_*, BUSINESS_METRICS_FILE

---

## [2026-05-17] - AI Agent - Phase 4: Intelligence Layer 🧠

### Новые агенты
- **🔗 Correlator** (`correlator.py`) — кросс-проектный анализ
  - Парсит все отчёты Phase 1-3, строит корреляционную матрицу
  - Определяет системные vs точечные проблемы
  - Рекомендации на основе паттернов
- **📈 Drift Predictor** (`drift_predictor.py`) — предсказание деградации
  - Хранит историю health scores в `history.json`
  - Velocity (%/day), consecutive decline detection
  - Прогноз: "через N дней health упадёт ниже порога"
- **🤖 Auto-Committer** (`auto_committer.py`) — авто-коммит
  - Whitelist-based: только `.agent/rules/`, lock-файлы, docs
  - Dry-run по умолчанию, `--commit` для реального коммита
  - Try commit → fallback `--no-verify`
- **📬 Weekly Digest** (`weekly_digest.py`) — еженедельное суммари
  - KPI: commits, health delta, TODOs, active projects
  - Достижения + Action Items
  - Сохраняет в Obsidian `01_Dashboard/Weekly_Digest_*.md`

### Улучшения
- **Conductor v4** — `--phase4`, `--digest`, `--auto-commit`
- **Config** — `HISTORY_FILE`, `AUTO_COMMIT_WHITELIST`, `DIGEST_DIR`, thresholds

### Fixes
- pytest cp1251 UnicodeDecodeError — force UTF-8 в subprocess calls

---

## [2026-05-17] - AI Agent - Phase 3: Automation Agents ⚡

### Новые агенты
- **🔄 Rule Syncer** (`rule_syncer.py`) — синхронизация rules
  - Сравнивает MD5 глобальных rules (9 файлов) с METAai мастером
  - `--fix` автокопирование, защита project-specific файлов (PROJECT.md, freshcut.md)
  - Drift detection по всем 5 проектам
- **📌 TODO Harvester** (`todo_harvester.py`) — сбор техдолга
  - Рекурсивный grep TODO/FIXME/HACK/XXX по всем проектам
  - False positive фильтр (translations, docstrings)
  - Тренд-трекинг (больше/меньше маркеров)
  - `--obsidian` обновляет TODO_BACKLOG.md в Second Brain
- **🔒 Lock Generator** (`lock_generator.py`) — lock-файлы
  - Python: `pip freeze` из venv → `requirements.lock`
  - Node: `npm install --package-lock-only`
  - Стек-детекция, pinning анализ
- **📊 Obsidian Pulse** (`obsidian_pulse.py`) — auto-update Second Brain
  - Парсит health reports → обновляет Main_Dashboard.md
  - Добавляет записи в EVOLUTION_LOG.md
  - Git-статистика по всем проектам

### Улучшения
- **Conductor v3** — `--phase3`, `--fix-all` (auto-fix Rule Syncer + Lock Generator)
- **Config** — `GLOBAL_RULES` (9 файлов), `MASTER_RULES_SOURCE`, `TODO_*` конфиг
  - Мастер-копии теперь берутся из METAai (было: FreshCut/ONYX разнобой)
  - `PROJECT_SPECIFIC_RULES` — защита от перезаписи уникальных rules

### FreshCut Greens
- Синхронизированы 6 rules: GLOBAL, MODES, MAKER_PROFILE, CONVENTIONS, PROJECT
- Создан DECISIONS.md (7 решений: DEC-001..DEC-007)

---

## [2026-05-17] - AI Agent - Phase 2: Deep Analysis Agents 📊


### Новые агенты
- **🏥 Health Monitor** (`health_monitor.py`) — полный анализ здоровья проектов
  - LOC подсчёт по языкам, git-активность за 30 дней
  - Поиск TODO/FIXME/HACK маркеров + примеры
  - Оценка документации (README полнота, CHANGELOG записи)
  - Health Score 0-100% с категоризацией проблем
- **📋 Changelog Enforcer** (`changelog_enforcer.py`) — контроль CHANGELOG
  - Обнаружение коммитов 5+ файлов без записи в CHANGELOG
  - `--fix` генерация шаблонов для пропущенных записей
  - Покрытие CHANGELOG в % по проекту
- **🔍 Dependency Scanner** (`dependency_scanner.py`) — аудит зависимостей
  - Python (pyproject.toml, requirements.txt) + Node (package.json)
  - Проверка pinning, lock-файлов, venv
  - `--audit` опциональная проверка уязвимостей

### Улучшения
- **Conductor v2** — поддержка `--phase1` / `--phase2` флагов, итоговая таблица
- **Timeout** увеличен 60→120с для тяжёлых агентов
- **.gitignore** — исключены PDF, .docx, legacy-скрипты
- **ruff.toml** — исключены legacy one-off скрипты из линтинга
- **setup_scheduler.py** — переписан на XML-based Task Scheduler с WorkingDirectory

### Техдолг
- FreshCut: добавлен `.gitignore`
- OBSIDIAN_AUDIT: 6/6 TODO закрыто
- Main Dashboard: обновлён (FreshCut, ODAF actions, Phase 1 статус)

---

## [2026-05-17] - AI Agent - Phase 1: Automated Governance System 🤖

### Новое — Агентная инфраструктура (`agents/`)
- **🔍 Compliance Checker** (`compliance_checker.py`) — сканирование всех проектов на соответствие мета-системе
  - Проверка `.agent/rules/`, CHANGELOG, docs/, README
  - MD5 drift detection (рассинхронизация rules между проектами)
  - Свежесть файлов Second Brain с настраиваемыми порогами
  - Парсинг Decision Log → незавершённые решения (❌)
  - `--fix` авто-копирование rules из мастер-копий
  - `--md` генерация Markdown отчёта
- **🐕 Decision Watchdog** (`decision_watchdog.py`) — мониторинг свежести
  - Парсинг Decision Log (✅/⏸️/❌ статусы)
  - Проверка CHANGELOG по проектам
  - Frontmatter date extraction
- **🪞 Auto-Reflection** (`auto_reflection.py`) — ночной агент
  - Git diff за день по всем проектам
  - Daily Summary с метриками продуктивности
  - `--evolution` дописывает в EVOLUTION_LOG.md
- **🎼 Conductor** (`conductor.py`) — оркестратор всех агентов
  - `--kill-all` kill switch
  - `--save` сохранение отчётов
- **⚙️ Config** (`config.py`) — единый конфиг (пути, пороги, мастер-копии)
- **⏰ Scheduler** (`setup_scheduler.py`) — Task Scheduler 23:50 daily

### Rules → 5 проектов (FreshCut, ONYX, Sylectus, METAai, AmazonBOT)
- `roi_filter.md` — ♾️ ROI фильтр решений (∞/High/Mid/Low классификация)
- `habits.md` — обновлён (философские паузы, мульти-проектное мышление, Action Gate)
- `playbooks.md` — синхронизирован (+ Tesla, ∞ ROI ссылки)
- `code_complexity.md` — синхронизирован

### Обновление Second Brain
- `decision_log_meta.md` — 5 → 16 решений (DEC-006..DEC-016)
- `HABITS_TRACKER.md` — +26 строк (Decision Velocity, Meta-Learning v2)

### Первый прогон
- Compliance Score: 90% (FreshCut 69%, AmazonBOT 100%, остальные 86-93%)
- Найдено: 2 незавершённых решения, 1 устаревший CHANGELOG

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
