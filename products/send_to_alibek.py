"""Send Alibek Full Kit to Telegram @aivengo23."""
import httpx
from pathlib import Path

BOT_TOKEN = "8525390738:AAHNw4NkMLWz4qPMNAMPwtNc_0uGvhJsCxA"
CHAT_ID = 5930391280  # @aivengo23

ZIP_PATH = Path(__file__).parent / "dist" / "alibek-full-kit-v1.0.zip"

CAPTION = """🚀 Алибек, салам!

Это полный Vibecoding Kit от дяди Георгия — SoloCTO OS + всё метаинженерное.

📦 Внутри:
• 00-setup/ — установка среды (НАЧНИ СЮДА)
• agent-rules/ — AI-правила для проектов
• agent-pipeline/ — мульти-агентный код-ревью
• vault/ — Second Brain для Obsidian
• Научная аналитика кода (Entropy, Pareto, Bayes)

👉 Открой 00-setup/INSTALL_GUIDE.md — установка за 30 мин
👉 Потом 00-setup/CAPABILITIES.html — презентация в браузере

Пиши если что! 💪"""


def send():
    if not CHAT_ID:
        print("❌ Укажи CHAT_ID! Запусти: python find_chat_id.py")
        return
    if not ZIP_PATH.exists():
        print("❌ ZIP не найден. Запусти: python build_alibek_kit.py")
        return

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendDocument"
    with open(ZIP_PATH, "rb") as f:
        resp = httpx.post(
            url,
            data={"chat_id": CHAT_ID, "caption": CAPTION},
            files={"document": (ZIP_PATH.name, f, "application/zip")},
            timeout=60.0,
        )
    data = resp.json()
    if data.get("ok"):
        print(f"✅ Отправлено @aivengo23 (chat_id: {CHAT_ID})")
    else:
        print(f"❌ Ошибка: {data}")


if __name__ == "__main__":
    send()
