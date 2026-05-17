"""
🧬 Agent #22: Knowledge Distiller
Извлекает паттерны и знания из всех отчётов, сохраняет в Second Brain.

    python -m agents.knowledge_distiller          # Анализ
    python -m agents.knowledge_distiller --save   # + в Knowledge
"""

import re
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from agents.config import REPORTS_DIR, KNOWLEDGE_DIR


def scan_reports():
    """Сканирует все отчёты и извлекает ключевые данные."""
    if not REPORTS_DIR.exists():
        return {}

    data = {
        "total_reports": 0,
        "agent_runs": Counter(),
        "issues_found": [],
        "recommendations": [],
        "health_history": [],
        "recurring_problems": Counter(),
    }

    for f in sorted(REPORTS_DIR.glob("*.md")):
        data["total_reports"] += 1
        content = f.read_text(encoding="utf-8", errors="ignore")

        # Identify agent type from filename
        agent_type = f.stem.split("_")[0]
        data["agent_runs"][agent_type] += 1

        # Extract health scores
        for m in re.finditer(r"(\w+)\s+.*?(\d+)%", content):
            project = m.group(1)
            score = int(m.group(2))
            if 0 < score <= 100:
                data["health_history"].append({
                    "project": project, "score": score, "file": f.name
                })

        # Extract issues/problems
        for m in re.finditer(r"[🔴❌]\s*(.+)", content):
            issue = m.group(1).strip()[:100]
            data["issues_found"].append(issue)
            # Track recurring
            key = re.sub(r"\d+", "N", issue)[:50]
            data["recurring_problems"][key] += 1

        # Extract recommendations
        for m in re.finditer(r"[→➡️]\s*(.+)", content):
            rec = m.group(1).strip()[:100]
            data["recommendations"].append(rec)

    return data


def extract_patterns(data):
    """Извлекает паттерны из данных."""
    patterns = []

    # Recurring problems (appeared 3+ times)
    for problem, count in data["recurring_problems"].most_common(10):
        if count >= 2:
            patterns.append({
                "type": "recurring",
                "description": problem,
                "count": count,
                "severity": "high" if count >= 5 else "medium",
            })

    # Most active agents
    for agent, count in data["agent_runs"].most_common(5):
        patterns.append({
            "type": "activity",
            "description": f"Agent '{agent}' ran {count} times",
            "count": count,
            "severity": "info",
        })

    return patterns


def generate_knowledge(data, patterns):
    """Генерирует knowledge document."""
    now = datetime.now().strftime("%Y-%m-%d %H:%M")

    lines = [
        "---",
        f"updated: {now}",
        "tags: [auto-generated, knowledge, meta-engineering]",
        "---",
        "",
        "# 🧬 METAai Knowledge Base — Auto-Generated",
        "",
        f"_Обновлено: {now}_",
        f"_Источник: {data['total_reports']} отчётов_",
        "",
        "## 📊 Статистика агентов",
        "",
        "| Агент | Прогонов |",
        "|-------|:--------:|",
    ]

    for agent, count in data["agent_runs"].most_common():
        lines.append(f"| {agent} | {count} |")

    if patterns:
        lines.extend(["", "## 🔄 Повторяющиеся паттерны", ""])
        for p in patterns:
            icon = "🔴" if p["severity"] == "high" else "🟡" if p["severity"] == "medium" else "ℹ️"
            lines.append(f"- {icon} **{p['description']}** (×{p['count']})")

    # Top recommendations
    if data["recommendations"]:
        lines.extend(["", "## 💡 Собранные рекомендации", ""])
        seen = set()
        for rec in data["recommendations"][:15]:
            if rec not in seen:
                lines.append(f"- {rec}")
                seen.add(rec)

    lines.append("")
    return "\n".join(lines)


def main():
    args = sys.argv[1:]
    save_md = "--save" in args or "--md" in args

    data = scan_reports()

    print("\n" + "=" * 60)
    print("  🧬 KNOWLEDGE DISTILLER — Phase 6 Agent #22")
    print("=" * 60)

    if not data or data["total_reports"] == 0:
        print("  ⚠️ Нет отчётов для анализа")
        print("=" * 60 + "\n")
        return

    patterns = extract_patterns(data)

    print(f"  📊 Отчётов проанализировано: {data['total_reports']}")
    print(f"  🔍 Проблем найдено: {len(data['issues_found'])}")
    print(f"  🔄 Паттернов: {len(patterns)}")
    print(f"  💡 Рекомендаций: {len(data['recommendations'])}")

    for p in patterns[:5]:
        icon = "🔴" if p["severity"] == "high" else "🟡"
        print(f"  {icon} {p['description']} (×{p['count']})")

    knowledge = generate_knowledge(data, patterns)

    if save_md:
        # Save to Obsidian
        KNOWLEDGE_DIR.mkdir(parents=True, exist_ok=True)
        kb_path = KNOWLEDGE_DIR / "Auto_Knowledge.md"
        kb_path.write_text(knowledge, encoding="utf-8")
        print(f"\n  📄 Obsidian: {kb_path}")

        # Save to reports
        REPORTS_DIR.mkdir(parents=True, exist_ok=True)
        path = REPORTS_DIR / f"knowledge_{datetime.now().strftime('%Y%m%d')}.md"
        path.write_text(knowledge, encoding="utf-8")
        print(f"  📄 Reports: {path}")

    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
