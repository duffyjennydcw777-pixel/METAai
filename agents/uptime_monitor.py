"""
📡 Agent #51: Uptime Monitor
Пингует серверы ONYX, проверяет HTTP статус, трекит response time.
Алертит через Telegram при даунтайме.

    python -m agents.uptime_monitor               # Проверить
    python -m agents.uptime_monitor --save        # + сохранить
"""

import json
import socket
import sys
import time
import urllib.request
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from agents.config import REPORTS_DIR

UPTIME_DIR = REPORTS_DIR / "uptime"

# ═══════════════════════════════════════════════════════════
# ONYX Infrastructure — Source of Truth
# ═══════════════════════════════════════════════════════════
SERVERS = [
    {
        "name": "Production (BOT)",
        "ip": "92.246.137.35",
        "ssh_port": 2222,
        "role": "Bot + API + DB",
        "http_checks": [
            {"url": "http://92.246.137.35:8000/health", "name": "ONYX API"},
        ],
    },
    {
        "name": "Iron VPN",
        "ip": "62.60.229.187",
        "ssh_port": 2222,
        "role": "VPN Legacy",
        "http_checks": [
            {"url": "https://62.60.229.187:2053", "name": "X-UI Panel", "verify_ssl": False},
        ],
    },
    {
        "name": "Onyx2 PRIMARY",
        "ip": "83.147.192.178",
        "ssh_port": 2222,
        "role": "VPN Primary",
        "http_checks": [
            {"url": "https://83.147.192.178:2053", "name": "X-UI Panel", "verify_ssl": False},
        ],
    },
    {
        "name": "ForgeBot",
        "ip": "193.233.210.152",
        "ssh_port": 2222,
        "role": "BotForge + VPN",
        "http_checks": [],
    },
    {
        "name": "Onyx3",
        "ip": "193.233.138.146",
        "ssh_port": 2222,
        "role": "Spare VPN",
        "http_checks": [],
    },
    {
        "name": "Sylectus (Hetzner)",
        "ip": "65.109.58.108",
        "ssh_port": 22,
        "role": "Sylectus Prod",
        "http_checks": [
            {"url": "http://65.109.58.108:8001/health", "name": "Sylectus API"},
        ],
    },
]


def check_tcp(ip, port, timeout=5):
    """TCP port check — быстрее пинга, работает на Windows."""
    start = time.time()
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((ip, port))
        elapsed = round((time.time() - start) * 1000)
        sock.close()
        return result == 0, elapsed
    except (socket.error, OSError):
        elapsed = round((time.time() - start) * 1000)
        return False, elapsed


def check_http(url, timeout=10, verify_ssl=True):
    """HTTP health check."""
    import ssl
    start = time.time()
    try:
        ctx = None
        if not verify_ssl:
            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE

        req = urllib.request.Request(url, method="GET")
        req.add_header("User-Agent", "METAai-Uptime/1.0")
        with urllib.request.urlopen(req, timeout=timeout, context=ctx) as resp:
            elapsed = round((time.time() - start) * 1000)
            return resp.status, elapsed
    except urllib.error.HTTPError as exc:
        elapsed = round((time.time() - start) * 1000)
        return exc.code, elapsed
    except Exception:
        elapsed = round((time.time() - start) * 1000)
        return 0, elapsed


def notify_telegram(message):
    """Алерт в Telegram при даунтайме."""
    try:
        from agents.telegram_reporter import get_telegram_creds, send_telegram
        token, chat_id = get_telegram_creds()
        if token and chat_id:
            send_telegram(token, chat_id, message)
    except ImportError:
        pass


def main():
    args = sys.argv[1:]
    save_md = "--save" in args

    print("\n" + "=" * 60)
    print("  📡 UPTIME MONITOR — Phase 14 Agent #51")
    print("=" * 60)

    results = []
    down_servers = []

    for server in SERVERS:
        name = server["name"]
        ip = server["ip"]
        ssh_port = server["ssh_port"]

        print(f"\n  🖥️ {name} ({ip})")

        # TCP check on SSH port
        ssh_ok, ssh_ms = check_tcp(ip, ssh_port)
        status_icon = "✅" if ssh_ok else "❌"
        print(f"    {status_icon} SSH :{ssh_port} — {ssh_ms}ms")

        # TCP check on port 443 (VPN)
        vpn_ok, vpn_ms = check_tcp(ip, 443, timeout=3)
        if vpn_ok:
            print(f"    ✅ VPN :443 — {vpn_ms}ms")
        else:
            print(f"    ⬜ VPN :443 — N/A")

        # HTTP checks
        http_results = []
        for hc in server.get("http_checks", []):
            verify = hc.get("verify_ssl", True)
            http_code, http_ms = check_http(hc["url"], verify_ssl=verify)
            http_ok = 200 <= http_code < 500
            icon = "✅" if http_ok else "❌"
            print(f"    {icon} {hc['name']} — HTTP {http_code} ({http_ms}ms)")
            http_results.append({
                "name": hc["name"],
                "url": hc["url"],
                "status": http_code,
                "ms": http_ms,
                "ok": http_ok,
            })

        server_ok = ssh_ok
        if not server_ok:
            down_servers.append(name)

        results.append({
            "name": name,
            "ip": ip,
            "role": server["role"],
            "ssh_ok": ssh_ok,
            "ssh_ms": ssh_ms,
            "vpn_ok": vpn_ok,
            "vpn_ms": vpn_ms,
            "http_checks": http_results,
            "ok": server_ok,
        })

    # Summary
    up_count = sum(1 for r in results if r["ok"])
    total = len(results)
    avg_ms = round(sum(r["ssh_ms"] for r in results if r["ssh_ok"]) / max(up_count, 1))

    print(f"\n  {'─' * 50}")
    print(f"  📊 Итог: {up_count}/{total} серверов онлайн")
    print(f"  ⚡ Средний SSH latency: {avg_ms}ms")

    if down_servers:
        alert = (
            f"🚨 METAai ALERT: Даунтайм!\n"
            f"Серверы DOWN: {', '.join(down_servers)}\n"
            f"Время: {datetime.now().strftime('%H:%M:%S')}"
        )
        print(f"\n  🚨 DOWN: {', '.join(down_servers)}")
        notify_telegram(alert)

    if save_md:
        UPTIME_DIR.mkdir(parents=True, exist_ok=True)
        report = {
            "timestamp": datetime.now().isoformat(),
            "servers_up": up_count,
            "servers_total": total,
            "avg_latency_ms": avg_ms,
            "down_servers": down_servers,
            "results": results,
        }
        report_path = UPTIME_DIR / "latest.json"
        report_path.write_text(
            json.dumps(report, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        print(f"\n  💾 Сохранено: {report_path}")

    print("\n" + "=" * 60 + "\n")


if __name__ == "__main__":
    main()
