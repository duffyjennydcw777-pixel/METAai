"""
ONYX Infrastructure Full Audit v2 — SCP bash script to each server, run, collect.
"""
import subprocess
import os
from datetime import datetime

SERVERS = [
    {"name": "Production (BOT+API)", "ip": "92.246.137.35", "port": 2222},
    {"name": "Iron (VPN Legacy)", "ip": "62.60.229.187", "port": 2222},
    {"name": "Onyx2 (VPN Primary)", "ip": "83.147.192.178", "port": 2222},
    {"name": "ForgeBot", "ip": "193.233.210.152", "port": 2222},
    {"name": "Onyx3", "ip": "193.233.138.146", "port": 2222},
    {"name": "Sylectus (Hetzner)", "ip": "65.109.58.108", "port": 22},
]

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
AUDIT_SH = os.path.join(SCRIPT_DIR, "audit.sh")

def run(cmd, timeout=30):
    try:
        r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
        return r.stdout, r.stderr
    except subprocess.TimeoutExpired:
        return "", "TIMEOUT"
    except Exception as e:
        return "", str(e)

def parse(output, section):
    try:
        marker = f"==={section}==="
        start = output.index(marker) + len(marker)
        end = output.index("===", start)
        return output[start:end].strip()
    except (ValueError, IndexError):
        return "N/A"

def main():
    report = ["# 🖥️ ONYX Infrastructure Audit Report", f"> Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n"]
    
    for s in SERVERS:
        ip, port, name = s["ip"], s["port"], s["name"]
        print(f"[*] {name} ({ip}:{port})...")
        
        # SCP audit script
        scp_out, scp_err = run(f'scp -o ConnectTimeout=10 -P {port} "{AUDIT_SH}" root@{ip}:/tmp/audit.sh', timeout=15)
        if "TIMEOUT" in scp_err:
            report.append(f"\n---\n## {name}\n**IP:** `{ip}` | ⚠️ **UNREACHABLE** (timeout)\n")
            print("  ⚠️ TIMEOUT")
            continue
        
        # Run audit script
        out, err = run(f'ssh -o ConnectTimeout=10 -p {port} root@{ip} "bash /tmp/audit.sh"', timeout=30)
        
        if not out.strip():
            report.append(f"\n---\n## {name}\n**IP:** `{ip}` | ⚠️ **NO OUTPUT** (err: {err[:100]})\n")
            print("  ⚠️ NO OUTPUT")
            continue
        
        hostname = parse(out, "HOSTNAME")
        uptime_s = parse(out, "UPTIME")
        os_info = parse(out, "OS")
        kernel = parse(out, "KERNEL")
        cpu = parse(out, "CPU")
        ram = parse(out, "RAM")
        disk = parse(out, "DISK")
        services = parse(out, "SERVICES")
        docker = parse(out, "DOCKER")
        ports_s = parse(out, "LISTENING_PORTS")
        databases = parse(out, "DATABASES")
        envfiles = parse(out, "ENVFILES")
        optdir = parse(out, "OPTDIR")
        systemd = parse(out, "SYSTEMD_CUSTOM")
        xui = parse(out, "XUI")
        xray = parse(out, "XRAY")
        crontab = parse(out, "CRONTAB")
        ufw = parse(out, "UFW")
        postgres = parse(out, "POSTGRES")
        
        os_line = os_info.splitlines()[0] if os_info != "N/A" else "N/A"
        
        r = []
        r.append(f"\n---\n## {name}")
        r.append(f"**IP:** `{ip}` | **SSH Port:** `{port}` | **Hostname:** `{hostname}`\n")
        r.append("| Metric | Value |")
        r.append("|--------|-------|")
        r.append(f"| OS | {os_line} |")
        r.append(f"| Kernel | {kernel} |")
        r.append(f"| CPU | {cpu} cores |")
        r.append(f"| RAM | {ram.replace(chr(10), ' ')} |")
        r.append(f"| Disk | {disk} |")
        r.append(f"| Uptime | {uptime_s} |")
        r.append(f"| PostgreSQL | {postgres} |")
        r.append("")
        
        r.append(f"### Services\n```\n{services}\n```")
        
        if docker != "no docker" and docker != "N/A":
            r.append(f"\n### Docker\n```\n{docker}\n```")
        
        r.append(f"\n### Ports\n```\n{ports_s}\n```")
        
        if databases != "N/A":
            r.append(f"\n### Databases\n```\n{databases}\n```")
        
        if envfiles != "N/A":
            r.append(f"\n### .env Files\n```\n{envfiles}\n```")
        
        r.append(f"\n### /opt/\n```\n{optdir}\n```")
        r.append(f"\n### Systemd\n```\n{systemd}\n```")
        
        if xui != "no x-ui" and xui != "N/A":
            r.append(f"\n### X-UI\n```\n{xui}\n```")
        
        if xray != "no xray" and xray != "N/A":
            r.append(f"\n### Xray\n```\n{xray}\n```")
        
        if crontab != "no crontab" and crontab != "N/A":
            r.append(f"\n### Crontab\n```\n{crontab}\n```")
        
        r.append(f"\n### UFW\n```\n{ufw}\n```")
        
        report.extend(r)
        print("  ✅ Done")
    
    text = "\n".join(report)
    out_path = os.path.join(SCRIPT_DIR, "server_audit_report.md")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(text)
    print(f"\n✅ Saved to {out_path}")

if __name__ == "__main__":
    main()
