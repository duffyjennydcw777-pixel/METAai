"""
🔍 Agent #6: Dependency Scanner (Phase 2)
Сканирует зависимости проектов на актуальность.

Что делает:
1. Находит package.json / pyproject.toml / requirements.txt
2. Считает количество зависимостей
3. Проверяет наличие lock-файлов
4. Выявляет проекты без зафиксированных версий
5. Опционально: pip audit / npm audit

Использование:
    python -m agents.dependency_scanner              # Все проекты
    python -m agents.dependency_scanner --audit      # С проверкой уязвимостей
"""

import subprocess
import sys
import re
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent))
from agents.config import PROJECTS, REPORTS_DIR


def scan_python_deps(project_path: Path) -> dict:
    """Сканирует Python зависимости."""
    result = {
        "type": "python",
        "manager": None,
        "deps_count": 0,
        "dev_deps_count": 0,
        "has_lock": False,
        "has_venv": False,
        "unpinned": [],
        "deps_list": [],
    }

    # pyproject.toml
    pyproject = project_path / "pyproject.toml"
    if pyproject.exists():
        result["manager"] = "pyproject.toml"
        content = pyproject.read_text(encoding="utf-8", errors="replace")

        # Считаем зависимости
        in_deps = False
        for line in content.splitlines():
            if "dependencies" in line.lower() and "=" in line:
                in_deps = True
                continue
            if in_deps:
                if line.strip().startswith("]"):
                    in_deps = False
                elif line.strip().startswith('"') or line.strip().startswith("'"):
                    dep = line.strip().strip('",').strip("',")
                    result["deps_list"].append(dep)
                    result["deps_count"] += 1
                    # Проверяем pinning
                    if not re.search(r"[>=<~!]", dep):
                        result["unpinned"].append(dep)

    # requirements.txt
    req = project_path / "requirements.txt"
    if req.exists():
        if not result["manager"]:
            result["manager"] = "requirements.txt"
        for line in req.read_text(encoding="utf-8", errors="replace").splitlines():
            line = line.strip()
            if line and not line.startswith("#"):
                result["deps_count"] += 1
                if not re.search(r"[>=<~!=]", line):
                    result["unpinned"].append(line)

    # Lock files
    result["has_lock"] = (
        (project_path / "poetry.lock").exists()
        or (project_path / "Pipfile.lock").exists()
        or (project_path / "uv.lock").exists()
    )

    # Virtual env
    result["has_venv"] = (
        (project_path / ".venv").exists()
        or (project_path / "venv").exists()
    )

    return result


def scan_node_deps(project_path: Path) -> dict:
    """Сканирует Node.js зависимости."""
    result = {
        "type": "node",
        "manager": None,
        "deps_count": 0,
        "dev_deps_count": 0,
        "has_lock": False,
        "unpinned": [],
    }

    pkg = project_path / "package.json"
    if not pkg.exists():
        return result

    result["manager"] = "package.json"

    try:
        import json
        data = json.loads(pkg.read_text(encoding="utf-8"))
        deps = data.get("dependencies", {})
        dev_deps = data.get("devDependencies", {})
        result["deps_count"] = len(deps)
        result["dev_deps_count"] = len(dev_deps)

        # Проверяем pinning
        for name, version in {**deps, **dev_deps}.items():
            if version.startswith("^") or version.startswith("~") or version == "*":
                result["unpinned"].append(f"{name}@{version}")

    except (ImportError, Exception):
        pass

    result["has_lock"] = (
        (project_path / "package-lock.json").exists()
        or (project_path / "yarn.lock").exists()
        or (project_path / "pnpm-lock.yaml").exists()
    )

    return result


def run_audit(project_path: Path, dep_type: str) -> list[str]:
    """Запускает аудит безопасности."""
    warnings = []

    if dep_type == "python":
        try:
            result = subprocess.run(
                [sys.executable, "-m", "pip", "audit"],
                cwd=str(project_path),
                capture_output=True, text=True, timeout=30,
                encoding="utf-8", errors="replace"
            )
            if result.returncode != 0 and result.stdout:
                warnings.append(result.stdout[:500])
        except Exception:
            pass

    elif dep_type == "node":
        try:
            result = subprocess.run(
                ["npm", "audit", "--json"],
                cwd=str(project_path),
                capture_output=True, text=True, timeout=30,
                encoding="utf-8", errors="replace"
            )
            if result.returncode != 0:
                warnings.append("npm audit нашёл уязвимости")
        except Exception:
            pass

    return warnings


