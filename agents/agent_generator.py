"""
🧬 Agent #45: Agent Generator (Level 5 Core)
Система сама пишет новых агентов через LLM.
Код → drafts/ + Telegram approve → commit.

    python -m agents.agent_generator                   # Сгенерировать из gaps
    python -m agents.agent_generator --save            # + сохранить
    python -m agents.agent_generator --name uptime_monitor --desc "Ping ONYX servers"
"""

import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from agents.config import (
    EVOLUTION_DIR, AGENT_DRAFTS_DIR,
    LLM_MODEL,
)

AGENTS_DIR = Path(__file__).parent
PROJECT_ROOT = str(Path(__file__).resolve().parent.parent)


def load_json(path):
    if Path(path).exists():
        try:
            return json.loads(Path(path).read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            pass
    return {}


def get_gaps():
    """Получить gaps из System Architect."""
    arch = load_json(EVOLUTION_DIR / "architecture.json")
    return arch.get("suggestions", [])


def get_existing_agents():
    """Список существующих модулей."""
    return {
        p.stem for p in AGENTS_DIR.glob("*.py")
        if not p.name.startswith("_") and p.name != "config.py"
    }


def generate_agent_code(name, module_name, description):
    """Генерирует код агента через LLM."""
    try:
        from agents.llm_reasoner import reason
    except ImportError:
        return None, "LLM Reasoner not available"

    # Get next agent number
    existing = get_existing_agents()
    agent_num = len(existing) + 1

    prompt = (
        f"Напиши Python агента для системы METAai.\n\n"
        f"Название: {name}\n"
        f"Модуль: agents/{module_name}.py\n"
        f"Номер: Agent #{agent_num}\n"
        f"Описание: {description}\n\n"
        f"Требования:\n"
        f"1. Docstring с номером агента и описанием\n"
        f"2. sys.path.insert(0, str(Path(__file__).parent.parent))\n"
        f"3. from agents.config import REPORTS_DIR\n"
        f"4. def main() с sys.argv parsing (--save)\n"
        f"5. if __name__ == '__main__': main()\n"
        f"6. Красивый вывод с print и emoji\n"
        f"7. JSON отчёт при --save\n"
        f"8. ТОЛЬКО стандартная библиотека Python (json, urllib, pathlib, etc)\n"
        f"9. НЕ используй subprocess для опасных операций\n"
        f"10. Все данные — read-only + report\n\n"
        f"Верни ТОЛЬКО Python код, без маркдауна и пояснений."
    )

    result = reason(question=prompt)
    if result.get("error"):
        return None, result["error"]

    code = result.get("content", "")

    # Clean markdown code blocks if present
    if "```python" in code:
        code = code.split("```python", 1)[1]
        if "```" in code:
            code = code.split("```", 1)[0]
    elif "```" in code:
        code = code.split("```", 1)[1]
        if "```" in code:
            code = code.split("```", 1)[0]

    return code.strip(), None


def lint_code(code, module_name):
    """Проверяет код через Ruff."""
    draft_path = AGENT_DRAFTS_DIR / f"{module_name}.py"
    AGENT_DRAFTS_DIR.mkdir(parents=True, exist_ok=True)
    draft_path.write_text(code, encoding="utf-8")

    try:
        result = subprocess.run(
            [sys.executable, "-m", "ruff", "check", str(draft_path)],
            capture_output=True, text=True, timeout=10,
            cwd=PROJECT_ROOT, encoding="utf-8", errors="replace",
        )
        if result.returncode == 0:
            return True, "Clean"
        return False, result.stdout or result.stderr
    except Exception as exc:
        return False, str(exc)


def main():
    args = sys.argv[1:]
    save_md = "--save" in args

    print("\n" + "=" * 60)
    print("  🧬 AGENT GENERATOR — Phase 13 Agent #45 (Level 5)")
    print("=" * 60)

    # Check for explicit name
    name = None
    module_name = None
    description = None

    if "--name" in args:
        idx = args.index("--name")
        if idx + 1 < len(args):
            module_name = args[idx + 1]
            name = module_name.replace("_", " ").title()

    if "--desc" in args:
        idx = args.index("--desc")
        description = " ".join(args[idx + 1:]).split("--")[0].strip()

    # If no explicit name, check System Architect gaps
    if not module_name:
        gaps = get_gaps()
        existing = get_existing_agents()

        # Filter already existing
        new_gaps = [g for g in gaps if g["module"] not in existing]

        if not new_gaps:
            print("\n  ✅ Все пробелы закрыты! Нет новых агентов для генерации.")
            print("  Запусти System Architect: python -m agents.system_architect --save")
            print("\n" + "=" * 60 + "\n")
            return

        # Take highest priority
        gap = new_gaps[0]
        name = gap["name"]
        module_name = gap["module"]
        description = gap["description"]

        print("\n  🔍 Найден gap из System Architect:")
        print(f"     {name} ({module_name}.py)")
        print(f"     {description}")

    if not description:
        description = f"Автоматически сгенерированный агент: {name}"

    # Check if already exists
    target = AGENTS_DIR / f"{module_name}.py"
    if target.exists():
        print(f"\n  ⚠️ Агент {module_name}.py уже существует!")
        print("\n" + "=" * 60 + "\n")
        return

    # Generate code via LLM
    print(f"\n  🧠 Генерирую код: {name}...")
    print(f"     Модель: {LLM_MODEL}")

    code, error = generate_agent_code(name, module_name, description)

    if error or not code:
        print(f"\n  ❌ Ошибка: {error}")
        return

    print(f"  ✅ Код сгенерирован ({len(code)} символов)")

    # Lint
    print("  🔍 Проверяю через Ruff...")
    lint_ok, lint_msg = lint_code(code, module_name)

    if lint_ok:
        print("  ✅ Ruff: Clean")
    else:
        print(f"  ⚠️ Ruff: {lint_msg[:200]}")

    # Save to drafts
    draft_path = AGENT_DRAFTS_DIR / f"{module_name}.py"
    AGENT_DRAFTS_DIR.mkdir(parents=True, exist_ok=True)
    draft_path.write_text(code, encoding="utf-8")
    print(f"\n  📁 Сохранён в drafts: {draft_path}")

    # Preview
    lines = code.split("\n")
    print(f"\n  📝 Превью ({len(lines)} строк):")
    for line in lines[:15]:
        print(f"    {line}")
    if len(lines) > 15:
        print(f"    ... (+{len(lines) - 15} строк)")

    # Save generation log
    if save_md:
        EVOLUTION_DIR.mkdir(parents=True, exist_ok=True)
        gen_log_path = EVOLUTION_DIR / "generated_agents.json"
        gen_log = load_json(gen_log_path)
        if not isinstance(gen_log, list):
            gen_log = []

        gen_log.append({
            "timestamp": datetime.now().isoformat(),
            "name": name,
            "module": module_name,
            "description": description,
            "code_length": len(code),
            "lint_ok": lint_ok,
            "status": "draft",
            "draft_path": str(draft_path),
        })

        gen_log_path.write_text(
            json.dumps(gen_log, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        print(f"\n  💾 Лог: {gen_log_path}")

    print("\n  ━━━━━━━━━━━━━━━━━━━━━━━━")
    print("  📋 Следующие шаги:")
    print(f"    1. Проверь: code {draft_path}")
    print(f"    2. Одобри:  copy agents\\drafts\\{module_name}.py agents\\{module_name}.py")
    print("    3. Telegram: /approve")
    print("  ━━━━━━━━━━━━━━━━━━━━━━━━")

    print("\n" + "=" * 60 + "\n")


if __name__ == "__main__":
    main()
