import os
import httpx
from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse, JSONResponse
import uvicorn

# Load secrets from .env (two levels up from this file)
# On server: .env lives next to main.py in /root/payment_service/
# Locally: falls back two levels up to METAai/.env
_local_env = os.path.join(os.path.dirname(__file__), ".env")
_project_env = os.path.join(os.path.dirname(__file__), "..", "..", ".env")
load_dotenv(dotenv_path=_local_env if os.path.exists(_local_env) else _project_env)

API_KEY = os.environ["CRYPTOCLOUD_API_KEY"]
SHOP_ID = os.environ["CRYPTOCLOUD_SHOP_ID"]
TG_BOT_TOKEN = os.environ["TG_BOT_TOKEN"]
TG_ADMIN_ID = os.environ["TG_ADMIN_ID"]

app = FastAPI(title="Solo CTO OS Payment Service")

# Allow requests from GitHub Pages and local dev
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://duffyjennydcw777-pixel.github.io",
        "http://localhost:3000",
        "http://127.0.0.1:5500",  # Live Server (VS Code)
    ],
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

PRODUCTS = {
    "solocto": {"amount": 149.0, "name": "Solo CTO OS"},
    "promptkit": {"amount": 9.0, "name": "Prompt Kit"},
}


@app.get("/api/v1/checkout/{product_id}")
async def create_checkout(product_id: str):
    """Creates a CryptoCloud invoice and redirects the client to the payment page."""
    if product_id not in PRODUCTS:
        return JSONResponse({"error": "Product not found"}, status_code=404)

    p = PRODUCTS[product_id]
    order_id = f"{product_id}_{os.urandom(4).hex()}"

    headers = {
        "Authorization": f"Token {API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "shop_id": SHOP_ID,
        "amount": p["amount"],
        "currency": "USD",
        "order_id": order_id,
    }

    async with httpx.AsyncClient(timeout=15.0) as client:
        resp = await client.post(
            "https://api.cryptocloud.plus/v2/invoice/create",
            headers=headers,
            json=payload,
        )

    data = resp.json()

    if resp.status_code == 200 and data.get("status") == "success":
        payment_link = data["result"]["link"]
        return RedirectResponse(url=payment_link, status_code=303)

    # Log error to console for debugging
    print(f"[CryptoCloud ERROR] status={resp.status_code} body={data}")
    return JSONResponse({"error": "Failed to create invoice", "details": data}, status_code=502)


@app.post("/api/v1/webhook/cryptocloud")
async def cryptocloud_webhook(request: Request):
    """WebHook: CryptoCloud sends POST here after successful payment."""
    content_type = request.headers.get("content-type", "")

    if "application/json" in content_type:
        data = await request.json()
    else:
        form = await request.form()
        data = dict(form)

    status = data.get("status")
    order_id = data.get("order_id", "unknown")
    amount = data.get("amount", "unknown")
    customer_email = data.get("email", "Not provided")

    print(f"[Webhook] status={status} order={order_id} amount={amount}")

    if status in ["paid", "success", "completed"]:
        message = (
            f"💰 <b>НОВАЯ ПОКУПКА!</b>\n\n"
            f"🛒 Продукт: {order_id}\n"
            f"💵 Сумма: ${amount}\n"
            f"📧 Email: {customer_email}\n\n"
            f"⚠️ <i>Отправь ZIP архив клиенту!</i>"
        )
        await _send_tg(message)

    return {"status": "ok"}


@app.get("/health")
async def health():
    """Quick liveness check."""
    return {"status": "ok", "service": "payment_service"}


async def _send_tg(text: str):
    """Send Telegram notification (async, non-blocking)."""
    url = f"https://api.telegram.org/bot{TG_BOT_TOKEN}/sendMessage"
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            await client.post(url, json={
                "chat_id": TG_ADMIN_ID,
                "text": text,
                "parse_mode": "HTML",
            })
        except Exception as e:
            print(f"[TG notify error] {e}")


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8002)
