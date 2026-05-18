"""
🧠 Agent #44: LLM Reasoner
Обёртка над OpenRouter API для глубокого анализа.
Используется другими агентами для LLM-powered reasoning.

    python -m agents.llm_reasoner                          # Тест
    python -m agents.llm_reasoner --mode strategy          # Стратегия
    python -m agents.llm_reasoner --mode analyze_deal      # Анализ сделки
    python -m agents.llm_reasoner --ask "Вопрос"           # Свободный вопрос
"""

import json
import os
import sys
import urllib.request
import urllib.parse
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from agents.config import (
    LLM_API_KEY_ENV, LLM_BASE_URL_ENV,
    LLM_MODEL, LLM_MAX_TOKENS, LLM_TEMPERATURE, LLM_TIMEOUT,
    REPORTS_DIR, EVOLUTION_DIR,
)


def load_json(path):
    if Path(path).exists():
        try:
            return json.loads(Path(path).read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            pass
    return {}


def get_api_creds():
    try:
        from dotenv import load_dotenv
        load_dotenv(Path(__file__).parent.parent / ".env")
    except ImportError:
        pass
    api_key = os.environ.get(LLM_API_KEY_ENV, "")
    base_url = os.environ.get(LLM_BASE_URL_ENV, "https://openrouter.ai/api/v1")
    return api_key, base_url


def gather_system_context():
    """Собирает контекст из всех отчётов для LLM."""
    ctx = {}

    # Knowledge
    knowledge = load_json(EVOLUTION_DIR / "knowledge.json")
    if knowledge.get("insights"):
        top = sorted(knowledge["insights"], key=lambda x: -x.get("priority", 0))[:10]
        ctx["top_insights"] = [
            {"source": i.get("source", ""), "type": i.get("type", ""),
             "text": i.get("text", "")[:100], "priority": i.get("priority", 0)}
            for i in top
        ]

    # Portfolio
    portfolio = load_json(EVOLUTION_DIR / "portfolio.json")
    if portfolio.get("projects"):
        ctx["portfolio"] = [
            {"name": p["name"], "stage": p["stage"], "health": p["health"],
             "mrr": p["mrr"]}
            for p in portfolio["projects"]
        ]

    # Tuner
    tuner = load_json(EVOLUTION_DIR / "tuner.json")
    if tuner.get("metrics"):
        ctx["system_health"] = {
            "health_pct": tuner.get("system_health_pct", 0),
            "signal_noise": tuner["metrics"].get("signal_noise", {}).get("ratio", 0),
            "scrape_success": tuner["metrics"].get("scrape_success", {}).get("success_rate", 0),
        }

    # Deals
    deals = load_json(REPORTS_DIR / "signals" / "deal_evaluations.json")
    if deals.get("evaluations"):
        ctx["deals"] = [
            {"name": d.get("name", ""), "verdict": d.get("verdict", ""),
             "score": d.get("total_score", 0)}
            for d in deals["evaluations"][:5]
        ]

    # Trends
    trends = load_json(REPORTS_DIR / "signals" / "trend_matches.json")
    if trends.get("matches"):
        ctx["trends"] = [
            {"keywords": m.get("keywords", []), "count": m.get("match_count", 0)}
            for m in trends["matches"][:5]
        ]

    return ctx


SYSTEM_PROMPT = """Ты — AI-аналитик системы METAai. Это автономный governance engine для управления портфелем бизнесов.

Портфель:
- ONYX: VPN SaaS (Telegram Mini App)
- Sylectus: Logistics TMS
- FreshCut Greens: Микрозелень (ферма)

Система собирает данные с ProductHunt, TrustMRR, Acquire.com, мониторит конкурентов, оценивает M&A сделки, генерирует задачи.

Отвечай кратко, структурированно, с конкретными рекомендациями. Используй данные из контекста."""


MODES = {
    "strategy": {
        "prompt": "Проанализируй текущее состояние системы и дай 3-5 стратегических рекомендаций. "
                  "Учитывай: здоровье портфеля, рыночные тренды, конкурентную разведку.",
        "description": "Стратегические рекомендации",
    },
    "analyze_deal": {
        "prompt": "Проанализируй текущие M&A сделки. Какую из них стоит рассмотреть в первую очередь? "
                  "Дай оценку рисков и потенциала.",
        "description": "Анализ M&A сделок",
    },
    "market_brief": {
        "prompt": "Дай краткий обзор рыночной ситуации на основе трендов и конкурентной разведки. "
                  "Какие ниши сейчас горячие? Что это значит для нашего портфеля?",
        "description": "Рыночный обзор",
    },
    "find_gaps": {
        "prompt": "Проанализируй архитектуру системы METAai. Какие области бизнеса не покрыты агентами? "
                  "Какие данные мы не собираем, но должны? Предложи 3 новых агента.",
        "description": "Поиск архитектурных пробелов",
    },
    "new_business": {
        "prompt": "На основе всех данных системы (тренды, сделки, конкуренты) предложи 3 НОВЫХ бизнес-идеи, "
                  "которые НЕ связаны с текущим портфелем (VPN/Logistics/Farm). "
                  "Для каждой: название, рынок, time-to-MVP, почему именно сейчас.",
        "description": "Генерация новых бизнес-идей",
    },
}


def call_llm(api_key, base_url, messages):
    """Вызов OpenRouter API."""
    url = f"{base_url}/chat/completions"
    payload = json.dumps({
        "model": LLM_MODEL,
        "messages": messages,
        "max_tokens": LLM_MAX_TOKENS,
        "temperature": LLM_TEMPERATURE,
    }).encode("utf-8")

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
        "HTTP-Referer": "https://metaai.local",
        "X-Title": "METAai LLM Reasoner",
    }

    req = urllib.request.Request(url, data=payload, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=LLM_TIMEOUT) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            choice = data.get("choices", [{}])[0]
            message = choice.get("message", {})
            usage = data.get("usage", {})
            return {
                "content": message.get("content", ""),
                "model": data.get("model", LLM_MODEL),
                "tokens_in": usage.get("prompt_tokens", 0),
                "tokens_out": usage.get("completion_tokens", 0),
                "cost": round(usage.get("prompt_tokens", 0) * 0.000001
                              + usage.get("completion_tokens", 0) * 0.000005, 6),
            }
    except Exception as exc:
        return {"content": "", "error": str(exc)}


