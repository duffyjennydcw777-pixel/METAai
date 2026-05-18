"""
🔮 Agent #49: Opportunity Engine
Анализирует ВСЕ данные системы через LLM → генерирует идеи НОВЫХ бизнесов.

    python -m agents.opportunity_engine               # Генерировать
    python -m agents.opportunity_engine --save         # + сохранить
"""

import json
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from agents.config import (
    EVOLUTION_DIR, REPORTS_DIR,
    OPPORTUNITY_IDEAS_CACHE, MAX_IDEAS_PER_RUN,
    IDEA_MIN_SCORE_THRESHOLD,
)


def load_json(path):
    if Path(path).exists():
        try:
            return json.loads(Path(path).read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            pass
    return {}


def gather_all_data():
    """Собирает ВСЕ данные системы для LLM."""
    data = {}

    # Trends from PH and TrustMRR
    trends = load_json(REPORTS_DIR / "signals" / "trend_matches.json")
    if trends.get("matches"):
        data["hot_trends"] = [
            {"keywords": m.get("keywords", []), "match_count": m.get("match_count", 0),
             "examples": m.get("examples", [])[:3]}
            for m in trends["matches"][:10]
        ]

    # High-growth startups from feeds
    trustmrr = load_json(REPORTS_DIR / "feeds" / "trustmrr.json")
    if trustmrr.get("startups"):
        high_growth = [
            s for s in trustmrr["startups"]
            if s.get("mrr", 0) > 10000
        ][:10]
        data["high_growth_startups"] = [
            {"name": s.get("name", ""), "mrr": s.get("mrr", 0),
             "category": s.get("category", "")}
            for s in high_growth
        ]

    # ProductHunt trending
    ph = load_json(REPORTS_DIR / "feeds" / "producthunt.json")
    if ph.get("products"):
        data["ph_trending"] = [
            {"name": p.get("name", ""), "tagline": p.get("tagline", ""),
             "votes": p.get("votes", 0)}
            for p in ph["products"][:10]
        ]

    # Competitor gaps
    seo = load_json(REPORTS_DIR / "competitors" / "seo_audit.json")
    if seo.get("audits"):
        weak = [a for a in seo["audits"] if a.get("score", 10) < 6]
        data["competitor_weak_spots"] = [
            {"name": a.get("name", ""), "score": a.get("score", 0),
             "issues": a.get("issues", [])[:3]}
            for a in weak
        ]

    # Our portfolio
    portfolio = load_json(EVOLUTION_DIR / "portfolio.json")
    if portfolio.get("projects"):
        data["our_portfolio"] = [
            {"name": p["name"], "type": p.get("type", ""),
             "stage": p.get("stage", ""), "health": p.get("health", 0)}
            for p in portfolio["projects"]
        ]

    # Deal evaluations for market multiples
    deals = load_json(REPORTS_DIR / "signals" / "deal_evaluations.json")
    if deals.get("evaluations"):
        data["market_multiples"] = [
            {"name": d.get("name", ""), "multiplier": d.get("multiplier", 0),
             "mrr": d.get("mrr", 0)}
            for d in deals["evaluations"][:5]
        ]

    return data


def generate_ideas_via_llm(data):
    """Генерирует бизнес-идеи через LLM Reasoner."""
    try:
        from agents.llm_reasoner import reason
    except ImportError:
        return {"error": "LLM Reasoner not available"}

    question = (
        f"На основе следующих данных предложи {MAX_IDEAS_PER_RUN} НОВЫХ бизнес-идей.\n"
        "ВАЖНО: идеи НЕ должны быть связаны с VPN, логистикой или фермерством "
        "(это наши текущие проекты).\n\n"
        "Для каждой идеи дай:\n"
        "1. Название\n"
        "2. Описание (1 предложение)\n"
        "3. Размер рынка\n"
        "4. Time-to-MVP\n"
        "5. Почему ИМЕННО СЕЙЧАС (на основе данных)\n"
        "6. Оценка 1-10\n\n"
        "Формат: JSON массив с полями: name, description, market_size, "
        "time_to_mvp, timing_rationale, score\n\n"
        f"Данные системы:\n```json\n{json.dumps(data, indent=2, ensure_ascii=False, default=str)[:3000]}\n```"
    )

    result = reason(question=question)
    return result


def parse_llm_ideas(content):
    """Извлекает JSON из ответа LLM."""
    # Try to find JSON array in response
    ideas = []
    try:
        # Look for JSON block
        start = content.find("[")
        end = content.rfind("]") + 1
        if start >= 0 and end > start:
            raw = content[start:end]
            ideas = json.loads(raw)
    except (json.JSONDecodeError, ValueError):
        pass

    # Validate and filter
    valid = []
    for idea in ideas:
        if isinstance(idea, dict) and idea.get("name"):
            score = float(idea.get("score", 0))
            if score >= IDEA_MIN_SCORE_THRESHOLD:
                valid.append({
                    "name": idea.get("name", ""),
                    "description": idea.get("description", ""),
                    "market_size": idea.get("market_size", "Unknown"),
                    "time_to_mvp": idea.get("time_to_mvp", "Unknown"),
                    "timing_rationale": idea.get("timing_rationale", ""),
                    "score": score,
                })

    return sorted(valid, key=lambda x: -x["score"])


def main():
    args = sys.argv[1:]
    save_md = "--save" in args

    print("\n" + "=" * 60)
    print("  🔮 OPPORTUNITY ENGINE — Phase 13 Agent #49")
    print("=" * 60)

    # Gather data
    print("\n  📊 Собираю данные из всех источников...")
    data = gather_all_data()

    sources = sum(1 for v in data.values() if v)
    print(f"  ✅ Источники: {sources}")
    for key, val in data.items():
        count = len(val) if isinstance(val, list) else 1
        print(f"    📁 {key}: {count} элементов")

    if not data:
        print("\n  ⚠️ Нет данных. Запусти: python -m agents.conductor --loop --recon --evolve --save")
        return

    # Generate ideas via LLM
    print("\n  🧠 Генерирую идеи через LLM...")
    result = generate_ideas_via_llm(data)

    if result.get("error"):
        print(f"  ❌ LLM Error: {result['error']}")
        return

    content = result.get("content", "")
    cost = result.get("cost", 0)
    tokens = f"{result.get('tokens_in', 0)}→{result.get('tokens_out', 0)}"

    print(f"  ✅ LLM ответил (${cost:.4f} | {tokens})")

    # Parse ideas
    ideas = parse_llm_ideas(content)

    if not ideas:
        print("\n  ⚠️ Не удалось извлечь идеи из ответа LLM")
        print(f"  Raw response:\n  {content[:200]}")
        return

    print(f"\n  💡 Идеи ({len(ideas)}):")
    for i, idea in enumerate(ideas, 1):
        print(f"\n  {i}. 🚀 {idea['name']} [{idea['score']}/10]")
        print(f"     {idea['description']}")
        print(f"     📈 Рынок: {idea['market_size']}")
        print(f"     ⏱️ MVP: {idea['time_to_mvp']}")
        print(f"     🎯 Почему сейчас: {idea['timing_rationale']}")

    if save_md:
        EVOLUTION_DIR.mkdir(parents=True, exist_ok=True)
        output = {
            "timestamp": datetime.now().isoformat(),
            "sources_used": list(data.keys()),
            "ideas": ideas,
            "llm_cost": cost,
            "llm_tokens": tokens,
        }

        # Append to history
        history = load_json(OPPORTUNITY_IDEAS_CACHE)
        if not isinstance(history, dict):
            history = {"runs": []}
        if "runs" not in history:
            history["runs"] = []

        history["runs"].append(output)
        history["runs"] = history["runs"][-10:]  # Keep 10 runs

        Path(OPPORTUNITY_IDEAS_CACHE).write_text(
            json.dumps(history, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        print(f"\n  💾 Сохранено: {OPPORTUNITY_IDEAS_CACHE}")

    print("\n" + "=" * 60 + "\n")


if __name__ == "__main__":
    main()
