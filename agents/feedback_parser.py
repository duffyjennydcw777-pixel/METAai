"""
💬 Agent #52: Feedback Parser
Парсит обратную связь клиентов из Telegram бота (через БД),
проводит sentiment analysis через LLM.

    python -m agents.feedback_parser               # Анализ
    python -m agents.feedback_parser --save        # + сохранить
"""

import json
import os
import sys
import urllib.request
from datetime import datetime, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from agents.config import REPORTS_DIR

FEEDBACK_DIR = REPORTS_DIR / "feedback"

# Telegram Bot API для получения сообщений
TELEGRAM_API = "https://api.telegram.org/bot"


def get_bot_token():
    """Получить токен бота из .env."""
    try:
        from dotenv import load_dotenv
        load_dotenv(Path(__file__).parent.parent / ".env")
    except ImportError:
        pass
    return os.environ.get("METAAI_TELEGRAM_BOT_TOKEN", "")


def get_bot_updates(token, offset=0, limit=100):
    """Получить последние сообщения боту."""
    url = f"{TELEGRAM_API}{token}/getUpdates?offset={offset}&limit={limit}&timeout=1"
    try:
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            if data.get("ok"):
                return data.get("result", [])
    except Exception:
        pass
    return []


def extract_feedback(updates):
    """Извлекает сообщения, похожие на обратную связь."""
    feedback_keywords = [
        "проблем", "не работает", "ошибк", "баг", "bug", "fix",
        "спасибо", "отлично", "круто", "супер", "класс",
        "медленно", "slow", "disconnect", "отключ",
        "не могу", "помогите", "help", "support",
        "оплат", "подписк", "ключ", "key",
        "предложени", "хочу", "можно ли", "добавьте",
    ]

    messages = []
    for update in updates:
        msg = update.get("message", {})
        text = msg.get("text", "")
        if not text or text.startswith("/"):
            continue

        # Check if message looks like feedback
        text_lower = text.lower()
        is_feedback = any(kw in text_lower for kw in feedback_keywords)

        if is_feedback or len(text) > 50:  # Long messages are likely feedback
            user = msg.get("from", {})
            messages.append({
                "text": text[:500],
                "user": user.get("first_name", "") + " " + user.get("last_name", ""),
                "username": user.get("username", ""),
                "date": datetime.fromtimestamp(msg.get("date", 0)).isoformat(),
                "chat_id": msg.get("chat", {}).get("id", 0),
            })

    return messages


def analyze_sentiment_local(messages):
    """Простой sentiment analysis без LLM (fallback)."""
    positive_words = ["спасибо", "отлично", "круто", "супер", "класс", "работает",
                      "хорошо", "great", "thanks", "awesome", "love", "perfect"]
    negative_words = ["проблем", "не работает", "ошибк", "баг", "медленно", "плохо",
                      "disconnect", "отключ", "не могу", "broken", "slow", "bug"]

    results = []
    for msg in messages:
        text_lower = msg["text"].lower()
        pos = sum(1 for w in positive_words if w in text_lower)
        neg = sum(1 for w in negative_words if w in text_lower)

        if pos > neg:
            sentiment = "positive"
        elif neg > pos:
            sentiment = "negative"
        else:
            sentiment = "neutral"

        results.append({
            **msg,
            "sentiment": sentiment,
            "pos_score": pos,
            "neg_score": neg,
        })

    return results


