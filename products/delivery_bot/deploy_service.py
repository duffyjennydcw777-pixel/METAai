import subprocess

service = """[Unit]
Description=Solo CTO OS Delivery Bot
After=network.target

[Service]
Type=simple
WorkingDirectory=/opt/solocto-bot
EnvironmentFile=/opt/solocto-bot/.env
ExecStart=/opt/solocto-bot/venv/bin/python bot.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
"""

cmds = [
    f"echo '{service}' > /etc/systemd/system/solocto-bot.service",
    "systemctl daemon-reload",
    "systemctl enable solocto-bot",
    "systemctl start solocto-bot",
    "systemctl status solocto-bot --no-pager",
]

for cmd in cmds:
    result = subprocess.run(
        ["ssh", "-p", "2222", "root@92.246.137.35", cmd],
        capture_output=True, text=True
    )
    print(f"$ {cmd}")
    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print("ERR:", result.stderr)
