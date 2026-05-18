"""
🧪 Agent #54: Experiment Tracker
Трекинг A/B экспериментов: гипотеза, метрика, результат, значимость.

    python -m agents.experiment_tracker               # Статус
    python -m agents.experiment_tracker --save        # + сохранить
    python -m agents.experiment_tracker --new "Тест цены $5 vs $7"
    python -m agents.experiment_tracker --close 1 --winner a
"""

import json
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from agents.config import EVOLUTION_DIR

EXPERIMENTS_FILE = EVOLUTION_DIR / "experiments.json"


def load_experiments():
    if EXPERIMENTS_FILE.exists():
        try:
            return json.loads(EXPERIMENTS_FILE.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            pass
    return {"experiments": [], "next_id": 1}


def save_experiments(data):
    EVOLUTION_DIR.mkdir(parents=True, exist_ok=True)
    EXPERIMENTS_FILE.write_text(
        json.dumps(data, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


def create_experiment(name, hypothesis=None, metric=None, variant_a=None, variant_b=None):
    """Создать новый эксперимент."""
    data = load_experiments()
    exp_id = data["next_id"]

    experiment = {
        "id": exp_id,
        "name": name,
        "hypothesis": hypothesis or "TBD",
        "metric": metric or "conversion_rate",
        "variant_a": variant_a or "Control (текущий)",
        "variant_b": variant_b or "Treatment (новый)",
        "status": "running",
        "created": datetime.now().isoformat(),
        "closed": None,
        "winner": None,
        "results": {
            "a": {"samples": 0, "conversions": 0, "value": 0},
            "b": {"samples": 0, "conversions": 0, "value": 0},
        },
        "notes": [],
    }

    data["experiments"].append(experiment)
    data["next_id"] = exp_id + 1
    save_experiments(data)
    return experiment


def close_experiment(exp_id, winner, notes=None):
    """Закрыть эксперимент с результатом."""
    data = load_experiments()

    for exp in data["experiments"]:
        if exp["id"] == exp_id:
            exp["status"] = "closed"
            exp["closed"] = datetime.now().isoformat()
            exp["winner"] = winner
            if notes:
                exp["notes"].append({
                    "timestamp": datetime.now().isoformat(),
                    "text": notes,
                })
            save_experiments(data)
            return exp

    return None


def update_results(exp_id, variant, samples=0, conversions=0, value=0):
    """Обновить результаты варианта."""
    data = load_experiments()

    for exp in data["experiments"]:
        if exp["id"] == exp_id:
            r = exp["results"].get(variant, {})
            r["samples"] = r.get("samples", 0) + samples
            r["conversions"] = r.get("conversions", 0) + conversions
            r["value"] = r.get("value", 0) + value
            exp["results"][variant] = r
            save_experiments(data)
            return exp

    return None


def calculate_significance(exp):
    """Простой расчёт статистической значимости (Z-test)."""
    ra = exp["results"].get("a", {})
    rb = exp["results"].get("b", {})

    na = ra.get("samples", 0)
    nb = rb.get("samples", 0)
    ca = ra.get("conversions", 0)
    cb = rb.get("conversions", 0)

    if na == 0 or nb == 0:
        return 0, "insufficient_data"

    pa = ca / na
    pb = cb / nb

    # Pooled proportion
    p_pool = (ca + cb) / (na + nb)
    if p_pool == 0 or p_pool == 1:
        return 0, "no_variance"

    # Z-score
    import math
    se = math.sqrt(p_pool * (1 - p_pool) * (1/na + 1/nb))
    if se == 0:
        return 0, "no_variance"

    z = abs(pa - pb) / se

    # Significance levels
    if z >= 2.576:
        return z, "99%"
    elif z >= 1.96:
        return z, "95%"
    elif z >= 1.645:
        return z, "90%"
    else:
        return z, "not_significant"


def main():
    args = sys.argv[1:]
    save_md = "--save" in args

    print("\n" + "=" * 60)
    print("  🧪 EXPERIMENT TRACKER — Phase 14 Agent #54")
    print("=" * 60)

    # Create new experiment
    if "--new" in args:
        idx = args.index("--new")
        name = " ".join(args[idx + 1:]).split("--")[0].strip()
        if not name:
            name = "Unnamed Experiment"

        exp = create_experiment(name)
        print(f"\n  ✅ Эксперимент #{exp['id']} создан: {name}")
        print(f"     Гипотеза: {exp['hypothesis']}")
        print(f"     Метрика: {exp['metric']}")
        print(f"     A: {exp['variant_a']}")
        print(f"     B: {exp['variant_b']}")
        print("\n" + "=" * 60 + "\n")
        return

    # Close experiment
    if "--close" in args:
        idx = args.index("--close")
        exp_id = int(args[idx + 1]) if idx + 1 < len(args) else 0
        winner = "a"
        if "--winner" in args:
            w_idx = args.index("--winner")
            winner = args[w_idx + 1] if w_idx + 1 < len(args) else "a"

        exp = close_experiment(exp_id, winner)
        if exp:
            print(f"\n  ✅ Эксперимент #{exp_id} закрыт. Победитель: {winner.upper()}")
        else:
            print(f"\n  ❌ Эксперимент #{exp_id} не найден")
        print("\n" + "=" * 60 + "\n")
        return

    # Show all experiments
    data = load_experiments()
    experiments = data.get("experiments", [])

    if not experiments:
        print("\n  ℹ️ Нет экспериментов")
        print("  Создай: python -m agents.experiment_tracker --new \"Название\"")
        print("\n" + "=" * 60 + "\n")
        return

    running = [e for e in experiments if e["status"] == "running"]
    closed = [e for e in experiments if e["status"] == "closed"]

    print(f"\n  📊 Всего: {len(experiments)} ({len(running)} активных, {len(closed)} завершённых)")

    if running:
        print(f"\n  🟢 Активные ({len(running)}):")
        for exp in running:
            z_score, significance = calculate_significance(exp)
            ra = exp["results"].get("a", {})
            rb = exp["results"].get("b", {})

            print(f"\n    #{exp['id']} {exp['name']}")
            print(f"      Гипотеза: {exp['hypothesis']}")
            print(f"      Метрика: {exp['metric']}")
            print(f"      A ({exp['variant_a']}): "
                  f"{ra.get('conversions', 0)}/{ra.get('samples', 0)}")
            print(f"      B ({exp['variant_b']}): "
                  f"{rb.get('conversions', 0)}/{rb.get('samples', 0)}")

            if significance != "insufficient_data":
                print(f"      📈 Z-score: {z_score:.2f} → {significance}")
            else:
                print(f"      ⏳ Недостаточно данных")

    if closed:
        print(f"\n  ⬜ Завершённые ({len(closed)}):")
        for exp in closed:
            winner = exp.get("winner", "?").upper()
            print(f"    #{exp['id']} {exp['name']} → Победитель: {winner}")

    if save_md:
        save_experiments(data)
        print(f"\n  💾 Сохранено: {EXPERIMENTS_FILE}")

    print("\n" + "=" * 60 + "\n")


if __name__ == "__main__":
    main()
