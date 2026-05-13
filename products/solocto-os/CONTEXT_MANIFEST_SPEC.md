# Context Manifest Specification v1.0

> Universal standard for AI-native projects.
> File `.agent/context_manifest.yaml` goes in the root of every project.

## Purpose

Context Manifest solves **context overload and amnesia** in AI agents:
- Agent receives ONLY relevant context for the specific task
- Critical files are loaded ALWAYS, regardless of task type
- Forbidden actions are formalized as guardrails
- Validation is mandatory before commit/deploy

## File Structure

```yaml
# .agent/context_manifest.yaml
# Version: 1.0 — Solo CTO OS Standard

project:
  name: "<project-name>"
  type: "<type>"          # telegram-bot | saas | cli-tool | library | infra
  stage: "<stage>"        # mvp | beta | production | maintenance
  primary_language: "<lang>"
  repo_url: "<url>"       # optional

# ─── Context loaded ALWAYS ───────────────────────
always_load:
  - .agent/rules/project.md
  - docs/2_ARCHITECTURE.md
  - DECISIONS.md
  - CHANGELOG.md           # last 50 lines

# ─── Conditional loading by task type ───────────────────
load_when:
  database:
    - src/db/models.py
    - alembic/
  frontend:
    - src/webapp/
    - src/components/
  api:
    - src/api/
    - docs/api_reference.md
  deploy:
    - docs/4_DEPLOY_RUNBOOK.md
    - docs/3_INFRASTRUCTURE.md
    - docker-compose.yml
    - Dockerfile
  payments:
    - src/payments/
    - .env.example

# ─── Forbidden actions (Agent Firewall) ──────────────
forbidden:
  - "Never modify production migration files without explicit approval"
  - "Never delete user data or drop tables"
  - "Never store secrets in code — .env ONLY"
  - "Never use create_all() in production — Alembic only"
  - "Never deploy without updating CHANGELOG.md"
  - "Never skip Code Complexity Level assessment"

# ─── Mandatory validation before commit ────────────────
validation:
  before_commit:
    - "Run tests: pytest tests/ -x --tb=short"
    - "Check CHANGELOG.md is updated"
    - "Check DECISIONS.md if architecture changed"
  before_deploy:
    - "Verify .env is synced with .env.example"
    - "Check anti-patterns registry"
    - "Ensure git is committed"
    - "Verify rollback plan exists"

# ─── Domain knowledge (hints for the agent) ─────────────
domain_hints:
  terminology:
    MRR: "Monthly Recurring Revenue"
    CCL: "Code Complexity Level (1=Trivial, 2=Standard, 3=Complex)"
    ADR: "Architecture Decision Record"
  critical_invariants:
    - "All dates are UTC internally, convert only in UI"
    - "Secrets go in .env, never in code"
```

## Rules

1. **Every project** gets its own `.agent/context_manifest.yaml`
2. **AI agent** must read the manifest at the start of work
3. **always_load** — load unconditionally
4. **load_when** — load only if task matches the key
5. **forbidden** — hard guardrails, violation = error
6. **validation** — checklist before commit/deploy
7. **domain_hints** — reduces hallucinations on domain terminology

## How to Create Your Own

1. Copy this template to `.agent/context_manifest.yaml`
2. Fill in `project` section
3. List your critical files in `always_load`
4. Group files by task type in `load_when`
5. Add YOUR project's forbidden actions
6. Add YOUR domain terminology

The manifest grows with your project. Start simple, add as you learn.
