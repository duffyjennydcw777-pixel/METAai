"""
💰 Solo CTO OS — Delivery Bot v2
Zero-action payment: покупатель только платит, бот сам находит транзакцию.

Flow:
  /start → уникальная сумма (149.01, 149.02...) + адрес + QR
  Бот мониторит TronGrid каждые 30 сек
  Находит платёж → автоматически отправляет ZIP
"""

import asyncio
import json
import logging
import os
import time
from pathlib import Path

import httpx
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    CallbackQueryHandler,
)

load_dotenv()

logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# ── Config ──────────────────────────────────────────────────────────────
BOT_TOKEN = os.getenv("BOT_TOKEN", "")
USDT_ADDRESS = os.getenv("USDT_ADDRESS", "TE18CRGjhC5Woag4gKjH8VUTDaN7iDxr4W")
PRICE_BASE = float(os.getenv("PRICE_USDT", "149"))
PRODUCT_ZIP = Path(os.getenv("PRODUCT_ZIP", "solocto-os-pro-v1.0.zip"))
ADMIN_CHAT_ID = int(os.getenv("ADMIN_CHAT_ID", "0"))
PENDING_FILE = Path("pending.json")

# TRC-20 USDT Contract on mainnet
USDT_CONTRACT = "TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t"
TRONGRID_URL = "https://api.trongrid.io"

# Допустимая погрешность суммы (±$0.01)
AMOUNT_TOLERANCE = 0.015

# ── State persistence ────────────────────────────────────────────────────
def load_pending() -> dict:
    """Загружает список ожидающих покупателей {unique_amount: {chat_id, username, ts}}"""
    if PENDING_FILE.exists():
        return json.loads(PENDING_FILE.read_text())
    return {}

def save_pending(data: dict):
    PENDING_FILE.write_text(json.dumps(data, indent=2))

def load_delivered() -> set:
    p = Path("delivered.json")
    if p.exists():
        return set(json.loads(p.read_text()))
    return set()

def save_delivered(data: set):
    Path("delivered.json").write_text(json.dumps(list(data)))

# ── Unique amount generator ──────────────────────────────────────────────
def get_unique_amount(pending: dict) -> float:
    """
    Генерирует уникальную сумму 149.01, 149.02 ...
    чтобы бот точно знал кому какой платёж.
    """
    used = {float(k) for k in pending.keys()}
    cent = 1
    while True:
        amount = round(PRICE_BASE + cent * 0.01, 2)
        if amount not in used:
            return amount
        cent += 1

# ── TronGrid API ─────────────────────────────────────────────────────────
async def get_recent_usdt_transfers(hours: int = 2) -> list[dict]:
    """
    Получает входящие USDT TRC-20 транзакции на наш адрес за последние N часов.
    """
    min_ts = int((time.time() - hours * 3600) * 1000)
    url = (
        f"{TRONGRID_URL}/v1/accounts/{USDT_ADDRESS}/transactions/trc20"
        f"?contract_address={USDT_CONTRACT}&only_to=true&limit=50&min_timestamp={min_ts}"
    )
    async with httpx.AsyncClient(timeout=15) as client:
        try:
            resp = await client.get(url, headers={"Accept": "application/json"})
            if resp.status_code != 200:
                logger.warning(f"TronGrid {resp.status_code}: {resp.text[:200]}")
                return []
            data = resp.json().get("data", [])
            return data
        except Exception as e:
            logger.error(f"TronGrid error: {e}")
            return []

def parse_usdt_amount(tx: dict) -> float:
    """Парсит сумму USDT из TRC-20 транзакции."""
    try:
        value = int(tx.get("value", "0"))
        return value / 1_000_000  # 6 decimals
    except (ValueError, TypeError):
        return 0.0

# ── Delivery ─────────────────────────────────────────────────────────────
async def deliver_product(bot, chat_id: int, username: str, amount: float, tx_id: str):
    """Отправляет ZIP покупателю и уведомляет админа."""
    if not PRODUCT_ZIP.exists():
        logger.error(f"ZIP not found: {PRODUCT_ZIP}")
        await bot.send_message(
            chat_id=chat_id,
            text=(
                "✅ Оплата получена! Произошла техническая ошибка при доставке.\n"
                "Пишем тебе вручную в течение 10 минут. @IrattaRazma"
            ),
        )
        return

    await bot.send_message(
        chat_id=chat_id,
        text=f"✅ Оплата {amount:.2f} USDT получена! Отправляю продукт...",
    )

    with open(PRODUCT_ZIP, "rb") as f:
        await bot.send_document(
            chat_id=chat_id,
            document=f,
            filename=PRODUCT_ZIP.name,
            caption=(
                "🎉 *Solo CTO OS Pro v1.0*\n\n"
                "Начни с `GETTING_STARTED.md`\n\n"
                "Вопросы → @IrattaRazma\n"
                "Спасибо! ⚡"
            ),
            parse_mode="Markdown",
        )

    logger.info(f"✅ Delivered to @{username} (chat {chat_id}), amount={amount}, tx={tx_id}")

    if ADMIN_CHAT_ID:
        await bot.send_message(
            chat_id=ADMIN_CHAT_ID,
            text=(
                f"💰 *Продажа!*\n"
                f"Покупатель: @{username} (id: {chat_id})\n"
                f"Сумма: {amount:.2f} USDT\n"
                f"TX: `{tx_id}`"
            ),
            parse_mode="Markdown",
        )

