"""
📦 Build Alibek Full Kit — SoloCTO OS + метаинженерия + инструкция установки.
Берёт полный пакет build_full_package + добавляет персональные файлы.
"""
import zipfile
from pathlib import Path
from datetime import datetime

VERSION = "1.0"
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent  # METAai root
SOLOCTO_DIR = SCRIPT_DIR / "solocto-os"
PROMPT_KIT_DIR = SCRIPT_DIR / "prompt-kit"
ALIBEK_KIT_DIR = SCRIPT_DIR / "alibek-kit"
OUT_DIR = SCRIPT_DIR / "dist"
OUT_DIR.mkdir(parents=True, exist_ok=True)

OUTPUT = OUT_DIR / "alibek-full-kit-v1.0.zip"
PREFIX = "alibek-full-kit"

# Agent pipeline files from METAai root
PIPELINE_FILES = [
    "review.py", "batch_review.py", "entropy.py", "impact.py",
    "pareto.py", "bayes.py", "kolmogorov.py", "review_history.py",
    "dashboard.py", "dashboard.html", "costs.py", "fix_tracker.py",
    "watch.py", "audit_project.py", ".env.example", "pyproject.toml",
]

AGENT_DIR = PROJECT_ROOT / "src" / "agents"


def add_file(zf, src, arcname):
    if src.exists():
        zf.write(src, arcname)
        print(f"  ✅ {arcname}")
    else:
        print(f"  ⚠️ SKIP: {src}")


def add_dir_recursive(zf, src_dir, arc_prefix):
    if not src_dir.exists():
        print(f"  ⚠️ SKIP dir: {src_dir}")
        return
    for f in sorted(src_dir.rglob("*")):
        if f.is_file() and "__pycache__" not in str(f):
            rel = f.relative_to(src_dir)
            arcname = f"{arc_prefix}/{rel}".replace("\\", "/")
            zf.write(f, arcname)
            print(f"  ✅ {arcname}")


