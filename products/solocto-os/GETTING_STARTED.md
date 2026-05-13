# 🚀 Getting Started — Solo CTO OS

> From zero to a fully working AI-powered development system in under 1 hour.

---

## What's Inside This Package

```
solocto-os/
├── agent-rules/              # AI project rules (Layer 1)
│   ├── rules/                # 5 rule files for .agent/rules/
│   ├── templates/            # DECISIONS.md, SOLUTION_PATTERNS.md, CHANGELOG.md
│   ├── docs/                 # Documentation 2.0 templates
│   ├── PROMPT_LIBRARY.md     # 25 battle-tested prompts
│   └── setup.py              # Auto-installer
│
├── agent-pipeline/           # Multi-Agent Code Review (Layer 2)
│   ├── src/agents/           # 10 AI agents
│   ├── review.py             # CLI entry point
│   ├── entropy.py            # Shannon Entropy Analyzer
│   ├── impact.py             # Impact Graph
│   ├── pareto.py             # Pareto Hot Files
│   ├── bayes.py              # Bayesian Bug Predictor
│   ├── kolmogorov.py         # Kolmogorov NCD
│   ├── dashboard.py          # HTML Dashboard generator
│   └── ...                   # Cost tracker, fix tracker, etc.
│
├── vault/                    # Second Brain (Layer 4)
│   ├── 00_Inbox/
│   ├── 01_Dashboard/         # Central Command
│   ├── 03_Projects/          # Project tracking
│   ├── 04_Architecture/      # Meta-engineering notes
│   ├── 05_Life/              # Vision, Evolution Log, templates
│   ├── 06_Business/          # Metrics, standups
│   ├── 07_Journal/           # Daily reflections
│   └── 08_Ideas/             # Idea pipeline
│
├── ANTI_PATTERNS.md          # AI Immune System (Layer 3)
├── CONTEXT_MANIFEST_SPEC.md  # Context routing for AI
└── GETTING_STARTED.md        # This file
```

---

## Part 1: AI Rules Setup (5 minutes)

### Step 1: Install rules into your project
```bash
cd /path/to/your/project
python /path/to/solocto-os/agent-rules/setup.py .
```

This copies 13 files into your project:
- `.agent/rules/` — 5 rule files
- `DECISIONS.md`, `SOLUTION_PATTERNS.md`, `CHANGELOG.md`
- `docs/` — 3 documentation templates
- `PROMPT_LIBRARY.md`

### Step 2: Customize MAKER_PROFILE.md
Open `.agent/rules/MAKER_PROFILE.md` and fill in:
- Your communication style (casual/formal)
- Your expertise level
- Your preferences (terse answers vs detailed)
- Your timezone and work hours

**This is the most impactful file.** It's the difference between a generic assistant and YOUR personal CTO.

### Step 3: Customize PROJECT.md
Open `.agent/rules/PROJECT.md` and fill in:
- Project name and description
- Tech stack
- Architecture decisions (ADR section)
- Project-specific forbidden patterns

### Step 4: Verify
Open your AI tool (Cursor, VS Code, etc.) and ask:
```
What are the rules for this project? Summarize my MAKER_PROFILE.
```
If AI responds with YOUR rules — you're done. ✅

---

## Part 2: Agent Pipeline Setup (15 minutes)

### Prerequisites
- Python 3.10+
- An OpenRouter API key ($5 credit is enough for weeks)