# ── Background monitor ───────────────────────────────────────────────────
async def monitor_payments(app):
    """Фоновая задача: проверяет TronGrid каждые 30 сек."""
    logger.info("🔍 Payment monitor started")

    while True:
        try:
            pending = load_pending()
            delivered = load_delivered()

            if pending:
                transfers = await get_recent_usdt_transfers(hours=3)

                for tx in transfers:
                    tx_id = tx.get("transaction_id", "")
                    if tx_id in delivered:
                        continue

                    amount = parse_usdt_amount(tx)

                    # Ищем matching pending покупателя
                    for unique_amount_str, buyer in list(pending.items()):
                        unique_amount = float(unique_amount_str)
                        if abs(amount - unique_amount) <= AMOUNT_TOLERANCE:
                            chat_id = buyer["chat_id"]
                            username = buyer.get("username", "unknown")

                            # Доставляем
                            await deliver_product(app.bot, chat_id, username, amount, tx_id)

                            # Убираем из pending, добавляем в delivered
                            del pending[unique_amount_str]
                            save_pending(pending)

                            delivered.add(tx_id)
                            save_delivered(delivered)
                            break

        except Exception as e:
            logger.error(f"Monitor error: {e}")

        await asyncio.sleep(30)

# ── Handlers ─────────────────────────────────────────────────────────────
async def cmd_start(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    """Генерирует уникальный инвойс и показывает инструкции."""
    user = update.effective_user
    pending = load_pending()

    # Проверяем — может уже есть активный инвойс для этого пользователя
    for amount_str, buyer in pending.items():
        if buyer["chat_id"] == user.id:
            amount = float(amount_str)
            await _send_invoice(update, user, amount, existing=True)
            return

    # Создаём новый
    amount = get_unique_amount(pending)
    pending[str(amount)] = {
        "chat_id": user.id,
        "username": user.username or "unknown",
        "ts": int(time.time()),
    }
    save_pending(pending)

    await _send_invoice(update, user, amount, existing=False)


async def _send_invoice(update, user, amount: float, existing: bool):
    prefix = "⚠️ У тебя уже есть активный инвойс:\n\n" if existing else ""
    text = (
        f"{prefix}"
        f"👋 *Solo CTO OS Pro* — Автоматическая доставка\n\n"
        f"1️⃣ Отправь ровно *{amount:.2f} USDT* (TRC-20) на адрес:\n"
        f"`{USDT_ADDRESS}`\n\n"
        f"2️⃣ *Больше ничего не нужно* — бот проверит оплату автоматически\n\n"
        f"⏱ Обычно доставка происходит в течение 1-2 минут после подтверждения\n\n"
        f"❓ Вопросы: @IrattaRazma"
    )
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("✅ Я оплатил — проверить статус", callback_data=f"check_{amount}")],
    ])
    await update.message.reply_text(text, parse_mode="Markdown", reply_markup=keyboard)


async def callback_check(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    """Ручная проверка статуса по кнопке."""
    query = update.callback_query
    await query.answer()

    user = update.effective_user
    pending = load_pending()

    for amount_str, buyer in pending.items():
        if buyer["chat_id"] == user.id:
            await query.edit_message_text(
                f"🔍 Ищу твой платёж на {float(amount_str):.2f} USDT...\n"
                f"Проверяю блокчейн, подожди 30 секунд и нажми снова если не пришло.",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("🔄 Проверить ещё раз", callback_data=f"check_{amount_str}")
                ]])
            )
            return

    # Не найден в pending — значит уже доставлено
    await query.edit_message_text("✅ Твой заказ уже доставлен! Проверь чат выше.")


async def cmd_status(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    """Показывает статус заказа."""
    user = update.effective_user
    pending = load_pending()

    for amount_str, buyer in pending.items():
        if buyer["chat_id"] == user.id:
            elapsed = int((time.time() - buyer["ts"]) / 60)
            await update.message.reply_text(
                f"⏳ Ожидаю оплату *{float(amount_str):.2f} USDT*\n"
                f"Инвойс создан {elapsed} мин. назад\n\n"
                f"Как только платёж придёт — ZIP отправится автоматически.",
                parse_mode="Markdown",
            )
            return

    await update.message.reply_text("У тебя нет активных заказов. Напиши /start чтобы начать.")


async def cmd_admin(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    """Статистика для админа."""
    if update.effective_user.id != ADMIN_CHAT_ID:
        return
    pending = load_pending()
    delivered = load_delivered()
    text = (
        f"📊 *Статус бота*\n\n"
        f"Ожидают оплаты: {len(pending)}\n"
        f"Доставлено: {len(delivered)}\n\n"
    )
    if pending:
        text += "*Pending заказы:*\n"
        for amt, b in pending.items():
            mins = int((time.time() - b["ts"]) / 60)
            text += f"• @{b['username']} → {float(amt):.2f} USDT ({mins} мин.)\n"

    await update.message.reply_text(text, parse_mode="Markdown")

# ── Main ─────────────────────────────────────────────────────────────────
def main() -> None:
    if not BOT_TOKEN:
        raise ValueError("BOT_TOKEN не задан в .env")

    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("status", cmd_status))
    app.add_handler(CommandHandler("admin", cmd_admin))
    app.add_handler(CallbackQueryHandler(callback_check, pattern=r"^check_"))

    # Запускаем фоновый монитор
    async def post_init(application):
        asyncio.create_task(monitor_payments(application))

    app.post_init = post_init

    logger.info("🤖 Delivery Bot v2 started (auto-monitor mode)")
    logger.info(f"📦 Product: {PRODUCT_ZIP}")
    logger.info(f"💰 Base price: {PRICE_BASE} USDT → {USDT_ADDRESS}")
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