def generate_report(do_audit: bool = False) -> str:
    """Генерирует отчёт по зависимостям."""
    now = datetime.now()
    lines = [
        "# 🔍 Dependency Scanner Report",
        "",
        f"> Дата: {now.strftime('%Y-%m-%d %H:%M')}",
        f"> Аудит: {'✅ Включён' if do_audit else '⬜ Выключен'}",
        "",
    ]

    summary_table = []

    for name, path in PROJECTS.items():
        if not path.exists():
            continue

        py_deps = scan_python_deps(path)
        node_deps = scan_node_deps(path)

        # Определяем основной стек
        if py_deps["manager"] and node_deps["manager"]:
            stack = "Python + Node"
        elif py_deps["manager"]:
            stack = "Python"
        elif node_deps["manager"]:
            stack = "Node.js"
        else:
            lines.append(f"### ⚪ {name} — нет зависимостей")
            lines.append("")
            continue

        total_deps = py_deps["deps_count"] + node_deps["deps_count"]
        total_unpinned = len(py_deps["unpinned"]) + len(node_deps["unpinned"])
        has_lock = py_deps["has_lock"] or node_deps["has_lock"]

        # Оценка
        if total_unpinned == 0 and has_lock:
            icon = "✅"
        elif total_unpinned > 5 or not has_lock:
            icon = "🔴"
        else:
            icon = "🟡"

        lines.append(f"### {icon} {name} ({stack})")
        lines.append("")
        lines.append(f"| Метрика | Значение |")
        lines.append(f"|---------|----------|")
        lines.append(f"| Зависимостей | {total_deps} |")

        if node_deps["dev_deps_count"]:
            lines.append(f"| Dev-зависимостей | {node_deps['dev_deps_count']} |")

        lines.append(f"| Lock-файл | {'✅' if has_lock else '❌'} |")

        if py_deps["has_venv"]:
            lines.append(f"| Virtual env | ✅ |")

        if total_unpinned:
            lines.append(f"| Незафиксировано | ⚠️ {total_unpinned} |")

        lines.append("")

        if total_unpinned > 0:
            all_unpinned = py_deps["unpinned"] + node_deps["unpinned"]
            lines.append(f"**Незафиксированные:**")
            for dep in all_unpinned[:5]:
                lines.append(f"- `{dep}`")
            if len(all_unpinned) > 5:
                lines.append(f"- ... и ещё {len(all_unpinned) - 5}")
            lines.append("")

        # Аудит
        if do_audit:
            if py_deps["manager"]:
                warnings = run_audit(path, "python")
                if warnings:
                    lines.append("**⚠️ Аудит Python:**")
                    for w in warnings:
                        lines.append(f"- {w[:200]}")
                    lines.append("")

            if node_deps["manager"]:
                warnings = run_audit(path, "node")
                if warnings:
                    lines.append("**⚠️ Аудит Node:**")
                    for w in warnings:
                        lines.append(f"- {w[:200]}")
                    lines.append("")

        summary_table.append((name, stack, total_deps, total_unpinned, has_lock))
        lines.append("---")
        lines.append("")

    # Сводная таблица
    if summary_table:
        lines.extend([
            "## 📊 Сводка",
            "",
            "| Проект | Стек | Зависимости | Незафикс. | Lock |",
            "|--------|------|:-----------:|:---------:|:----:|",
        ])
        for name, stack, deps, unpinned, lock in summary_table:
            lock_icon = "✅" if lock else "❌"
            unpin_str = f"⚠️ {unpinned}" if unpinned else "0"
            lines.append(f"| {name} | {stack} | {deps} | {unpin_str} | {lock_icon} |")

    return "\n".join(lines)


def main():
    args = sys.argv[1:]
    do_audit = "--audit" in args

    report = generate_report(do_audit)
    print(report)

    if "--save" in args:
        REPORTS_DIR.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d")
        path = REPORTS_DIR / f"deps_{timestamp}.md"
        path.write_text(report, encoding="utf-8")
        print(f"\n📄 Сохранено: {path}")


if __name__ == "__main__":
    main()
