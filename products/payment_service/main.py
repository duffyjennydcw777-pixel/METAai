"""
Solo CTO OS — Unified Payment & Delivery Service v2.0

Flow:
  Landing → /pay/checkout/{product} → CryptoCloud invoice → payment
  CryptoCloud webhook → /pay/webhook/cryptocloud → auto-deliver ZIP via TG Bot
"""

import json
import logging
import os
import secrets
from pathlib import Path

import httpx
from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, RedirectResponse
import uvicorn

# ── Config ───────────────────────────────────────────────────────────────
_local_env = Path(__file__).parent / ".env"
_project_env = Path(__file__).parent.parent.parent / ".env"
load_dotenv(dotenv_path=_local_env if _local_env.exists() else _project_env)

API_KEY = os.environ["CRYPTOCLOUD_API_KEY"]
SHOP_ID = os.environ["CRYPTOCLOUD_SHOP_ID"]
TG_BOT_TOKEN = os.environ["TG_BOT_TOKEN"]
TG_ADMIN_ID = os.environ["TG_ADMIN_ID"]

# ZIP product file (lives next to main.py on server)
PRODUCT_ZIP = Path(__file__).parent / "solocto-os-pro-v1.0.zip"

# Idempotency store
PROCESSED_FILE = Path(__file__).parent / "processed_orders.json"

# Landing page URLs (GitHub Pages)
SUCCESS_URL = "https://duffyjennydcw777-pixel.github.io/solocto-os/success.html"
FAIL_URL = "https://duffyjennydcw777-pixel.github.io/solocto-os/"

logging.basicConfig(
    format="%(asctime)s [%(levelname)s] %(message)s",
    level=logging.INFO,
)
log = logging.getLogger("payment")

# ── App ──────────────────────────────────────────────────────────────────
app = FastAPI(title="Solo CTO OS Payment Service", version="2.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://duffyjennydcw777-pixel.github.io",
        "https://ironyx.tech",
        "https://api.ironyx.tech",
        "http://localhost:3000",
        "http://127.0.0.1:5500",
    ],
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

PRODUCTS = {
    "solocto": {"amount": 149.0, "name": "Solo CTO OS Pro"},
    "promptkit": {"amount": 9.0, "name": "Prompt Kit"},
}

# ── Idempotency ──────────────────────────────────────────────────────────
def _load_processed() -> set:
    if PROCESSED_FILE.exists():
        try:
            return set(json.loads(PROCESSED_FILE.read_text()))
        except (json.JSONDecodeError, TypeError):
            return set()
    return set()


def _save_processed(data: set):
    PROCESSED_FILE.write_text(json.dumps(list(data), indent=2))


# ── Checkout ─────────────────────────────────────────────────────────────
@app.get("/pay/checkout/{product_id}")
async def create_checkout(product_id: str):
    """Creates CryptoCloud invoice and redirects buyer to payment page."""
    if product_id not in PRODUCTS:
        return JSONResponse({"error": "Product not found"}, status_code=404)

    p = PRODUCTS[product_id]
    order_id = f"{product_id}_{secrets.token_hex(8)}"

    # Webhook + redirect URLs passed per-invoice (overrides dashboard settings)
    WEBHOOK_URL = "https://api.ironyx.tech/pay/webhook/cryptocloud"

    payload = {
        "shop_id": SHOP_ID,
        "amount": p["amount"],
        "currency": "USD",
        "order_id": order_id,
        "url_callback": WEBHOOK_URL,
        "url_success": SUCCESS_URL,
        "url_return": FAIL_URL,
    }

    async with httpx.AsyncClient(timeout=15.0) as client:
        resp = await client.post(
            "https://api.cryptocloud.plus/v2/invoice/create",
            headers={
                "Authorization": f"Token {API_KEY}",
                "Content-Type": "application/json",
            },
            json=payload,
        )

    data = resp.json()

    if resp.status_code == 200 and data.get("status") == "success":
        link = data["result"]["link"]
        log.info(f"Invoice created: order={order_id} product={product_id} → {link}")
        return RedirectResponse(url=link, status_code=303)

    log.error(f"CryptoCloud error: status={resp.status_code} body={data}")
    return JSONResponse(
        {"error": "Failed to create invoice", "details": data},
        status_code=502,
    )


