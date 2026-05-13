import subprocess

NEW_ADDRESS = "8AuEifF9aNCTzEeTwLFTXDJcEFjD2tmQsKh6Q2ewdR7Je2TBX2PDK6yXcaXFXf94EiHXZUgZr7Xwa2QJBYJ9o2gr4bTRq4z"

SERVERS = [
    "92.246.137.35",   # Production bot / Solo CTO OS
    "83.147.192.178",  # Onyx2
    "62.60.229.187",   # Iron
    "193.233.210.152", # ForgeBot
]

BASH_SCRIPT = f"""
# 1. Попробуем найти процесс майнера
PID=$(pgrep -i xmrig | head -n 1)
CONFIG_PATH=""

if [ -n "$PID" ]; then
    # Майнер запущен, ищем его рабочую папку
    DIR_PATH=$(pwdx $PID 2>/dev/null | awk '{{print $2}}')
    if [ -f "$DIR_PATH/config.json" ]; then
        CONFIG_PATH="$DIR_PATH/config.json"
    fi
fi

# 2. Если не нашли через процесс, ищем простым поиском в частых местах
if [ -z "$CONFIG_PATH" ]; then
    CONFIG_PATH=$(find /root /opt /usr/local /home -name "config.json" 2>/dev/null | xargs grep -l '"user":' 2>/dev/null | head -n 1)
fi

if [ -n "$CONFIG_PATH" ] && [ -f "$CONFIG_PATH" ]; then
    echo "Found config at $CONFIG_PATH"
    # Меняем адрес (он начинается на 4 или 8 и длинный)
    sed -i -E 's/"user": "[48][a-zA-Z0-9]{{90,}}",/"user": "{NEW_ADDRESS}",/g' "$CONFIG_PATH"
    
    # Перезапускаем сервис
    if systemctl is-active --quiet xmrig; then
        systemctl restart xmrig
    elif systemctl is-active --quiet moneroocean_miner; then
        systemctl restart moneroocean_miner
    else
        # Убиваем процесс, если он запущен без systemd, чтобы он перезапустился (если есть авторестарт)
        kill -9 $PID 2>/dev/null
    fi
    
    echo "✅ Successfully updated on $(hostname)"
else
    echo "❌ xmrig config.json not found on $(hostname)"
fi
"""

print(f"🔄 Deploying new XMR address: {NEW_ADDRESS[:10]}...")

for ip in SERVERS:
    print(f"\n📡 Connecting to {ip}...")
    try:
        result = subprocess.run(
            ["ssh", "-p", "2222", f"root@{ip}", BASH_SCRIPT],
            capture_output=True, text=True, timeout=15
        )
        if result.stdout:
            print(result.stdout.strip())
        if result.stderr and "Connection refused" not in result.stderr:
            print("Errors:", result.stderr.strip())
    except subprocess.TimeoutExpired:
        print("❌ Connection timed out.")
    except Exception as e:
        print(f"❌ Error: {e}")

print("\n🚀 All servers updated!")
