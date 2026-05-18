"""
✍️ Agent #53: Content Generator
Генерирует SEO-контент, social media посты, email-рассылки
на основе трендов и competitor intel через LLM.

    python -m agents.content_generator               # Сгенерировать
    python -m agents.content_generator --save        # + сохранить
    python -m agents.content_generator --type blog   # Тип: blog/social/email
"""

import json
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from agents.config import REPORTS_DIR, PROJECTS

CONTENT_DIR = REPORTS_DIR / "content"

CONTENT_TYPES = {
    "blog": {
        "name": "SEO Blog Post",
        "prompt_template": (
            "Напиши SEO-оптимизированную статью для блога VPN-сервиса ONYX.\n"
            "Тема: {topic}\n"
            "Требования:\n"
            "- 800-1200 слов\n"
            "- H1, H2, H3 структура\n"
            "- Meta title (до 60 символов)\n"
            "- Meta description (до 160 символов)\n"
            "- 3-5 ключевых слов\n"
            "- CTA в конце\n"
            "Формат: JSON с полями: meta_title, meta_description, keywords, content"
        ),
    },
    "social": {
        "name": "Social Media Post",
        "prompt_template": (
            "Создай 5 постов для социальных сетей для {project}.\n"
            "Тренды: {trends}\n"
            "Требования:\n"
            "- Telegram канал: 1 пост (200-300 слов, markdown)\n"
            "- Twitter/X: 2 поста (до 280 символов каждый)\n"
            "- Instagram: 1 caption (до 2200 символов + хештеги)\n"
            "- LinkedIn: 1 пост (профессиональный тон)\n"
            "Формат: JSON массив с полями: platform, text, hashtags"
        ),
    },
    "email": {
        "name": "Email Campaign",
        "prompt_template": (
            "Создай email-рассылку для {project}.\n"
            "Цель: {goal}\n"
            "Требования:\n"
            "- Subject line (A/B варианты)\n"
            "- Preheader text\n"
            "- Body (HTML-friendly markdown)\n"
            "- CTA button text\n"
            "- Отписка footer\n"
            "Формат: JSON с полями: subject_a, subject_b, preheader, body, cta_text"
        ),
    },
}


def load_json(path):
    if Path(path).exists():
        try:
            return json.loads(Path(path).read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            pass
    return {}


def get_trends():
    """Собирает тренды для контента."""
    trends = []

    # ProductHunt trending
    ph = load_json(REPORTS_DIR / "feeds" / "producthunt.json")
    if ph.get("products"):
        trends.extend([p.get("name", "") for p in ph["products"][:5]])

    # Hot trends
    tm = load_json(REPORTS_DIR / "signals" / "trend_matches.json")
    if tm.get("matches"):
        for match in tm["matches"][:5]:
            keywords = match.get("keywords", [])
            trends.extend(keywords[:2])

    return trends[:10]


def get_competitor_insights():
    """Слабости конкурентов для использования в контенте."""
    seo = load_json(REPORTS_DIR / "competitors" / "seo_audit.json")
    insights = []
    if seo.get("audits"):
        for audit in seo["audits"]:
            if audit.get("score", 10) < 6:
                insights.append(f"{audit.get('name', '')}: слабый SEO ({audit.get('score', 0)}/10)")
    return insights[:5]


def generate_content(content_type, project="ONYX", topic=None, goal=None):
    """Генерирует контент через LLM."""
    try:
        from agents.llm_reasoner import reason
    except ImportError:
        return None, "LLM Reasoner not available"

    template = CONTENT_TYPES.get(content_type, CONTENT_TYPES["blog"])
    trends = get_trends()
    insights = get_competitor_insights()

    prompt = template["prompt_template"].format(
        topic=topic or "VPN безопасность в 2026 году",
        project=project,
        trends=", ".join(trends) if trends else "AI, VPN, privacy",
        goal=goal or "re-engagement неактивных пользователей",
    )

    if insights:
        prompt += f"\n\nСлабости конкурентов (используй для позиционирования):\n"
        prompt += "\n".join(f"- {i}" for i in insights)

    result = reason(question=prompt)
    return result, None


def main():
    args = sys.argv[1:]
    save_md = "--save" in args

    # Parse content type
    content_type = "blog"
    if "--type" in args:
        idx = args.index("--type")
        if idx + 1 < len(args):
            content_type = args[idx + 1]

    # Parse topic
    topic = None
    if "--topic" in args:
        idx = args.index("--topic")
        topic = " ".join(args[idx + 1:]).split("--")[0].strip()

    print("\n" + "=" * 60)
    print("  ✍️ CONTENT GENERATOR — Phase 14 Agent #53")
    print("=" * 60)

    if content_type not in CONTENT_TYPES:
        print(f"\n  ⚠️ Неизвестный тип: {content_type}")
        print(f"  Доступные: {', '.join(CONTENT_TYPES.keys())}")
        print("\n" + "=" * 60 + "\n")
        return

    ct = CONTENT_TYPES[content_type]
    print(f"\n  📝 Тип: {ct['name']}")

    # Show data sources
    trends = get_trends()
    insights = get_competitor_insights()
    print(f"  📈 Тренды: {len(trends)}")
    print(f"  🔍 Competitor insights: {len(insights)}")

    # Generate
    print(f"\n  🧠 Генерирую через LLM...")
    result, error = generate_content(content_type, topic=topic)

    if error:
        print(f"  ❌ Ошибка: {error}")
        print("\n" + "=" * 60 + "\n")
        return

    if result and result.get("error"):
        print(f"  ❌ LLM Error: {result['error']}")
        print("\n" + "=" * 60 + "\n")
        return

    content = result.get("content", "")
    cost = result.get("cost", 0)
    tokens = f"{result.get('tokens_in', 0)}→{result.get('tokens_out', 0)}"

    print(f"  ✅ Сгенерировано (${cost:.4f} | {tokens})")

    # Preview
    print(f"\n  📄 Превью:")
    for line in content.split("\n")[:20]:
        print(f"    {line}")
    if content.count("\n") > 20:
        print(f"    ... (+{content.count(chr(10)) - 20} строк)")

    if save_md:
        CONTENT_DIR.mkdir(parents=True, exist_ok=True)
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        report = {
            "timestamp": datetime.now().isoformat(),
            "type": content_type,
            "type_name": ct["name"],
            "trends_used": trends,
            "competitor_insights": insights,
            "content": content,
            "cost": cost,
            "tokens": tokens,
        }
        report_path = CONTENT_DIR / f"{content_type}_{ts}.json"
        report_path.write_text(
            json.dumps(report, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        print(f"\n  💾 Сохранено: {report_path}")

    print("\n" + "=" * 60 + "\n")


if __name__ == "__main__":
    main()