def reason(mode=None, question=None):
    """Основная функция: собирает контекст + вызывает LLM."""
    api_key, base_url = get_api_creds()
    if not api_key:
        return {"error": "No API key. Set OPENROUTER_API_KEY in .env"}

    context = gather_system_context()
    context_str = json.dumps(context, indent=2, ensure_ascii=False, default=str)

    if question:
        user_prompt = f"Контекст системы:\n```json\n{context_str}\n```\n\nВопрос: {question}"
    elif mode and mode in MODES:
        user_prompt = f"Контекст системы:\n```json\n{context_str}\n```\n\n{MODES[mode]['prompt']}"
    else:
        user_prompt = f"Контекст системы:\n```json\n{context_str}\n```\n\nДай краткий обзор состояния системы."

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_prompt},
    ]

    return call_llm(api_key, base_url, messages)


def main():
    args = sys.argv[1:]

    print("\n" + "=" * 60)
    print("  🧠 LLM REASONER — Phase 13 Agent #44")
    print("=" * 60)

    # Parse mode
    mode = None
    question = None

    if "--mode" in args:
        idx = args.index("--mode")
        if idx + 1 < len(args):
            mode = args[idx + 1]

    if "--ask" in args:
        idx = args.index("--ask")
        question = " ".join(args[idx + 1:])

    if mode:
        mode_info = MODES.get(mode, {})
        print(f"\n  📋 Режим: {mode} — {mode_info.get('description', 'unknown')}")
    elif question:
        print(f"\n  ❓ Вопрос: {question}")
    else:
        print("\n  📋 Режим: обзор системы")

    print("\n  🔄 Вызываю LLM...", flush=True)

    result = reason(mode=mode, question=question)

    if result.get("error"):
        print(f"\n  ❌ Ошибка: {result['error']}")
        return

    print(f"\n  ✅ Модель: {result.get('model', 'unknown')}")
    print(f"  📊 Токены: {result.get('tokens_in', 0)} → {result.get('tokens_out', 0)}")
    print(f"  💰 Стоимость: ${result.get('cost', 0):.4f}")

    print("\n  ─── Ответ ───")
    content = result.get("content", "")
    for line in content.split("\n"):
        print(f"  {line}")
    print("  ─── Конец ───")

    if "--save" in args:
        EVOLUTION_DIR.mkdir(parents=True, exist_ok=True)
        log_path = EVOLUTION_DIR / "llm_log.json"
        history = []
        if log_path.exists():
            try:
                history = json.loads(log_path.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError):
                history = []

        history.append({
            "timestamp": datetime.now().isoformat(),
            "mode": mode,
            "question": question,
            "response": content[:500],
            "tokens_in": result.get("tokens_in", 0),
            "tokens_out": result.get("tokens_out", 0),
            "cost": result.get("cost", 0),
        })
        history = history[-50:]  # Keep 50

        log_path.write_text(json.dumps(history, indent=2, ensure_ascii=False),
                            encoding="utf-8")
        print(f"\n  💾 Сохранено: {log_path}")

    print("\n" + "=" * 60 + "\n")


if __name__ == "__main__":
    main()
