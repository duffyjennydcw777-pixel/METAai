"""
📦 Build Zalina Dev Kit — сборка ZIP-пакета для Залины.
Собирает все наработки из METAai + персональную инструкцию.
"""
import zipfile
from pathlib import Path

# Paths
ROOT = Path(__file__).parent.parent  # METAai root
DIST = ROOT / "products" / "dist"
DIST.mkdir(parents=True, exist_ok=True)

OUTPUT = DIST / "zalina-dev-kit-v1.0.zip"

# Source directories
PROMPT_KIT = ROOT / "products" / "prompt-kit"
SOLOCTO = ROOT / "products" / "solocto-os"
AGENTS = ROOT / "src" / "agents"
DOCS = ROOT / "docs"


def add_file(zf: zipfile.ZipFile, src: Path, arcname: str):
    """Add a file to zip with a custom archive name."""
    if src.exists():
        zf.write(src, arcname)
        print(f"  ✅ {arcname}")
    else:
        print(f"  ⚠️ SKIP (not found): {src}")


def add_dir(zf: zipfile.ZipFile, src_dir: Path, arc_prefix: str, pattern: str = "*"):
    """Add all files from a directory to zip."""
    if not src_dir.exists():
        print(f"  ⚠️ SKIP dir (not found): {src_dir}")
        return
    for f in sorted(src_dir.rglob(pattern)):
        if f.is_file() and "__pycache__" not in str(f) and ".pyc" not in str(f):
            rel = f.relative_to(src_dir)
            arcname = f"{arc_prefix}/{rel}"
            zf.write(f, arcname)
            print(f"  ✅ {arcname}")


