"""
⏱️ Agent #42: Performance Benchmarker
Замеряет скорость и ресурсы каждого агента.
Трекает деградацию/улучшение производительности.

    python -m agents.perf_benchmarker              # Бенчмарк
    python -m agents.perf_benchmarker --save       # + сохранить
"""

import json
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from agents.config import (
    BENCHMARK_CACHE, BENCHMARK_HISTORY_LIMIT, EVOLUTION_DIR,
)

# Агенты для бенчмарка (быстрые, без сетевых вызовов)
BENCHMARK_AGENTS = [
    ("signal_router", "--save"),
    ("deal_evaluator", "--save"),
    ("trend_matcher", "--save"),
    ("action_generator", "--save"),
    ("knowledge_distiller", "--save"),
    ("portfolio_tracker", "--save"),
    ("self_tuner", "--save"),
]


def benchmark_agent(module_name, extra_args=""):
    """Запускает агента и замеряет время."""
    cmd = [sys.executable, "-m", f"agents.{module_name}"]
    if extra_args:
        cmd.append(extra_args)

    start = time.time()
    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=60,
            cwd=str(Path(__file__).parent.parent),
        )
        elapsed = round(time.time() - start, 3)
        return {
            "agent": module_name,
            "time_sec": elapsed,
            "exit_code": result.returncode,
            "ok": result.returncode == 0,
            "stdout_lines": len(result.stdout.splitlines()),
            "stderr_lines": len(result.stderr.splitlines()),
        }
    except subprocess.TimeoutExpired:
        return {
            "agent": module_name,
            "time_sec": 60.0,
            "exit_code": -1,
            "ok": False,
            "stdout_lines": 0,
            "stderr_lines": 0,
            "error": "timeout",
        }
    except Exception as exc:
        return {
            "agent": module_name,
            "time_sec": round(time.time() - start, 3),
            "exit_code": -1,
            "ok": False,
            "error": str(exc),
        }


def load_history():
    """Загружает историю бенчмарков."""
    if BENCHMARK_CACHE.exists():
        try:
            data = json.loads(BENCHMARK_CACHE.read_text(encoding="utf-8"))
            return data.get("history", [])
        except (json.JSONDecodeError, OSError):
            pass
    return []


def compare_with_previous(current, history):
    """Сравнивает с предыдущим запуском."""
    if not history:
        return {}

    prev = history[-1]
    prev_agents = {r["agent"]: r for r in prev.get("results", [])}

    deltas = {}
    for r in current:
        prev_r = prev_agents.get(r["agent"])
        if prev_r:
            delta = r["time_sec"] - prev_r["time_sec"]
            pct = (delta / prev_r["time_sec"] * 100) if prev_r["time_sec"] > 0 else 0
            deltas[r["agent"]] = {
                "delta_sec": round(delta, 3),
                "delta_pct": round(pct, 1),
                "trend": "⬆️" if pct > 10 else "⬇️" if pct < -10 else "➡️",
            }

    return deltas


def main():
    args = sys.argv[1:]
    save_md = "--save" in args

    print("\n" + "=" * 60)
    print("  ⏱️ PERFORMANCE BENCHMARKER — Phase 12 Agent #42")
    print("=" * 60)

    print(f"\n  🚀 Бенчмарк {len(BENCHMARK_AGENTS)} агентов...\n")

    results = []
    for module_name, extra in BENCHMARK_AGENTS:
        print(f"    ⏱️ {module_name}...", end=" ", flush=True)
        bench = benchmark_agent(module_name, extra)
        results.append(bench)

        icon = "✅" if bench["ok"] else "❌"
        print(f"{icon} {bench['time_sec']:.3f}s")

    # Summary
    ok_count = sum(1 for r in results if r["ok"])
    total_time = sum(r["time_sec"] for r in results)
    avg_time = total_time / len(results) if results else 0

    print("\n  📊 Результаты:")
    print(f"    {'Агент':<25s} {'Время':>8s} {'Статус':>8s}")
    print(f"    {'─'*25} {'─'*8} {'─'*8}")

    for r in sorted(results, key=lambda x: -x["time_sec"]):
        icon = "✅" if r["ok"] else "❌"
        print(f"    {r['agent']:<25s} {r['time_sec']:>7.3f}s {icon}")

    print(f"\n    Всего: {total_time:.3f}s | Среднее: {avg_time:.3f}s | "
          f"Успешно: {ok_count}/{len(results)}")

    # Compare with history
    history = load_history()
    deltas = compare_with_previous(results, history)

    if deltas:
        print("\n  📈 Сравнение с предыдущим:")
        for agent, d in sorted(deltas.items(), key=lambda x: x[1]["delta_pct"]):
            trend = d["trend"]
            delta = d["delta_sec"]
            pct = d["delta_pct"]
            sign = "+" if delta > 0 else ""
            print(f"    {trend} {agent:<25s} {sign}{delta:.3f}s ({sign}{pct:.1f}%)")

    # Slowest agent warning
    slowest = max(results, key=lambda x: x["time_sec"])
    if slowest["time_sec"] > 5:
        print(f"\n  ⚠️ Самый медленный: {slowest['agent']} ({slowest['time_sec']:.1f}s)")

    if save_md:
        EVOLUTION_DIR.mkdir(parents=True, exist_ok=True)

        # Update history
        run_entry = {
            "timestamp": datetime.now().isoformat(),
            "total_time": round(total_time, 3),
            "avg_time": round(avg_time, 3),
            "success_rate": round(ok_count / len(results), 3),
            "results": results,
        }

        history.append(run_entry)
        history = history[-BENCHMARK_HISTORY_LIMIT:]  # Keep N

        BENCHMARK_CACHE.write_text(json.dumps({
            "last_run": datetime.now().isoformat(),
            "history": history,
        }, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"\n  💾 Сохранено: {BENCHMARK_CACHE}")

    print("\n" + "=" * 60 + "\n")


if __name__ == "__main__":
    main()