def analyze_sentiment_llm(messages):
    """Sentiment analysis через LLM (если доступен)."""
    try:
        from agents.llm_reasoner import reason
    except ImportError:
        return analyze_sentiment_local(messages)

    if not messages:
        return []

    # Batch analyze
    texts = "\n".join(
        f"{i+1}. [{m['user']}]: {m['text'][:200]}"
        for i, m in enumerate(messages[:20])
    )

    question = (
        "Проанализируй sentiment следующих сообщений от клиентов VPN-сервиса.\n"
        "Для каждого сообщения определи:\n"
        "1. sentiment: positive/negative/neutral\n"
        "2. category: bug/feature_request/praise/support/question\n"
        "3. priority: high/medium/low\n"
        "4. summary: 1 предложение\n\n"
        "Формат: JSON массив с полями: id, sentiment, category, priority, summary\n\n"
        f"Сообщения:\n{texts}"
    )

    result = reason(question=question)
    if result.get("error"):
        return analyze_sentiment_local(messages)

    # Parse LLM response
    content = result.get("content", "")
    try:
        start = content.find("[")
        end = content.rfind("]") + 1
        if start >= 0 and end > start:
            analysis = json.loads(content[start:end])
            for i, item in enumerate(analysis):
                if i < len(messages):
                    messages[i].update({
                        "sentiment": item.get("sentiment", "neutral"),
                        "category": item.get("category", "other"),
                        "priority": item.get("priority", "medium"),
                        "llm_summary": item.get("summary", ""),
                    })
            return messages
    except (json.JSONDecodeError, ValueError):
        pass

    return analyze_sentiment_local(messages)


def main():
    args = sys.argv[1:]
    save_md = "--save" in args
    use_llm = "--llm" in args

    print("\n" + "=" * 60)
    print("  💬 FEEDBACK PARSER — Phase 14 Agent #52")
    print("=" * 60)

    token = get_bot_token()
    if not token:
        print("\n  ⚠️ Нет METAAI_TELEGRAM_BOT_TOKEN в .env")
        print("\n" + "=" * 60 + "\n")
        return

    print(f"\n  🤖 Bot token: ...{token[-6:]}")

    # Get updates
    print("  🔄 Загружаю сообщения...")
    updates = get_bot_updates(token)
    print(f"  📨 Получено: {len(updates)} updates")

    # Extract feedback
    feedback = extract_feedback(updates)
    print(f"  💬 Обратная связь: {len(feedback)} сообщений")

    if not feedback:
        print("\n  ℹ️ Нет новой обратной связи")
        print("\n" + "=" * 60 + "\n")
        return

    # Analyze sentiment
    print("  🧠 Анализирую sentiment...")
    if use_llm:
        analyzed = analyze_sentiment_llm(feedback)
    else:
        analyzed = analyze_sentiment_local(feedback)

    # Stats
    sentiments = {"positive": 0, "negative": 0, "neutral": 0}
    for msg in analyzed:
        sentiments[msg.get("sentiment", "neutral")] += 1

    print(f"\n  📊 Результаты:")
    print(f"    😊 Positive: {sentiments['positive']}")
    print(f"    😐 Neutral:  {sentiments['neutral']}")
    print(f"    😞 Negative: {sentiments['negative']}")

    # Show top feedback
    negative = [m for m in analyzed if m.get("sentiment") == "negative"]
    if negative:
        print(f"\n  🔴 Негативные ({len(negative)}):")
        for msg in negative[:5]:
            user = msg.get("username") or msg.get("user", "")
            print(f"    [{user}] {msg['text'][:80]}")
            if msg.get("llm_summary"):
                print(f"      → {msg['llm_summary']}")

    positive = [m for m in analyzed if m.get("sentiment") == "positive"]
    if positive:
        print(f"\n  🟢 Позитивные ({len(positive)}):")
        for msg in positive[:3]:
            user = msg.get("username") or msg.get("user", "")
            print(f"    [{user}] {msg['text'][:80]}")

    if save_md:
        FEEDBACK_DIR.mkdir(parents=True, exist_ok=True)
        report = {
            "timestamp": datetime.now().isoformat(),
            "total_updates": len(updates),
            "total_feedback": len(feedback),
            "sentiments": sentiments,
            "messages": analyzed[:50],
        }
        report_path = FEEDBACK_DIR / "latest.json"
        report_path.write_text(
            json.dumps(report, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        print(f"\n  💾 Сохранено: {report_path}")

    print("\n" + "=" * 60 + "\n")


if __name__ == "__main__":
    main()
