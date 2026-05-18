"""
📧 Agent #55: Email Automator
Cold outreach, re-engagement, onboarding sequences.
Генерирует через LLM, отправка через Telegram approve.

    python -m agents.email_automator                    # Статус
    python -m agents.email_automator --save             # + сохранить
    python -m agents.email_automator --generate re-engagement
    python -m agents.email_automator --generate onboarding
    python -m agents.email_automator --generate cold-outreach
"""

import json
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from agents.config import REPORTS_DIR, EVOLUTION_DIR

EMAIL_DIR = REPORTS_DIR / "emails"

# Email sequence templates
SEQUENCES = {
    "onboarding": {
        "name": "Onboarding Sequence",
        "description": "Серия из 3 писем для новых пользователей ONYX VPN",
        "emails": [
            {"day": 0, "subject": "Добро пожаловать в ONYX! 🛡️", "goal": "Активация"},
            {"day": 3, "subject": "Настроили VPN? Вот 3 лайфхака", "goal": "Engagement"},
            {"day": 7, "subject": "Как вам ONYX? Бонус внутри", "goal": "Retention"},
        ],
    },
    "re-engagement": {
        "name": "Re-engagement Sequence",
        "description": "Возврат неактивных пользователей (30+ дней без подключения)",
        "emails": [
            {"day": 0, "subject": "Мы скучаем! 🥺 Скидка 30% на возврат", "goal": "Win-back"},
            {"day": 5, "subject": "Последний шанс: скидка сгорает через 48ч", "goal": "Urgency"},
            {"day": 10, "subject": "Что пошло не так? Помогите нам стать лучше", "goal": "Feedback"},
        ],
    },
    "cold-outreach": {
        "name": "Cold Outreach (B2B)",
        "description": "Холодные письма для потенциальных B2B клиентов",
        "emails": [
            {"day": 0, "subject": "Корпоративный VPN для вашей команды", "goal": "Introduction"},
            {"day": 3, "subject": "Re: VPN для {company}", "goal": "Follow-up"},
            {"day": 7, "subject": "Кейс: как {industry} экономит на безопасности", "goal": "Social proof"},
        ],
    },
    "upsell": {
        "name": "Upsell Sequence",
        "description": "Апгрейд с месячной на годовую подписку",
        "emails": [
            {"day": 0, "subject": "Сэкономьте 40%: годовой план ONYX", "goal": "Value prop"},
            {"day": 5, "subject": "Что включает ONYX Premium?", "goal": "Feature highlight"},
        ],
    },
}


def load_json(path):
    if Path(path).exists():
        try:
            return json.loads(Path(path).read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            pass
    return {}


def generate_email_content(sequence_type):
    """Генерирует email-контент через LLM."""
    try:
        from agents.llm_reasoner import reason
    except ImportError:
        return None, "LLM Reasoner not available"

    seq = SEQUENCES.get(sequence_type)
    if not seq:
        return None, f"Unknown sequence: {sequence_type}"

    emails_desc = "\n".join(
        f"  Email {i+1} (Day {e['day']}): Subject: \"{e['subject']}\" | Goal: {e['goal']}"
        for i, e in enumerate(seq["emails"])
    )

    prompt = (
        f"Создай email-sequence: {seq['name']}\n"
        f"Описание: {seq['description']}\n\n"
        f"Структура:\n{emails_desc}\n\n"
        "Для КАЖДОГО email напиши:\n"
        "1. subject_line (2 A/B варианта)\n"
        "2. preheader (до 100 символов)\n"
        "3. body (HTML-friendly markdown, 150-300 слов)\n"
        "4. cta_text (текст кнопки)\n"
        "5. cta_url (placeholder)\n\n"
        "Бренд: ONYX VPN — премиальный, безопасный, быстрый.\n"
        "Тон: дружелюбный, но профессиональный.\n\n"
        "Формат: JSON массив с полями: day, subject_a, subject_b, "
        "preheader, body, cta_text, cta_url"
    )

    result = reason(question=prompt)
    return result, None


def parse_email_response(content):
    """Извлекает JSON из ответа LLM."""
    try:
        start = content.find("[")
        end = content.rfind("]") + 1
        if start >= 0 and end > start:
            return json.loads(content[start:end])
    except (json.JSONDecodeError, ValueError):
        pass
    return []


def main():
    args = sys.argv[1:]
    save_md = "--save" in args

    print("\n" + "=" * 60)
    print("  📧 EMAIL AUTOMATOR — Phase 14 Agent #55")
    print("=" * 60)

    # Generate mode
    if "--generate" in args:
        idx = args.index("--generate")
        seq_type = args[idx + 1] if idx + 1 < len(args) else "onboarding"

        if seq_type not in SEQUENCES:
            print(f"\n  ⚠️ Неизвестная последовательность: {seq_type}")
            print(f"  Доступные: {', '.join(SEQUENCES.keys())}")
            print("\n" + "=" * 60 + "\n")
            return

        seq = SEQUENCES[seq_type]
        print(f"\n  📝 Генерирую: {seq['name']}")
        print(f"     {seq['description']}")
        print(f"     Писем: {len(seq['emails'])}")

        print("\n  🧠 Генерирую через LLM...")
        result, error = generate_email_content(seq_type)

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
        print(f"  ✅ Сгенерировано (${cost:.4f})")

        emails = parse_email_response(content)
        if emails:
            print(f"\n  📬 Emails ({len(emails)}):")
            for email in emails:
                day = email.get("day", "?")
                subj = email.get("subject_a", "No subject")
                cta = email.get("cta_text", "")
                print(f"\n    📩 Day {day}: {subj}")
                print(f"       CTA: [{cta}]")
                body_preview = email.get("body", "")[:100]
                print(f"       {body_preview}...")

        if save_md:
            EMAIL_DIR.mkdir(parents=True, exist_ok=True)
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            report = {
                "timestamp": datetime.now().isoformat(),
                "sequence": seq_type,
                "sequence_name": seq["name"],
                "emails": emails,
                "raw_content": content,
                "cost": cost,
                "status": "draft",
            }
            report_path = EMAIL_DIR / f"{seq_type}_{ts}.json"
            report_path.write_text(
                json.dumps(report, indent=2, ensure_ascii=False),
                encoding="utf-8",
            )
            print(f"\n  💾 Сохранено: {report_path}")
            print("  ⚠️ Статус: DRAFT — требует одобрения через /approve")

        print("\n" + "=" * 60 + "\n")
        return

    # Status mode — show all sequences
    print(f"\n  📋 Email Sequences ({len(SEQUENCES)}):")
    for key, seq in SEQUENCES.items():
        email_count = len(seq["emails"])
        print(f"\n    📧 {seq['name']} (--generate {key})")
        print(f"       {seq['description']}")
        print(f"       Писем: {email_count}")

    # Show generated drafts
    if EMAIL_DIR.exists():
        drafts = list(EMAIL_DIR.glob("*.json"))
        if drafts:
            print(f"\n  📁 Сгенерированные ({len(drafts)}):")
            for draft in sorted(drafts)[-5:]:
                data = load_json(draft)
                status = data.get("status", "?")
                name = data.get("sequence_name", draft.stem)
                icon = "✅" if status == "approved" else "📝"
                print(f"    {icon} {name} [{status}] — {draft.name}")

    print("\n" + "=" * 60 + "\n")


if __name__ == "__main__":
    main()
