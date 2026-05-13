import subprocess

SERVERS = [
    "83.147.192.178",  # Onyx2
]

BASH_SCRIPT = """
echo "--- Top CPU processes ---"
ps -eo pid,pcpu,comm,args --sort=-pcpu | head -n 5

echo "\n--- Systemd services ---"
systemctl list-units --type=service --state=running | grep -i -E 'miner|xmrig|monero'
"""

for ip in SERVERS:
    print(f"\n📡 Connecting to {ip}...")
    result = subprocess.run(
        ["ssh", "-p", "2222", f"root@{ip}", BASH_SCRIPT],
        capture_output=True, text=True
    )
    print(result.stdout)
    if result.stderr:
        print("ERR:", result.stderr)
