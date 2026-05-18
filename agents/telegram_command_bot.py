"""
🤖 Agent #43: Telegram Command Bot
Интерактивный интерфейс METAai через Telegram.
Команды, approve/reject действий, LLM-вопросы.

    python -m agents.telegram_command_bot              # Запуск бота
    python -m agents.telegram_command_bot --once       # Одна проверка и выход
"""

import json
import os
import subprocess
import sys
import time
import urllib.request
import urllib.parse
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from agents.config import (
    REPORTS_DIR, EVOLUTION_DIR,
    APPROVAL_LOG,
)

PROJECT_ROOT = str(Path(__file__).resolve().parent.parent)


def get_telegram_creds():
    try:
        from dotenv import load_dotenv
        load_dotenv(Path(__file__).parent.parent / ".env")
    except ImportError:
        pass
    token = os.environ.get("METAAI_TELEGRAM_BOT_TOKEN", "")
    chat_id = os.environ.get("METAAI_TELEGRAM_CHAT_ID", "")
    return token, chat_id


def tg_request(token, method, data=None):
    """Вызов Telegram Bot API."""
    url = f"https://api.telegram.org/bot{token}/{method}"
    if data:
        payload = json.dumps(data).encode("utf-8")
        req = urllib.request.Request(
            url, data=payload,
            headers={"Content-Type": "application/json"},
        )
    else:
        req = urllib.request.Request(url)

    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except Exception as exc:
        return {"ok": False, "error": str(exc)}


def send_message(token, chat_id, text, reply_markup=None):
    """Отправить сообщение."""
    data = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML",
    }
    if reply_markup:
        data["reply_markup"] = reply_markup
    return tg_request(token, "sendMessage", data)


def answer_callback(token, callback_id, text=""):
    """Ответить на callback query."""
    return tg_request(token, "answerCallbackQuery", {
        "callback_query_id": callback_id,
        "text": text,
    })


def load_json(path):
    if Path(path).exists():
        try:
            return json.loads(Path(path).read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            pass
    return {}


def save_json(path, data):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(
        json.dumps(data, indent=2, ensure_ascii=False, default=str),
        encoding="utf-8",
    )


# ═══════════════════════════════════════════════════════════
# COMMAND HANDLERS
# ═══════════════════════════════════════════════════════════

def cmd_status():
    """Статус портфеля и системы."""
    portfolio = load_json(EVOLUTION_DIR / "portfolio.json")
    tuner = load_json(EVOLUTION_DIR / "tuner.json")

    lines = ["🎼 <b>METAai Status</b>", ""]

    # Portfolio
    projects = portfolio.get("projects", [])
    if projects:
        lines.append("📊 <b>Портфель:</b>")
        for p in projects:
            health_icon = "🟢" if p.get("health", 0) >= 8 else "🟡" if p.get("health", 0) >= 5 else "🔴"
            mrr = f"${p.get('mrr', 0):,}" if p.get("mrr", 0) > 0 else "—"
            lines.append(f"  {health_icon} {p['name']} | {p.get('stage', '?')} | {p.get('health', 0)}/10 | MRR: {mrr}")

    # System health
    health_pct = tuner.get("system_health_pct", 0)
    lines.append(f"\n🏥 System Health: {health_pct:.0f}%")

    # Signal noise
    metrics = tuner.get("metrics", {})
    snr = metrics.get("signal_noise", {})
    lines.append(f"📡 Signal/Noise: {snr.get('ratio', 0)} [{snr.get('quality', '?')}]")
    scrape = metrics.get("scrape_success", {})
    lines.append(f"🌐 Scrape: {scrape.get('success_rate', 0)*100:.0f}%")

    return "\n".join(lines)


def cmd_insights():
    """Топ-5 инсайтов."""
    knowledge = load_json(EVOLUTION_DIR / "knowledge.json")
    insights = knowledge.get("insights", [])
    top = sorted(insights, key=lambda x: -x.get("priority", 0))[:5]

    lines = ["🧠 <b>Топ-5 Insights</b>", ""]
    for i, ins in enumerate(top, 1):
        lines.append(
            f"{i}. [{ins.get('source', '?')}] P{ins.get('priority', 0)} "
            f"| {ins.get('text', '?')[:60]}"
        )

    return "\n".join(lines) if top else "Нет инсайтов. Запусти: /run evolve"


def cmd_deals():
    """Текущие M&A оценки."""
    deals = load_json(REPORTS_DIR / "signals" / "deal_evaluations.json")
    evaluations = deals.get("evaluations", [])

    lines = ["💰 <b>M&A Оценки</b>", ""]
    for d in evaluations[:5]:
        lines.append(
            f"• {d.get('name', '?')} — {d.get('verdict', '?')} "
            f"({d.get('total_score', 0):.1f}/10)"
        )

    return "\n".join(lines) if evaluations else "Нет оценок. Запусти: /run loop"


def cmd_competitors():
    """Конкурентная разведка."""
    seo = load_json(REPORTS_DIR / "competitors" / "seo_audit.json")
    pricing = load_json(REPORTS_DIR / "competitors" / "pricing.json")

    lines = ["🕵️ <b>Competitor Intel</b>", ""]

    audits = seo.get("audits", [])
    for a in audits[:5]:
        lines.append(f"  🔍 {a.get('name', '?')}: SEO {a.get('score', 0)}/10")

    prices = pricing.get("competitors", [])
    for p in prices[:5]:
        price_range = p.get("price_range", "?")
        lines.append(f"  💲 {p.get('name', '?')}: {price_range}")

    return "\n".join(lines) if (audits or prices) else "Нет данных. Запусти: /run recon"


def cmd_bench():
    """Последний бенчмарк."""
    bench = load_json(EVOLUTION_DIR / "benchmarks.json")
    history = bench.get("history", [])
    if not history:
        return "Нет бенчмарков. Запусти: /run evolve"

    last = history[-1]
    lines = [
        "⏱️ <b>Последний бенчмарк</b>",
        f"📅 {last.get('timestamp', '?')[:19]}",
        f"⏱ Total: {last.get('total_time', 0):.3f}s",
        f"📊 Avg: {last.get('avg_time', 0):.3f}s",
        f"✅ Success: {last.get('success_rate', 0)*100:.0f}%",
    ]
    return "\n".join(lines)


def cmd_run(phase_name, token, chat_id):
    """Запускает фазу через Conductor."""
    flag_map = {
        "all": "--save",
        "loop": "--loop --save",
        "recon": "--recon --save",
        "evolve": "--evolve --save",
        "phase1": "--phase1 --save",
        "phase12": "--phase12 --save",
        "phase13": "--phase13 --save",
    }

    flags = flag_map.get(phase_name, f"--{phase_name} --save")
    send_message(token, chat_id, f"🚀 Запускаю: conductor {flags}...")

    cmd = [sys.executable, "-m", "agents.conductor"] + flags.split()
    env = dict(os.environ)
    env["PYTHONUTF8"] = "1"
    env["PYTHONIOENCODING"] = "utf-8"

    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=300,
            cwd=PROJECT_ROOT, env=env, encoding="utf-8", errors="replace",
        )
        ok = result.returncode == 0
        icon = "✅" if ok else "❌"
        return f"{icon} Conductor {flags} завершён (exit: {result.returncode})"
    except subprocess.TimeoutExpired:
        return "⏰ Conductor timeout (5 min)"
    except Exception as exc:
        return f"❌ Ошибка: {str(exc)[:100]}"


