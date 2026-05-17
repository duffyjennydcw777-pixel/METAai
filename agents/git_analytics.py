"""
📊 Agent #19: Git Analytics
Глубокий анализ git-активности: velocity, bus factor, stale branches.

    python -m agents.git_analytics            # Анализ
    python -m agents.git_analytics --save     # + отчёт
"""

import subprocess
import sys
from datetime import datetime, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from agents.config import PROJECTS, REPORTS_DIR, GIT_STALE_BRANCH_DAYS


def git_cmd(project_path, args):
    try:
        result = subprocess.run(
            ["git"] + args,
            capture_output=True, text=True, timeout=15,
            cwd=str(project_path), encoding="utf-8", errors="replace",
        )
        return result.stdout.strip() if result.returncode == 0 else ""
    except (subprocess.TimeoutExpired, OSError):
        return ""


def analyze_project(name, path):
    if not (path / ".git").exists():
        return None

    data = {"name": name}

    # Total commits
    log = git_cmd(path, ["log", "--oneline", "--format=%H"])
    data["total_commits"] = len(log.split("\n")) if log else 0

    # Commits last 7/30 days
    w = git_cmd(path, ["log", "--oneline", "--since=7.days", "--format=%H"])
    m = git_cmd(path, ["log", "--oneline", "--since=30.days", "--format=%H"])
    data["commits_7d"] = len(w.split("\n")) if w else 0
    data["commits_30d"] = len(m.split("\n")) if m else 0

    # Velocity (commits/week over last 4 weeks)
    data["velocity"] = round(data["commits_30d"] / 4, 1) if data["commits_30d"] else 0

    # Contributors (bus factor)
    authors = git_cmd(path, ["log", "--format=%aN", "--since=90.days"])
    unique = set(a.strip() for a in authors.split("\n") if a.strip()) if authors else set()
    data["contributors"] = len(unique)
    data["bus_factor"] = len(unique)  # Simplified: 1 = risky

    # Stale branches
    branches_raw = git_cmd(path, ["branch", "-a", "--format=%(refname:short) %(committerdate:iso)"])
    stale = []
    cutoff = datetime.now() - timedelta(days=GIT_STALE_BRANCH_DAYS)
    for line in branches_raw.split("\n"):
        if not line.strip():
            continue
        parts = line.rsplit(" ", 3)
        if len(parts) >= 2:
            branch_name = parts[0]
            try:
                date_str = " ".join(parts[1:3]) if len(parts) >= 3 else parts[1]
                date = datetime.fromisoformat(date_str[:19])
                if date < cutoff and "HEAD" not in branch_name:
                    stale.append(branch_name)
            except (ValueError, IndexError):
                continue
    data["stale_branches"] = stale

    # Last commit date
    last = git_cmd(path, ["log", "-1", "--format=%ci"])
    data["last_commit"] = last[:10] if last else "—"

    # Files count
    files = git_cmd(path, ["ls-files"])
    data["total_files"] = len(files.split("\n")) if files else 0

    # Lines of code (Python only)
    py_files = [f for f in files.split("\n") if f.endswith(".py")] if files else []
    data["py_files"] = len(py_files)

    return data


def main():
    args = sys.argv[1:]
    save_md = "--save" in args or "--md" in args

    print("\n" + "=" * 60)
    print("  📊 GIT ANALYTICS — Phase 6 Agent #19")
    print("=" * 60)

    all_data = []
    for name, path in PROJECTS.items():
        data = analyze_project(name, path)
        if not data:
            continue
        all_data.append(data)

        bf_icon = "🔴" if data["bus_factor"] <= 1 else "🟢"
        stale_str = f", {len(data['stale_branches'])} stale" if data["stale_branches"] else ""

        print(f"  {name:12s}  commits: {data['total_commits']:4d}"
              f"  vel: {data['velocity']}/w"
              f"  {bf_icon} bus:{data['bus_factor']}"
              f"  files:{data['total_files']}"
              f"{stale_str}")

    print("=" * 60 + "\n")

    if save_md:
        lines = [
            f"# 📊 Git Analytics — {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            "",
            "| Проект | Commits | 7d | 30d | Vel/w | Bus | Files | Stale |",
            "|--------|:-------:|:--:|:---:|:-----:|:---:|:-----:|:-----:|",
        ]
        for d in all_data:
            lines.append(
                f"| {d['name']} | {d['total_commits']} | {d['commits_7d']}"
                f" | {d['commits_30d']} | {d['velocity']} | {d['bus_factor']}"
                f" | {d['total_files']} | {len(d['stale_branches'])} |"
            )
        REPORTS_DIR.mkdir(parents=True, exist_ok=True)
        path = REPORTS_DIR / f"git_analytics_{datetime.now().strftime('%Y%m%d')}.md"
        path.write_text("\n".join(lines), encoding="utf-8")
        print(f"📄 Сохранено: {path}")


if __name__ == "__main__":
    main()
