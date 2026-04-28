#!/usr/bin/env python3
"""
🚀 SoloCTO Prompt Kit — Setup Script
Автоматически копирует правила и шаблоны в ваш проект.

Использование:
    python setup.py                    # текущая директория
    python setup.py /path/to/project   # конкретный проект
    python setup.py --all              # все компоненты
    python setup.py --rules-only       # только правила
"""
import shutil
import sys
from pathlib import Path


SCRIPT_DIR = Path(__file__).parent

COMPONENTS = {
    "rules": {
        "src": SCRIPT_DIR / "rules",
        "dst": ".agent/rules",
        "files": ["GLOBAL.md", "PROJECT.md", "CODE_COMPLEXITY.md", "CONVENTIONS.md", "MAKER_PROFILE.md"],
    },
    "templates": {
        "src": SCRIPT_DIR / "templates",
        "dst": ".",
        "files": ["DECISIONS.md", "SOLUTION_PATTERNS.md", "CHANGELOG.md"],
    },
    "docs": {
        "src": SCRIPT_DIR / "docs",
        "dst": "docs",
        "files": ["1_PRODUCT.md", "2_ARCHITECTURE.md", "3_DEPLOYMENT.md"],
    },
}


def install(project_dir: Path, components: list[str] = None):
    """Install components into project directory."""
    if components is None:
        components = list(COMPONENTS.keys())

    project_dir = project_dir.resolve()
    if not project_dir.exists():
        print(f"❌ Директория не найдена: {project_dir}")
        sys.exit(1)

    print(f"📦 SoloCTO Prompt Kit → {project_dir.name}")
    print("-" * 40)

    total = 0
    for comp_name in components:
        comp = COMPONENTS[comp_name]
        src_dir = comp["src"]
        dst_dir = project_dir / comp["dst"]

        dst_dir.mkdir(parents=True, exist_ok=True)

        for filename in comp["files"]:
            src_file = src_dir / filename
            dst_file = dst_dir / filename

            if dst_file.exists():
                print(f"  ⚠️  {comp['dst']}/{filename} — уже существует, пропускаю")
                continue

            if src_file.exists():
                shutil.copy2(src_file, dst_file)
                print(f"  ✅ {comp['dst']}/{filename}")
                total += 1
            else:
                print(f"  ❌ {filename} — не найден в пакете")

    # Copy prompt library
    prompt_lib = SCRIPT_DIR / "PROMPT_LIBRARY.md"
    dst_prompt = project_dir / "PROMPT_LIBRARY.md"
    if prompt_lib.exists() and not dst_prompt.exists():
        shutil.copy2(prompt_lib, dst_prompt)
        print(f"  ✅ PROMPT_LIBRARY.md")
        total += 1

    print("-" * 40)
    print(f"📊 Установлено: {total} файлов")
    print()
    print("🎯 Следующие шаги:")
    print("   1. Заполни .agent/rules/MAKER_PROFILE.md (5 мин)")
    print("   2. Заполни .agent/rules/PROJECT.md (5 мин)")
    print("   3. Готово! AI теперь знает твои правила.")
    print()
    print("💡 Открой PROMPT_LIBRARY.md — 25 проверенных промптов для разработки")


def main():
    args = sys.argv[1:]

    # Determine project directory
    if "--help" in args or "-h" in args:
        print(__doc__)
        sys.exit(0)

    project_dir = Path.cwd()
    components = None

    for arg in args:
        if arg == "--all":
            components = list(COMPONENTS.keys())
        elif arg == "--rules-only":
            components = ["rules"]
        elif arg == "--templates-only":
            components = ["templates"]
        elif arg == "--docs-only":
            components = ["docs"]
        elif not arg.startswith("-"):
            project_dir = Path(arg)

    install(project_dir, components)


if __name__ == "__main__":
    main()
