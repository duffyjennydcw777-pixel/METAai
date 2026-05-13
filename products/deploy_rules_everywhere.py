"""
🚀 Deploy unified rules to ALL projects.
Creates missing GLOBAL.md, CODE_COMPLEXITY.md, CONVENTIONS.md, MODES.md,
CHANGELOG.md, DECISIONS.md, SOLUTION_PATTERNS.md, REFLEXION_LOG.md,
EXPERIMENTS.md across every project.

v2.0 — 2026-05-13: Added MODES.md (9 thinking modes), REFLEXION_LOG.md,
EXPERIMENTS.md, Detective-first protocol. Meta-Engineering OS system-wide.
"""
from pathlib import Path

DEV = Path(r"C:\Dev")

# ─── All projects with their status ─────────────────────────
PROJECTS = {
    # Production
    "ONYX": {"lang": "python", "desc": "VPN SaaS — Telegram bot + XRay/VLESS"},
    "Sylectus": {"lang": "python", "desc": "Sylectus Bid Assistant — freight logistics"},
    "VPN": {"lang": "python", "desc": "VPN provisioning scripts"},
    # Active Development
    "FamilyQuest": {"lang": "react", "desc": "Family gamification — FastAPI + React"},
    "METAai": {"lang": "python", "desc": "AI Team OS — Multi-Agent Pipeline"},
    "AmazonBOT": {"lang": "python", "desc": "Amazon Seller Automation / Profit Analytics"},
    "LifeBot": {"lang": "python", "desc": "Telegram бот для Life OS"},
    "NewLife": {"lang": "python", "desc": "BotForge — платформа Telegram ботов"},
    "betbot": {"lang": "python", "desc": "Sports betting analytics bot"},
    "trading_bot": {"lang": "python", "desc": "Binance trading bot"},
    # Early Stage
    "ASTRAL_APP": {"lang": "react", "desc": "Esoteric platform — Vite + Capacitor"},
    "Project2": {"lang": "react", "desc": "AI Call Center — React dashboard"},
}

# ─── Standard files content ─────────────────────────────────

GLOBAL_MD = """# 🌍 Global Agent Rules

> Эти правила применяются ко ВСЕМ проектам без исключений.
> AI ОБЯЗАН прочитать этот файл перед началом работы.

---

## 🔒 Безопасность

1. **НИКОГДА** не оставляй API ключи, пароли, токены в коде или Markdown. ТОЛЬКО `.env`.
2. При обновлении `.env` на сервере — НЕ используй sed. Создай скрипт.
3. После деплоя файлов через SCP — ВСЕГДА проверяй `chmod`/`chown`.

## 📝 Документация

4. Задача НЕ завершена, пока `CHANGELOG.md` не обновлён.
5. Сохраняй ВСЕ существующие комментарии и docstrings, если они не относятся к твоим изменениям.
6. При изменении архитектуры — добавь запись в `DECISIONS.md`.
7. При нахождении проверенного решения — добавь в `SOLUTION_PATTERNS.md`.

## 🧪 Code Complexity Levels

8. **ПЕРЕД каждой задачей** определи уровень сложности (см. `CODE_COMPLEXITY.md`).
9. Формат вывода в начале ответа:
   ```
   📊 Complexity: Level [1/2/3] — [Trivial/Standard/Complex]
   🧪 Testing: [план]
   ```
10. При сомнении между уровнями — **ВСЕГДА выбирай высший**.

## 🔄 Качество

11. **Не ломай то, что работает.** При изменении кода — проверь зависимые модули.
12. Перед деплоем — проверь что `.env` синхронизирован.
13. **ZERO COPY-PASTE**: если можешь создать файл, сгенерировать код или запустить команду — делай это САМ.
14. После 5+ изменённых файлов — напоминай о git commit.

## 🧠 Контекст

15. В начале каждой сессии прочитай `DECISIONS.md` и `SOLUTION_PATTERNS.md`.
16. Проверяй `.agent/rules/` перед каждым ответом.
17. При работе с сервером — ВСЕГДА сверяйся с таблицей серверов (если есть).
"""

CCL_MD = """# 🧪 Code Complexity Levels (CCL)

> Система классификации кода для AI. Определяет объём тестирования.
> AI ОБЯЗАН классифицировать КАЖДОЕ изменение перед выполнением.

---

## Level 1 — 🟢 Trivial (Деплой без тестов)
- README, CHANGELOG, комментарии, документация
- CSS/стили (если не ломают layout)
- .gitignore, .editorconfig
- Логирование (logger.info)
- Переименование переменных (без изменения логики)

**⚠️ НЕ Level 1:** конфиги, .env, feature flags → **Level 2**

## Level 2 — 🟡 Standard (3 теста)
- Новый endpoint / функция
- Баг-фикс, рефакторинг, валидация, фильтрация
- Новая модель данных

**Тесты:** ✅ Happy path · ❌ Error case · 🔲 Edge case

## Level 3 — 🔴 Complex (85% уверенности)
- Финансовые расчёты, auth, миграции БД
- Async/concurrent, security, core-алгоритмы
- Деплой на production

**AI обязан:** назвать % уверенности, перечислить риски, предложить rollback.

## 📌 Post-Mortem Protocol
Если баг проскочил: код `CCL-XXX`, повысить уровень НАВСЕГДА, записать в anti-patterns.

> **Правило:** при сомнении — ВСЕГДА выбирай высший уровень.
"""