# ── Webhook (CryptoCloud callback) ──────────────────────────────────────
@app.post("/pay/webhook/cryptocloud")
async def cryptocloud_webhook(request: Request):
    """
    CryptoCloud POSTs here after successful payment.
    Auto-delivers ZIP to admin TG (who forwards to buyer).
    Sends buyer notification if email is available.
    """
    content_type = request.headers.get("content-type", "")
    if "application/json" in content_type:
        data = await request.json()
    else:
        form = await request.form()
        data = dict(form)

    status = data.get("status")
    order_id = data.get("order_id", "unknown")
    amount = data.get("amount", "unknown")
    invoice_id = data.get("invoice_id", data.get("uuid", ""))
    email = data.get("email", "")

    log.info(f"Webhook: status={status} order={order_id} amount={amount} email={email}")

    # Idempotency — skip already processed
    processed = _load_processed()
    idempotency_key = order_id if order_id != "unknown" else invoice_id
    if idempotency_key in processed:
        log.warning(f"Duplicate webhook skipped: {idempotency_key}")
        return {"status": "ok", "note": "already_processed"}

    if status in ("paid", "success", "completed"):
        # Determine product from order_id (format: "solocto_abc123" or "promptkit_abc123")
        product_name = "Solo CTO OS Pro"
        is_full_product = True
        if order_id.startswith("promptkit"):
            product_name = "Prompt Kit"
            is_full_product = False

        # Notify admin with full details
        admin_msg = (
            f"💰 <b>НОВАЯ ПОКУПКА!</b>\n\n"
            f"🛒 Продукт: {product_name}\n"
            f"💵 Сумма: ${amount}\n"
            f"📧 Email: {email or 'не указан'}\n"
            f"🆔 Order: <code>{order_id}</code>\n"
            f"🧾 Invoice: <code>{invoice_id}</code>\n"
        )
        await _send_tg(admin_msg, chat_id=TG_ADMIN_ID)

        # Auto-deliver ZIP to admin (for forwarding)
        if is_full_product and PRODUCT_ZIP.exists():
            await _send_zip(
                chat_id=TG_ADMIN_ID,
                caption=(
                    f"📦 Auto-delivery для {email or order_id}\n"
                    f"Перешли этот файл покупателю!"
                ),
            )
        elif is_full_product:
            await _send_tg(
                f"⚠️ ZIP не найден на сервере: {PRODUCT_ZIP}\n"
                f"Отправь вручную!",
                chat_id=TG_ADMIN_ID,
            )

        # Mark as processed
        processed.add(idempotency_key)
        _save_processed(processed)

    return {"status": "ok"}


# ── Health ───────────────────────────────────────────────────────────────
@app.get("/pay/health")
@app.get("/health")
async def health():
    return {
        "status": "ok",
        "service": "payment_service",
        "version": "2.0",
        "zip_exists": PRODUCT_ZIP.exists(),
    }


# ── Spots counter (for landing page urgency) ────────────────────────────
TOTAL_LAUNCH_SPOTS = 50

@app.get("/pay/spots")
async def spots():
    """Returns remaining launch-price spots for the landing page counter."""
    processed = _load_processed()
    # Count only solocto purchases (not promptkit)
    sold = sum(1 for oid in processed if oid.startswith("solocto"))
    remaining = max(0, TOTAL_LAUNCH_SPOTS - sold)
    return {
        "total": TOTAL_LAUNCH_SPOTS,
        "sold": sold,
        "remaining": remaining,
    }


# ── Telegram helpers ─────────────────────────────────────────────────────
async def _send_tg(text: str, chat_id: str = None):
    """Send Telegram message (async, fire-and-forget)."""
    url = f"https://api.telegram.org/bot{TG_BOT_TOKEN}/sendMessage"
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            await client.post(url, json={
                "chat_id": chat_id or TG_ADMIN_ID,
                "text": text,
                "parse_mode": "HTML",
            })
        except Exception as e:
            log.error(f"TG notify error: {e}")


async def _send_zip(chat_id: str, caption: str = ""):
    """Send ZIP file via Telegram Bot API."""
    url = f"https://api.telegram.org/bot{TG_BOT_TOKEN}/sendDocument"
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            with open(PRODUCT_ZIP, "rb") as f:
                await client.post(
                    url,
                    data={
                        "chat_id": chat_id,
                        "caption": caption,
                        "parse_mode": "HTML",
                    },
                    files={"document": (PRODUCT_ZIP.name, f, "application/zip")},
                )
            log.info(f"ZIP sent to {chat_id}")
        except Exception as e:
            log.error(f"ZIP send error: {e}")


# ── Entry point ──────────────────────────────────────────────────────────
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8002)
