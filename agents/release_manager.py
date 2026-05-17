"""
🏷️ Agent #21: Release Manager
Авто-тегирование версий и генерация release notes.

    python -m agents.release_manager              # Показать текущую версию
    python -m agents.release_manager --tag        # Создать тег
    python -m agents.release_manager --save       # + отчёт
"""

import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from agents.config import ROOT, REPORTS_DIR, RELEASE_LOG


def git_cmd(args):
    try:
        result = subprocess.run(
            ["git"] + args,
            capture_output=True, text=True, timeout=15,
            cwd=str(ROOT), encoding="utf-8", errors="replace",
        )
        return result.stdout.strip() if result.returncode == 0 else ""
    except (subprocess.TimeoutExpired, OSError):
        return ""


def get_latest_tag():
    return git_cmd(["describe", "--tags", "--abbrev=0"]) or "v0.0.0"


def get_commits_since_tag(tag):
    log = git_cmd(["log", f"{tag}..HEAD", "--oneline", "--format=%s"])
    return [line.strip() for line in log.split("\n") if line.strip()] if log else []


def categorize_commits(commits):
    categories = {"feat": [], "fix": [], "chore": [], "other": []}
    for c in commits:
        if c.startswith("feat"):
            categories["feat"].append(c)
        elif c.startswith("fix"):
            categories["fix"].append(c)
        elif c.startswith("chore"):
            categories["chore"].append(c)
        else:
            categories["other"].append(c)
    return categories


def bump_version(current, commits):
    """Определяет следующую версию по conventional commits."""
    match = re.match(r"v?(\d+)\.(\d+)\.(\d+)", current)
    if not match:
        return "v1.0.0"
    major, minor, patch = int(match.group(1)), int(match.group(2)), int(match.group(3))

    has_feat = any(c.startswith("feat") for c in commits)
    has_breaking = any("BREAKING" in c or "!" in c.split(":")[0] for c in commits)

    if has_breaking:
        return f"v{major + 1}.0.0"
    if has_feat:
        return f"v{major}.{minor + 1}.0"
    return f"v{major}.{minor}.{patch + 1}"


def generate_release_notes(version, categories):
    lines = [
        f"## {version} — {datetime.now().strftime('%Y-%m-%d')}",
        "",
    ]
    section_names = {
        "feat": "🚀 Features",
        "fix": "🐛 Fixes",
        "chore": "🔧 Maintenance",
        "other": "📝 Other",
    }
    for key, title in section_names.items():
        if categories[key]:
            lines.append(f"### {title}")
            for c in categories[key]:
                lines.append(f"- {c}")
            lines.append("")
    return "\n".join(lines)


def create_tag(version):
    result = subprocess.run(
        ["git", "tag", "-a", version, "-m", f"Release {version}"],
        capture_output=True, text=True, timeout=15,
        cwd=str(ROOT), encoding="utf-8", errors="replace",
    )
    return result.returncode == 0


def update_release_log(notes):
    if RELEASE_LOG.exists():
        existing = RELEASE_LOG.read_text(encoding="utf-8")
        # Insert after header
        if "# Releases" in existing:
            parts = existing.split("\n", 2)
            updated = parts[0] + "\n\n" + notes + "\n" + (parts[2] if len(parts) > 2 else "")
        else:
            updated = "# Releases — METAai\n\n" + notes + "\n" + existing
    else:
        updated = "# Releases — METAai\n\n" + notes
    RELEASE_LOG.write_text(updated, encoding="utf-8")


def main():
    args = sys.argv[1:]
    do_tag = "--tag" in args
    save_md = "--save" in args or "--md" in args

    current_tag = get_latest_tag()
    commits = get_commits_since_tag(current_tag)
    categories = categorize_commits(commits)
    next_version = bump_version(current_tag, commits)

    print("\n" + "=" * 60)
    print("  🏷️ RELEASE MANAGER — Phase 6 Agent #21")
    print("=" * 60)
    print(f"  Текущий тег: {current_tag}")
    print(f"  Коммитов с тега: {len(commits)}")
    print(f"  Следующая версия: {next_version}")
    print()

    for key, items in categories.items():
        if items:
            print(f"  {key}: {len(items)}")

    if not commits:
        print("\n  ✅ Нет новых коммитов — релиз не нужен")
        print("=" * 60 + "\n")
        return

    notes = generate_release_notes(next_version, categories)

    if do_tag:
        if create_tag(next_version):
            print(f"\n  ✅ Тег {next_version} создан")
            update_release_log(notes)
            print("  📄 RELEASES.md обновлён")
        else:
            print("\n  ❌ Ошибка создания тега")
    else:
        print("\n  [DRY-RUN] Добавь --tag для создания")

    print("=" * 60 + "\n")

    if save_md:
        REPORTS_DIR.mkdir(parents=True, exist_ok=True)
        path = REPORTS_DIR / f"release_{datetime.now().strftime('%Y%m%d')}.md"
        path.write_text(notes, encoding="utf-8")
        print(f"📄 Сохранено: {path}")


if __name__ == "__main__":
    main()