def conventions_md(lang):
    if lang == "react":
        return """# 🎨 Code Conventions

## Язык и стиль
| Правило | Значение |
|---------|----------|
| Язык комментариев | Русский |
| Язык переменных | English |
| Стиль именования | `camelCase` (JS) / `PascalCase` (компоненты) |
| Максимальная длина строки | 120 символов |
| Отступы | 2 пробела |

## Файлы
- Один компонент = один файл (SRP)
- Максимум 300 строк на файл
- Imports: React → библиотеки → сторы → утилиты → компоненты

## Git
- Commit message: `[тип]: описание` (feat, fix, refactor, docs, chore)
- Не коммитить `node_modules/`, `.env`, `dist/`
"""
    else:
        return """# 🎨 Code Conventions

## Язык и стиль
| Правило | Значение |
|---------|----------|
| Язык комментариев | Русский |
| Язык переменных | English |
| Стиль именования | `snake_case` |
| Максимальная длина строки | 120 символов |
| Отступы | 4 пробела |

## Файлы
- Один файл = одна ответственность (SRP)
- Максимум 300 строк на файл
- Imports: stdlib → third-party → local

## Функции
- Максимум 30 строк на функцию
- Docstring для каждой публичной функции
- Type hints обязательны (Python 3.10+)
- Return early pattern (guard clauses)

## Обработка ошибок
- Конкретные исключения, не `except Exception`
- Логирование ошибок с контекстом

## Git
- Commit message: `[тип]: описание` (feat, fix, refactor, docs, chore)
- Не коммитить `.env`, `__pycache__/`, `node_modules/`
"""

CHANGELOG_TEMPLATE = """# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]

### Added
- Initial project setup
"""

DECISIONS_TEMPLATE = """# 📋 Архитектурные решения (ADR)

> Каждое важное решение записывается здесь.

---

_Пока нет записей. Первое решение добавится автоматически._
"""

PATTERNS_TEMPLATE = """# 🔧 Solution Patterns

> Проверенные решения. При похожей задаче — используй паттерн отсюда.

---

_Пока нет записей. Первый паттерн добавится при нахождении рабочего решения._
"""

MODES_SOURCE = DEV / "METAai" / ".agent" / "rules" / "MODES.md"

REFLEXION_TEMPLATE = """# 🔄 REFLEXION LOG — Стратегические выводы

> Лог стратегических решений, которые не сработали.
> Anti-Pattern Registry = тактические ошибки. Reflexion Log = стратегические промахи.
> AI ОБЯЗАН проверять этот файл при стратегических решениях.

---

_Пока нет записей. Первая запись добавится при стратегическом промахе._
"""

EXPERIMENTS_TEMPLATE = """# 🧪 EXPERIMENTS — A/B Testing Framework

> Не гадать, а измерять. Каждое продуктовое решение — эксперимент с гипотезой и метрикой.
> AI ОБЯЗАН предлагать EXP-запись при изменении тарифов, формата, UX.

---

_Пока нет записей. Первый эксперимент добавится при продуктовом изменении._
"""

def write_if_missing(path: Path, content: str):
    """Write file only if it doesn't exist."""
    if path.exists():
        print(f"  ⏭️  SKIP (exists): {path.name}")
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    print(f"  ✅ CREATED: {path.name}")
    return True

def deploy():
    total_created = 0
    total_skipped = 0

    # Read MODES.md master copy
    modes_content = ""
    if MODES_SOURCE.exists():
        modes_content = MODES_SOURCE.read_text(encoding="utf-8")
        print(f"📋 MODES.md master loaded ({len(modes_content)} bytes)")
    else:
        print(f"⚠️  MODES.md master not found at {MODES_SOURCE}")

    for name, info in PROJECTS.items():
        proj = DEV / name
        if not proj.exists():
            print(f"\n⚠️  {name} — directory not found, skipping")
            continue

        print(f"\n{'='*50}")
        print(f"📁 {name} ({info['desc'][:50]}...)")
        print(f"{'='*50}")

        rules_dir = proj / ".agent" / "rules"

        # Standard rules
        files = {
            rules_dir / "GLOBAL.md": GLOBAL_MD,
            rules_dir / "CODE_COMPLEXITY.md": CCL_MD,
            rules_dir / "CONVENTIONS.md": conventions_md(info["lang"]),
        }

        # Add MODES.md (from master copy)
        if modes_content and name != "METAai":  # Don't overwrite master
            files[rules_dir / "MODES.md"] = modes_content

        # Root-level docs
        root_files = {
            proj / "CHANGELOG.md": CHANGELOG_TEMPLATE,
            proj / "DECISIONS.md": DECISIONS_TEMPLATE,
            proj / "SOLUTION_PATTERNS.md": PATTERNS_TEMPLATE,
            proj / "REFLEXION_LOG.md": REFLEXION_TEMPLATE,
            proj / "EXPERIMENTS.md": EXPERIMENTS_TEMPLATE,
        }

        for path, content in {**files, **root_files}.items():
            created = write_if_missing(path, content)
            if created:
                total_created += 1
            else:
                total_skipped += 1

    print(f"\n{'='*50}")
    print(f"🏁 Done! Created: {total_created} | Skipped (already exist): {total_skipped}")
    print(f"{'='*50}")

if __name__ == "__main__":
    deploy()