def build():
    print("=" * 60)
    print(f"📦 Building Alibek Full Kit v{VERSION}")
    print("   SoloCTO OS + Meta-Engineering + Personal Setup")
    print("=" * 60)

    with zipfile.ZipFile(OUTPUT, "w", zipfile.ZIP_DEFLATED) as zf:

        # ── Personal files (инструкция, презентация, конфиги) ──
        print("\n📁 Personal Setup Files")
        if ALIBEK_KIT_DIR.exists():
            add_dir_recursive(zf, ALIBEK_KIT_DIR, f"{PREFIX}/00-setup")

        # ── Layer 1: AI Rules ──
        print("\n📁 Layer 1: AI Rules (agent-rules/)")
        rules_prefix = f"{PREFIX}/agent-rules"

        rules_dir = PROMPT_KIT_DIR / "rules"
        if rules_dir.exists():
            for f in sorted(rules_dir.iterdir()):
                if f.is_file():
                    add_file(zf, f, f"{rules_prefix}/rules/{f.name}")

        templates_dir = PROMPT_KIT_DIR / "templates"
        if templates_dir.exists():
            for f in sorted(templates_dir.iterdir()):
                if f.is_file():
                    add_file(zf, f, f"{rules_prefix}/templates/{f.name}")

        docs_dir = PROMPT_KIT_DIR / "docs"
        if docs_dir.exists():
            for f in sorted(docs_dir.iterdir()):
                if f.is_file():
                    add_file(zf, f, f"{rules_prefix}/docs/{f.name}")

        for fname in ["PROMPT_LIBRARY.md", "setup.py", "README.md"]:
            add_file(zf, PROMPT_KIT_DIR / fname, f"{rules_prefix}/{fname}")

        # ── Layer 2: Multi-Agent Pipeline ──
        print("\n📁 Layer 2: Multi-Agent Pipeline")
        pipe_prefix = f"{PREFIX}/agent-pipeline"

        for fname in PIPELINE_FILES:
            add_file(zf, PROJECT_ROOT / fname, f"{pipe_prefix}/{fname}")

        if AGENT_DIR.exists():
            for f in sorted(AGENT_DIR.iterdir()):
                if f.is_file() and f.suffix == ".py":
                    add_file(zf, f, f"{pipe_prefix}/src/agents/{f.name}")

        # ── Layer 3: Meta-Engineering ──
        print("\n📁 Layer 3: Meta-Engineering")
        for fname in ["ANTI_PATTERNS.md", "CONTEXT_MANIFEST_SPEC.md"]:
            add_file(zf, SOLOCTO_DIR / fname, f"{PREFIX}/{fname}")

        # ── Layer 4: Second Brain Vault ──
        print("\n📁 Layer 4: Second Brain Vault")
        vault_dir = SOLOCTO_DIR / "vault"
        if vault_dir.exists():
            add_dir_recursive(zf, vault_dir, f"{PREFIX}/vault")

        # ── Getting Started ──
        add_file(zf, SOLOCTO_DIR / "GETTING_STARTED.md", f"{PREFIX}/GETTING_STARTED.md")

        # ── README для Алибека ──
        readme = f"""# 🚀 Алибек's Full Vibecoding Kit v{VERSION}

> Полный набор от дяди Георгия — SoloCTO OS + метаинженерия + среда разработки.
> Дата сборки: {datetime.now().strftime('%Y-%m-%d')}

## 📦 Что внутри

```
{PREFIX}/
├── 00-setup/                  ← НАЧНИ СЮДА
│   ├── INSTALL_GUIDE.md       ← Пошаговая установка среды (30 мин)
│   ├── CAPABILITIES.html      ← Презентация возможностей (открой в браузере!)
│   └── configs/               ← Готовые конфиги для AI
│
├── agent-rules/               ← Layer 1: AI-правила
│   ├── rules/                 ← 5 правил для AI
│   ├── templates/             ← Шаблоны документации
│   ├── docs/                  ← Шаблоны проекта
│   ├── PROMPT_LIBRARY.md      ← 25 готовых промптов
│   └── setup.py               ← Автоустановка правил
│
├── agent-pipeline/            ← Layer 2: Мульти-агентный пайплайн
│   ├── review.py              ← AI Code Review CLI
│   ├── batch_review.py        ← Пакетный review
│   ├── src/agents/            ← 10 AI-агентов
│   ├── entropy.py             ← Shannon Entropy анализ
│   ├── impact.py              ← Impact Graph
│   ├── pareto.py              ← Pareto анализ
│   ├── bayes.py               ← Bayesian анализ
│   ├── kolmogorov.py          ← Kolmogorov Complexity
│   ├── dashboard.py           ← HTML Dashboard
│   └── ...
│
├── ANTI_PATTERNS.md           ← Layer 3: Реестр ошибок AI
├── CONTEXT_MANIFEST_SPEC.md   ← Layer 3: Context Routing
│
├── vault/                     ← Layer 4: Obsidian Second Brain
│   ├── 01_Inbox/
│   ├── 02_Areas/
│   ├── 03_Projects/
│   ├── 04_Resources/
│   └── 05_Life/
│
└── GETTING_STARTED.md         ← Общий гайд по SoloCTO OS
```

## 🚀 Quick Start

1. **Сначала** — открой `00-setup/INSTALL_GUIDE.md` и установи среду
2. **Потом** — открой `00-setup/CAPABILITIES.html` в браузере
3. **Затем** — читай `GETTING_STARTED.md` для SoloCTO OS

Пиши в телегу если что! 💪
"""
        zf.writestr(f"{PREFIX}/README.md", readme)
        print("  ✅ README.md (персональный)")

    size_kb = OUTPUT.stat().st_size / 1024
    print(f"\n{'=' * 60}")
    print(f"✅ Готово! {OUTPUT.name} ({size_kb:.0f} KB)")
    print(f"📍 Путь: {OUTPUT}")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    build()