def cmd_ask(question, token, chat_id):
    """Вызывает LLM Reasoner."""
    send_message(token, chat_id, "🧠 Думаю...")

    from agents.llm_reasoner import reason
    result = reason(question=question)

    if result.get("error"):
        return f"❌ LLM Error: {result['error']}"

    cost = result.get("cost", 0)
    tokens = f"{result.get('tokens_in', 0)}→{result.get('tokens_out', 0)}"
    content = result.get("content", "Нет ответа")

    # Telegram limit 4096 chars
    if len(content) > 3800:
        content = content[:3800] + "\n...(обрезано)"

    return f"🧠 <b>LLM Reasoner</b> (${cost:.4f} | {tokens})\n\n{content}"


# ═══════════════════════════════════════════════════════════
# APPROVAL SYSTEM
# ═══════════════════════════════════════════════════════════

def get_pending_approvals():
    """Получить pending действия из action queue."""
    actions = load_json(REPORTS_DIR / "signals" / "actions.json")
    return [a for a in actions.get("actions", []) if a.get("status") == "pending"]


def send_approval_request(token, chat_id, action):
    """Отправить запрос на approve с inline кнопками."""
    action_id = action.get("id", "unknown")
    text = (
        f"🔔 <b>Новое действие</b>\n"
        f"━━━━━━━━━━━━━━━━\n"
        f"📋 {action.get('title', 'Untitled')}\n"
        f"🎯 Приоритет: {action.get('priority', '?')}\n"
        f"📊 Источник: {action.get('source', '?')}\n"
    )

    reply_markup = {
        "inline_keyboard": [[
            {"text": "✅ Approve", "callback_data": f"approve_{action_id}"},
            {"text": "❌ Reject", "callback_data": f"reject_{action_id}"},
            {"text": "⏸ Later", "callback_data": f"later_{action_id}"},
        ]]
    }

    send_message(token, chat_id, text, reply_markup=reply_markup)


