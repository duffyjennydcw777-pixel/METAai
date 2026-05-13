"""Send Zalina Dev Kit to Telegram."""
import httpx
from pathlib import Path

BOT_TOKEN = "8525390738:AAHNw4NkMLWz4qPMNAMPwtNc_0uGvhJsCxA"
CHAT_ID = 143982729
ZIP_PATH = Path(r"C:\Users\Gigabyte\.gemini\antigravity\scratch\METAai\products\dist\zalina-dev-kit-v1.0.zip")

CAPTION = """🎁 Залина, привет!

Это персональный Dev Kit от Георгия — всё, что нужно для AI-powered разработки.

📦 Внутри 63 файла, разбитые на 5 фаз:
• Phase 1 — Фундамент (начни с этого!)
• Phase 2 — Промпт-инженерия
• Phase 3 — AI Code Review
• Phase 4 — Автоматизация
• Phase 5 — Мета-инженерия

👉 Открой README.md — там быстрый старт за 15 минут.
Самый важный файл — MAKER_PROFILE.md, заполни его первым!"""

def send():
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendDocument"
    with open(ZIP_PATH, "rb") as f:
        resp = httpx.post(
            url,
            data={"chat_id": CHAT_ID, "caption": CAPTION, "parse_mode": "HTML"},
            files={"document": (ZIP_PATH.name, f, "application/zip")},
            timeout=30.0,
        )
    data = resp.json()
    if data.get("ok"):
        print(f"✅ Отправлено Залине (chat_id: {CHAT_ID})")
    else:
        print(f"❌ Ошибка: {data}")

if __name__ == "__main__":
    send()
