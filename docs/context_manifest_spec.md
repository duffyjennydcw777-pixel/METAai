# Context Manifest Specification — METAai v1.0

> Универсальный стандарт для всех проектов экосистемы.
> Файл `.agent/context_manifest.yaml` должен быть в корне каждого проекта.

## Назначение

Context Manifest решает проблему **контекстной перегрузки и амнезии** AI-агентов:
- Агент получает ТОЛЬКО релевантный контекст под конкретную задачу
- Критичные файлы загружаются ВСЕГДА, независимо от задачи
- Запрещённые действия формализованы как guardrails
- Валидация обязательна перед commit/deploy

## Структура файла

```yaml
# .agent/context_manifest.yaml
# Version: 1.0 — METAai Standard

project:
  name: "<project-name>"
  type: "<type>"          # telegram-bot | saas | cli-tool | library | infra
  stage: "<stage>"        # mvp | beta | production | maintenance
  primary_language: "<lang>"
  repo_url: "<url>"       # optional

# ─── Контекст, загружаемый ВСЕГДА ───────────────────────
always_load:
  - .agent/rules/project.md
  - docs/2_ARCHITECTURE.md
  - DECISIONS.md
  - CHANGELOG.md           # последние 50 строк

# ─── Условная загрузка по типу задачи ───────────────────
load_when:
  scoring:
    - src/engine/scoring.py
    - config/decision_thresholds.example.json
    - docs/5_PRODUCT_STRATEGY.md
  database:
    - src/db/tables.py
    - alembic/
  frontend:
    - src/webapp/
    - src/bot/handlers/
  integration:
    - src/integrations/
    - .env.example
  deploy:
    - docs/4_DEPLOY_RUNBOOK.md
    - docs/3_INFRASTRUCTURE.md
    - docker-compose.yml
    - Dockerfile

# ─── Запрещённые действия (Agent Firewall) ──────────────
forbidden:
  - "Never modify production migration files without explicit approval"
  - "Never delete user data or drop tables"
  - "Never store secrets in code — .env ONLY"
  - "Never bypass pipeline (src/app/pipeline.py)"
  - "Never use create_all() in production — Alembic only"
  - "Never deploy without updating CHANGELOG.md"
  - "Never change scoring formula without updating tests"

# ─── Обязательная валидация перед commit ────────────────
validation:
  before_commit:
    - "python -m pytest tests/ -x --tb=short"
    - "Check CHANGELOG.md is updated"
  before_deploy:
    - "Verify .env is synced with .env.example"
    - "Check anti-patterns registry"
    - "Ensure git is committed"

# ─── Доменные знания (подсказки для агента) ─────────────
domain_hints:
  terminology:
    RPM: "Rate Per Mile = offered_rate / loaded_miles"
    true_RPM: "Rate Per Mile including deadhead = rate / (loaded + deadhead)"
    deadhead: "Empty miles to pickup location"
    out_miles: "Same as deadhead — Sylectus terminology"
  critical_invariants:
    - "All dates are UTC internally, convert only in UI"
    - "One external_order_id + source = one order (dedup)"
    - "Scoring must be deterministic: same input + config = same output"
```

## Правила применения

1. **Каждый проект** получает свой `.agent/context_manifest.yaml`
2. **AI-агент** обязан прочитать manifest при начале работы
3. **always_load** — грузить безусловно
4. **load_when** — грузить только если задача соответствует ключу
5. **forbidden** — жёсткие guardrails, нарушение = ошибка
6. **validation** — чеклист перед commit/deploy
7. **domain_hints** — сокращает галлюцинации по доменной терминологии