def build():
    print("=" * 60)
    print("📦 Building Zalina Dev Kit v1.0")
    print("=" * 60)

    with zipfile.ZipFile(OUTPUT, "w", zipfile.ZIP_DEFLATED) as zf:
        prefix = "zalina-dev-kit"

        # ─── README (создаётся inline) ──────────────────────
        readme = README_CONTENT
        zf.writestr(f"{prefix}/README.md", readme)
        print("  ✅ README.md (персональный)")

        # ─── ROADMAP ────────────────────────────────────────
        roadmap = ROADMAP_CONTENT
        zf.writestr(f"{prefix}/ROADMAP.md", roadmap)
        print("  ✅ ROADMAP.md")

        # ─── Phase 1: Foundation ────────────────────────────
        print("\n📁 Phase 1: Foundation")
        p1 = f"{prefix}/phase-1-foundation"

        # Rules
        for rule in ["GLOBAL.md", "MAKER_PROFILE.md", "PROJECT.md"]:
            add_file(zf, PROMPT_KIT / "rules" / rule, f"{p1}/rules/{rule}")

        # Templates
        for tmpl in ["CHANGELOG.md", "DECISIONS.md", "SOLUTION_PATTERNS.md"]:
            add_file(zf, PROMPT_KIT / "templates" / tmpl, f"{p1}/templates/{tmpl}")

        # Docs templates
        for doc in ["1_PRODUCT.md", "2_ARCHITECTURE.md", "3_DEPLOYMENT.md"]:
            add_file(zf, PROMPT_KIT / "docs" / doc, f"{p1}/docs/{doc}")

        # Setup script
        add_file(zf, PROMPT_KIT / "setup.py", f"{p1}/setup.py")

        # .gitignore example
        zf.writestr(f"{p1}/examples/.gitignore", GITIGNORE_CONTENT)
        print("  ✅ examples/.gitignore")

        # .env.example
        zf.writestr(f"{p1}/examples/.env.example", ENV_EXAMPLE_CONTENT)
        print("  ✅ examples/.env.example")

        # ─── Phase 2: Prompts ───────────────────────────────
        print("\n📁 Phase 2: Prompts")
        p2 = f"{prefix}/phase-2-prompts"
        add_file(zf, PROMPT_KIT / "PROMPT_LIBRARY.md", f"{p2}/PROMPT_LIBRARY.md")
        add_file(zf, PROMPT_KIT / "rules" / "CONVENTIONS.md", f"{p2}/CONVENTIONS.md")

        # ─── Phase 3: Agents ───────────────────────────────
        print("\n📁 Phase 3: Code Review Agents")
        p3 = f"{prefix}/phase-3-agents"
        add_file(zf, PROMPT_KIT / "rules" / "CODE_COMPLEXITY.md", f"{p3}/CODE_COMPLEXITY.md")
        add_dir(zf, AGENTS, f"{p3}/src/agents")
        add_file(zf, ROOT / "review.py", f"{p3}/review.py")
        add_file(zf, ROOT / "batch_review.py", f"{p3}/batch_review.py")
        add_file(zf, ROOT / ".env.example", f"{p3}/.env.example")
        add_file(zf, ROOT / "pyproject.toml", f"{p3}/pyproject.toml")

        # ─── Phase 4: Automation ────────────────────────────
        print("\n📁 Phase 4: Automation")
        p4 = f"{prefix}/phase-4-automation"
        add_file(zf, ROOT / "watch.py", f"{p4}/watch.py")
        add_file(zf, ROOT / "dashboard.py", f"{p4}/dashboard.py")
        add_file(zf, ROOT / "costs.py", f"{p4}/costs.py")
        add_file(zf, ROOT / "fix_tracker.py", f"{p4}/fix_tracker.py")

        # GitHub Actions
        gh_workflow = ROOT / ".github" / "workflows"
        if gh_workflow.exists():
            add_dir(zf, gh_workflow, f"{p4}/github-actions")

        # Git hook
        add_file(zf, ROOT / "deploy" / "pre-push", f"{p4}/deploy/pre-push")

        # ─── Phase 5: Meta ──────────────────────────────────
        print("\n📁 Phase 5: Meta-Engineering")
        p5 = f"{prefix}/phase-5-meta"
        add_file(zf, DOCS / "context_manifest_spec.md", f"{p5}/context_manifest_spec.md")
        add_file(zf, SOLOCTO / "ANTI_PATTERNS.md", f"{p5}/ANTI_PATTERNS.md")
        add_file(zf, ROOT / ".agent" / "context_manifest.yaml", f"{p5}/example_context_manifest.yaml")

        # Scientific analytics
        for script in ["entropy.py", "pareto.py", "bayes.py", "impact.py", "kolmogorov.py", "review_history.py"]:
            add_file(zf, ROOT / script, f"{p5}/analytics/{script}")

        # Second Brain vault
        vault = SOLOCTO / "vault"
        if vault.exists():
            add_dir(zf, vault, f"{p5}/vault")

    size_kb = OUTPUT.stat().st_size / 1024
    print(f"\n{'=' * 60}")
    print(f"✅ Готово! {OUTPUT.name} ({size_kb:.0f} KB)")
    print(f"📍 Путь: {OUTPUT}")
    print(f"{'=' * 60}")


# ─── Inline content ─────────────────────────────────────────