def handle_callback(token, callback_data, callback_id):
    """Обработать callback от inline кнопки."""
    parts = callback_data.split("_", 1)
    if len(parts) != 2:
        return

    action_type, action_id = parts

    # Load approvals log
    approvals = load_json(APPROVAL_LOG)
    if not isinstance(approvals, list):
        approvals = []

    approvals.append({
        "action_id": action_id,
        "decision": action_type,
        "timestamp": datetime.now().isoformat(),
    })

    save_json(APPROVAL_LOG, approvals)

    status_map = {
        "approve": "✅ Одобрено",
        "reject": "❌ Отклонено",
        "later": "⏸ Отложено",
    }

    answer_callback(token, callback_id, status_map.get(action_type, "OK"))
    return status_map.get(action_type, "OK")


# ═══════════════════════════════════════════════════════════
# MAIN LOOP
# ═══════════════════════════════════════════════════════════

def process_update(token, chat_id, update):
    """Обработать одно обновление от Telegram."""
    # Callback query (inline buttons)
    if "callback_query" in update:
        cb = update["callback_query"]
        cb_data = cb.get("data", "")
        cb_id = cb.get("id", "")
        result = handle_callback(token, cb_data, cb_id)
        if result:
            send_message(token, chat_id, result)
        return

    # Text message
    msg = update.get("message", {})
    text = msg.get("text", "").strip()
    msg_chat_id = str(msg.get("chat", {}).get("id", ""))

    # Security: only respond to our chat
    if msg_chat_id != chat_id:
        return

    if not text.startswith("/"):
        return

    # Parse command
    cmd = text.split()[0].lower()
    cmd_args = text[len(cmd):].strip()

    response = ""

    if cmd == "/status":
        response = cmd_status()
    elif cmd == "/insights":
        response = cmd_insights()
    elif cmd == "/deals":
        response = cmd_deals()
    elif cmd == "/competitors":
        response = cmd_competitors()
    elif cmd == "/bench":
        response = cmd_bench()
    elif cmd == "/run":
        phase = cmd_args or "all"
        response = cmd_run(phase, token, chat_id)
    elif cmd == "/ask":
        if not cmd_args:
            response = "Напиши вопрос: /ask Какую сделку рассмотреть?"
        else:
            response = cmd_ask(cmd_args, token, chat_id)
    elif cmd == "/approve":
        pending = get_pending_approvals()
        if pending:
            for a in pending[:3]:
                send_approval_request(token, chat_id, a)
            response = f"📋 {len(pending)} действий ожидают решения"
        else:
            response = "✅ Нет pending действий"
    elif cmd in ("/help", "/start"):
        response = (
            "🎼 <b>METAai Command Bot</b>\n\n"
            "/status — Портфель + System Health\n"
            "/insights — Топ-5 инсайтов\n"
            "/deals — M&A оценки\n"
            "/competitors — Конкурентная разведка\n"
            "/bench — Последний бенчмарк\n"
            "/run [phase] — Запустить (all/loop/recon/evolve)\n"
            "/ask [вопрос] — Спросить LLM\n"
            "/approve — Показать pending действия\n"
        )
    else:
        response = f"❓ Неизвестная команда: {cmd}\nНапиши /help"

    if response:
        send_message(token, chat_id, response)


def main():
    args = sys.argv[1:]
    once = "--once" in args

    print("\n" + "=" * 60)
    print("  🤖 TELEGRAM COMMAND BOT — Phase 13 Agent #43")
    print("=" * 60)

    token, chat_id = get_telegram_creds()
    if not token or not chat_id:
        print("  ❌ Нет Telegram credentials")
        print("  Установи METAAI_TELEGRAM_BOT_TOKEN и METAAI_TELEGRAM_CHAT_ID в .env")
        return

    print(f"  ✅ Bot token: ...{token[-6:]}")
    print(f"  👤 Chat ID: {chat_id}")

    # Delete webhook (for long polling)
    tg_request(token, "deleteWebhook")

    offset = 0
    print("  🔄 Polling..." if not once else "  🔄 Проверяю...")

    iteration = 0
    while True:
        try:
            result = tg_request(token, "getUpdates", {
                "offset": offset,
                "timeout": 30 if not once else 1,
            })

            if result.get("ok"):
                for update in result.get("result", []):
                    offset = update["update_id"] + 1
                    process_update(token, chat_id, update)

            if once:
                print("  ✅ Проверка завершена")
                break

            iteration += 1
            if iteration % 100 == 0:
                print(f"  📡 Alive ({iteration} polls, offset={offset})")

        except KeyboardInterrupt:
            print("\n  ⏹ Остановлен")
            break
        except Exception as exc:
            print(f"  ❌ Error: {exc}")
            time.sleep(5)

    print("\n" + "=" * 60 + "\n")


if __name__ == "__main__":
    main()
