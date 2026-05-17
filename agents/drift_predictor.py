"""
📈 Agent #12: Drift Predictor
Предсказывает деградацию health score.

Использование:
    python -m agents.drift_predictor          # Анализ + запись
    python -m agents.drift_predictor --save   # + Markdown отчёт
"""

import json
import re
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from agents.config import (
    PROJECTS, REPORTS_DIR, HISTORY_FILE,
    HEALTH_CRITICAL_THRESHOLD, TREND_ALERT_DAYS,
)


def load_history():
    if HISTORY_FILE.exists():
        try:
            return json.loads(HISTORY_FILE.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return {}
    return {}


def save_history(history):
    HISTORY_FILE.parent.mkdir(parents=True, exist_ok=True)
    HISTORY_FILE.write_text(json.dumps(history, indent=2, ensure_ascii=False), encoding="utf-8")


def parse_current_health():
    reports = sorted(REPORTS_DIR.glob("health_*.md"), reverse=True)
    if not reports:
        return {}
    content = reports[0].read_text(encoding="utf-8", errors="ignore")
    scores = {}
    for m in re.finditer(r"## [🟢🟡🔴]\s+(\w+)\s+—\s+(\d+)%", content):
        scores[m.group(1)] = int(m.group(2))
    return scores


def compute_velocity(history, project, days=7):
    dates = sorted(history.keys(), reverse=True)[:days + 1]
    values = [history[d][project] for d in dates if project in history[d]]
    if len(values) < 2:
        return None
    return round((values[0] - values[-1]) / (len(values) - 1), 1)


def detect_decline(history, project):
    dates = sorted(history.keys(), reverse=True)
    count = 0
    for i in range(len(dates) - 1):
        cur = history[dates[i]].get(project, 0)
        prev = history[dates[i + 1]].get(project, 0)
        if cur < prev:
            count += 1
        else:
            break
    return count


def predict_days(current, velocity, threshold):
    if velocity is None or velocity >= 0 or current <= threshold:
        return None
    return round((current - threshold) / abs(velocity))


def main():
    args = sys.argv[1:]
    save_md = "--save" in args or "--md" in args

    history = load_history()
    current = parse_current_health()
    if not current:
        print("⚠️ Нет health отчётов")
        return

    today = datetime.now().strftime("%Y-%m-%d")
    history[today] = current
    save_history(history)

    print("\n" + "=" * 60)
    print("  📈 DRIFT PREDICTOR — Phase 4 Agent #12")
    print(f"  История: {len(history)} снимков")
    print("=" * 60)

    lines = [
        f"# 📈 Drift Predictor — {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        "", f"История: {len(history)} снимков", "",
        "| Проект | Score | Velocity | Decline | Прогноз |",
        "|--------|:-----:|:--------:|:-------:|---------|",
    ]

    for project in PROJECTS:
        if project not in current:
            continue
        score = current[project]
        vel = compute_velocity(history, project)
        decline = detect_decline(history, project)
        pred = predict_days(score, vel, HEALTH_CRITICAL_THRESHOLD)

        vel_str = f"{vel:+.1f}%/d" if vel is not None else "—"
        pred_str = f"critical через {pred}д" if pred else "стабильно"

        if vel is not None and vel <= -5:
            icon = "🔴"
        elif decline >= TREND_ALERT_DAYS:
            icon = "🟡"
        elif vel is not None and vel > 0:
            icon = "📈"
        else:
            icon = "🟢"

        print(f"  {icon} {project:12s}  {score}%  vel: {vel_str}  decline: {decline}д  {pred_str}")
        lines.append(f"| {project} | {icon} {score}% | {vel_str} | {decline}д | {pred_str} |")

    print("=" * 60 + "\n")

    if save_md:
        REPORTS_DIR.mkdir(parents=True, exist_ok=True)
        path = REPORTS_DIR / f"drift_{datetime.now().strftime('%Y%m%d')}.md"
        path.write_text("\n".join(lines), encoding="utf-8")
        print(f"📄 Сохранено: {path}")


if __name__ == "__main__":
    main()