### Step 1: Get an API key
1. Go to [openrouter.ai](https://openrouter.ai)
2. Sign up → Add $5 credit
3. Create an API key

### Step 2: Configure
```bash
cd /path/to/solocto-os/agent-pipeline/
cp .env.example .env
```

Edit `.env`:
```
OPENROUTER_API_KEY=sk-or-v1-your-key-here
```

### Step 3: Install dependencies
```bash
pip install httpx python-dotenv
```

### Step 4: Run your first review
```bash
# Review a specific file
python review.py review --level 2 --file /path/to/your/code.py

# Review with specific focus
python review.py review --level 3 --file handlers.py
```

### Step 5: Try other commands
```bash
# Architecture analysis
python review.py architect --file your_module.py

# Security audit
python review.py security --file payments.py

# Generate tests
python review.py test-gen --file your_code.py

# Performance check
python review.py perf --file slow_module.py

# Pre-deploy check
python review.py preflight

# Find code duplicates
python review.py dupes --dir src/

# Shannon entropy analysis
python entropy.py --dir src/

# Pareto hot files
python pareto.py --dir .
```

### Step 6: Set up auto-review (optional)
```bash
# Watch mode — auto-review on file save
python watch.py --dir src/

# GitHub Actions — auto-review on PR
# Copy .github/workflows/review.yml to your project
```

---

## Part 3: Second Brain Setup (30 minutes)

### Step 1: Install Obsidian
Download from [obsidian.md](https://obsidian.md) (free for personal use).

### Step 2: Open vault
Open Obsidian → "Open folder as vault" → select `vault/` from this package.

### Step 3: Install recommended plugins
1. **Dataview** — for dynamic dashboards and queries
2. **Calendar** — for journal navigation
3. **Templater** — for template shortcuts

### Step 4: Customize your Dashboard
Open `01_Dashboard/Main_Dashboard.md`:
- Replace `[YOUR_PRODUCT]` with your actual product names
- Update server table with your infrastructure
- Customize Skill Tree honestly

### Step 5: Fill in your Vision
Open `05_Life/VISION.md`:
- This is YOUR North Star
- Take 30 minutes. No AI. Just you and your thoughts.
- Be honest about where you are and where you want to be.

### Step 6: Set up your weekly ritual
Every Monday, 10 minutes:
1. Open Dashboard
2. Update metrics
3. Write a quick standup in `07_Journal/`
4. Check `05_Life/EVOLUTION_LOG.md` — add a session entry

---

## Part 4: Connecting Everything

### The Loop
```
Vision (05_Life/VISION.md)
    ↓ defines goals
Quarterly Strategy (05_Life/TEMPLATES/quarterly_strategy.md)
    ↓ breaks into OKRs
Projects (03_Projects/)
    ↓ tracked with .agent/rules/
Code → Agent Pipeline → Reviews → Fixes
    ↓ learnings go to
Anti-Patterns Registry + Solution Patterns
    ↓ compounds into
Evolution Log (05_Life/EVOLUTION_LOG.md)
    ↓ feeds back into
Vision (next review cycle)
```

### Daily Flow
1. Morning: check Dashboard (2 min)
2. Code: AI reads .agent/rules/ → context-aware responses
3. Pre-commit: `python review.py review --level 2`
4. Evening: quick journal entry (optional)

### Weekly Flow
1. Monday standup (10 min)
2. Update BUSINESS_METRICS
3. Process 00_Inbox → move items to their home
4. Update EVOLUTION_LOG if significant learning

### Monthly Flow
1. Review VISION — still aligned?
2. Update Quarterly Strategy OKRs
3. Prune Anti-Patterns — archive resolved ones
4. Skill Tree update

---

## Cost Breakdown

| Component | Cost | Notes |
|-----------|------|-------|
| AI Rules | Free | Markdown files |
| Agent Pipeline | ~$15-30/mo | OpenRouter API |
| Obsidian | Free | Personal use |
| Hosting (optional) | $0-5/mo | GitHub Pages |
| **Total** | **$15-35/mo** | For a full AI dev team |

Compare: CodeRabbit ($24/user/mo), Greptile ($30/user/mo), Cursor Pro ($40/mo)
You get ALL of them for $15-30/mo total.

---

## FAQ

**Q: Does this work with [my AI tool]?**
A: Yes. Rules are markdown. Any AI that reads project files will use them. Works with Cursor, VS Code + Copilot, Claude, Gemini, etc.

**Q: What programming language?**
A: Language-agnostic. The system works with Python, JavaScript, TypeScript, Go, Rust — anything.

**Q: What if I don't use Obsidian?**
A: The vault is just markdown files. Use Notion, Logseq, or even VS Code. Obsidian is recommended because of Dataview queries and graph view.

**Q: How do I update the system?**
A: Lifetime updates included. Re-download from your purchase link when new versions are released.

**Q: I found a bug / have a feature request**
A: DM on Telegram or email. We ship fixes fast.

---

> 🎯 **The key insight:** This system compounds. Week 1 feels like overhead.
> Month 1 feels natural. Month 3, you can't imagine working without it.
> By month 6, your Decision Log alone saves you hours.