README_CONTENT = """# 🎁 Zalina Dev Kit v1.0

> Персональный пакет от Георгия — всё, что нужно для AI-powered разработки.

---

## 👋 Привет, Залина!

Этот пакет — не учебник и не курс. Это **рабочая система**, которую мы с AI построили за месяцы реальной работы. Каждый файл здесь проверен на боевых проектах.

**Не пытайся освоить всё сразу.** Пакет разбит на 5 фаз — начни с первой и двигайся дальше по мере роста навыков.

---

## 📦 Что внутри

```
zalina-dev-kit/
├── README.md              ← Ты сейчас здесь
├── ROADMAP.md             ← Подробный план внедрения по фазам
│
├── phase-1-foundation/    ← НАЧНИ ОТСЮДА (неделя 1-2)
│   ├── rules/             ← AI-правила для твоих проектов
│   ├── templates/         ← Шаблоны документации
│   ├── docs/              ← Шаблоны описания проекта
│   ├── setup.py           ← Скрипт автоустановки
│   └── examples/          ← .gitignore, .env.example
│
├── phase-2-prompts/       ← Когда освоишь фазу 1 (неделя 3-4)
│   ├── PROMPT_LIBRARY.md  ← 25 готовых промптов
│   └── CONVENTIONS.md     ← Стиль кода
│
├── phase-3-agents/        ← Когда напишешь 2-3 проекта (месяц 2)
│   ├── src/agents/        ← 10 AI-агентов
│   ├── review.py          ← CLI для code review
│   └── ...
│
├── phase-4-automation/    ← Когда сделаешь первый деплой (месяц 3)
│   ├── github-actions/    ← Авто-review при push
│   ├── watch.py           ← Авто-review при сохранении файла
│   └── dashboard.py       ← HTML-дашборд
│
└── phase-5-meta/          ← Когда ведёшь 2+ проекта (месяц 4+)
    ├── analytics/         ← Научная аналитика кода
    ├── vault/             ← Obsidian Second Brain
    └── ...
```

---

## 🚀 Быстрый старт (15 минут)

### Шаг 1: Установи инструменты
- [VS Code](https://code.visualstudio.com/) — редактор кода
- [Python 3.10+](https://python.org/downloads/) — язык программирования
- [Git](https://git-scm.com/downloads) — контроль версий
- AI-помощник: [Gemini](https://gemini.google.com/) или [Claude](https://claude.ai/)

### Шаг 2: Создай свой первый проект
```bash
mkdir my-first-project
cd my-first-project
git init
```

### Шаг 3: Установи правила AI
```bash
python path/to/phase-1-foundation/setup.py .
```
Это создаст `.agent/rules/`, `docs/`, `CHANGELOG.md` и другие файлы.

### Шаг 4: Заполни MAKER_PROFILE.md
Открой `.agent/rules/MAKER_PROFILE.md` и заполни:
- Свою роль (Junior Dev)
- Стиль общения (casual, подробно)
- Зоны роста (что хочешь изучить)
- Предпочтения (объяснения перед кодом)

**Это самый важный шаг.** После этого AI будет отвечать не generic, а ТЕБЕ.

### Шаг 5: Настрой AI-помощника
В настройках Gemini/Claude/Cursor добавь:
```
Отвечай на русском.
Я начинающий разработчик, объясняй подробно.
Перед каждым ответом читай .agent/rules/ проекта.
Предлагай улучшения, которые я не вижу.
```

### Шаг 6: Проверь
Спроси AI: «Какие правила у этого проекта? Расскажи мой MAKER_PROFILE.»
Если AI отвечает из твоих файлов — всё работает! ✅

---

## 💡 Советы

1. **MAKER_PROFILE = самый важный файл.** Заполни его первым.
2. **Не торопись.** Осваивай по одной фазе за 1-2 недели.
3. **Записывай решения.** Через полгода DECISIONS.md — это золото.
4. **$5 на OpenRouter** хватит на недели (для фазы 3).
5. **Ошибки — это нормально.** Anti-Pattern Registry существует именно для этого.

---

## 📖 Подробности

Читай **ROADMAP.md** — там детальный план с объяснениями каждой фазы.

---

> *Собрано с ❤️ Георгием и AI · Май 2026*
"""

ROADMAP_CONTENT = open(
    Path(__file__).parent.parent.parent.parent
    / "brain" / "cc47b841-6fca-46e0-b537-47ccc30a7b97" / "roadmap_zalina.md",
    encoding="utf-8"
).read() if (
    Path(__file__).parent.parent.parent.parent
    / "brain" / "cc47b841-6fca-46e0-b537-47ccc30a7b97" / "roadmap_zalina.md"
).exists() else "# Roadmap\\nСм. README.md"

GITIGNORE_CONTENT = """# Python
__pycache__/
*.py[cod]
*.egg-info/
dist/
build/
.venv/
venv/

# Environment
.env
*.local

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db
desktop.ini

# Project
reviews/
generated_fixes/
generated_tests/
*.log
"""

ENV_EXAMPLE_CONTENT = """# API Keys (получи на openrouter.ai)
OPENROUTER_API_KEY=sk-or-v1-your-key-here

# Telegram Bot (опционально, для ботов)
# TG_BOT_TOKEN=123456:ABC-...
# TG_ADMIN_ID=your-telegram-id

# Database (опционально)
# DATABASE_URL=sqlite:///data.db
"""


if __name__ == "__main__":
    build()
