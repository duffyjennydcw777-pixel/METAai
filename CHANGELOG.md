# Changelog — METAai

Формат: `[Дата] - [Кто] - [Суть]`

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
