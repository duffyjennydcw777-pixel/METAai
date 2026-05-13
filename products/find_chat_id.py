"""Find Telegram chat_id by username from bot updates."""
import httpx

BOT_TOKEN = "8525390738:AAHNw4NkMLWz4qPMNAMPwtNc_0uGvhJsCxA"
TARGET_USERNAME = "aivengo23"

resp = httpx.get(f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates", timeout=10)
data = resp.json()

if not data.get("ok"):
    print(f"Error: {data}")
else:
    found = False
    for update in data.get("result", []):
        msg = update.get("message", {})
        user = msg.get("from", {})
        username = user.get("username", "")
        if username.lower() == TARGET_USERNAME.lower():
            print(f"✅ Found @{username}!")
            print(f"   chat_id: {user['id']}")
            print(f"   name: {user.get('first_name', '')} {user.get('last_name', '')}")
            found = True
            break
    if not found:
        print(f"❌ @{TARGET_USERNAME} не найден в последних сообщениях бота.")
        print("   Попроси Алибека написать /start боту: https://t.me/YourBotName")
        print("\n   Все username в updates:")
        seen = set()
        for update in data.get("result", []):
            msg = update.get("message", {})
            user = msg.get("from", {})
            un = user.get("username", "N/A")
            uid = user.get("id", "N/A")
            if uid not in seen:
                seen.add(uid)
                print(f"   - @{un} (id: {uid})")
