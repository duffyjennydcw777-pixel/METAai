# 🤖 METAai — AI Team OS

> Multi-agent AI pipeline for solo developers. Review, Security Audit, Preflight — автоматически.

## ⚡ Quick Start

```bash
# 1. Клонировать
git clone [URL] && cd METAai

# 2. Зависимости
pip install httpx python-dotenv

# 3. Настройка
cp .env.example .env
# Добавить OPENROUTER_API_KEY в .env

# 4. Первый review
python review.py review --level 2 --file path/to/your/code.py
```

## 🔧 Команды

### Code Review (Level 1-3)
```bash
python review.py review --level 2 --file src/handler.py
python review.py review --level 3 --file src/payments.py    # Review + Preflight + Security
python review.py review --level 2 --last-commit
python review.py review --level 2 --staged
```

### Preflight Check
```bash
python review.py preflight --dir .
```

### Batch Review
```bash
python batch_review.py --level 2 --project C:\path\to\project --critical-only
python batch_review.py --level 2 --project ./myapp --max-files 15
python batch_review.py --level 3 --files auth.py payments.py
```

### Cost Tracking
```bash
python costs.py
```

### Fix Tracker
```bash
python fix_tracker.py              # Показать все баги
python fix_tracker.py --export     # Экспорт в FIXES.md
```

### Dashboard
```bash
python dashboard.py                # Генерирует dashboard.html
start dashboard.html               # Открыть в браузере (Windows)
```

## 🏗️ Architecture

```
METAai/
├── review.py              # CLI — single file review
├── batch_review.py        # CLI — batch review (multiple files)
├── costs.py               # Cost tracking
├── fix_tracker.py         # Bug aggregator
├── dashboard.py           # HTML dashboard generator
├── src/
│   └── agents/
│       ├── base.py        # Base agent (API, retry, cost tracking)
│       ├── config.py      # Model configuration
│       ├── orchestrator.py # Level-based agent pipeline
│       ├── review_agent.py # Code review
│       ├── preflight_agent.py # Deploy safety check
│       └── security_agent.py  # Security audit
├── products/
│   └── prompt-kit/        # SoloCTO Prompt Kit ($9-49)
├── deploy/
│   └── pre-push           # Git hook for auto-review
└── reviews/               # Saved reports
```

## 📊 Pipeline Levels

| Level | Agents | Time | Cost | Use Case |
|-------|--------|------|------|----------|
| **1** | None | 0s | $0 | Docs, CSS, configs |
| **2** | Reviewer | ~12s | ~$0.009 | Standard changes |
| **3** | Reviewer + Preflight + Security | ~40s | ~$0.035 | Payments, auth, crypto |

## 💰 Pricing

All models on OpenRouter (Claude 3.5 Haiku):
- **Single review**: ~$0.01
- **Batch (10 files)**: ~$0.10
- **Monthly (5 reviews/day)**: ~$1.50-3.00

## 🏆 Results

| Project | Score | Critical Bugs Found |
|---------|:-----:|:---:|
| Sylectus | 71/100 | 12 |
| ONYX | 72/100 | 8 |

## 🛠️ Products

### SoloCTO Prompt Kit
5 rule files + 25 prompts + 3 templates. Drop into any project.
See `products/prompt-kit/`

## 📄 License

MIT
