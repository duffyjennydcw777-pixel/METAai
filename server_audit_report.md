# 🖥️ ONYX Infrastructure Audit Report
> Generated: 2026-05-15 20:36


---
## Production (BOT+API)
**IP:** `92.246.137.35` | **SSH Port:** `2222` | **Hostname:** `evident-scarlet.ptr.network`

| Metric | Value |
|--------|-------|
| OS | PRETTY_NAME="Ubuntu 24.04.4 LTS" |
| Kernel | 6.8.0-107-generic |
| CPU | 2 cores |
| RAM | total        used        free      shared  buff/cache   available Mem:           3.8Gi       1.6Gi       317Mi        35Mi       2.2Gi       2.2Gi |
| Disk | /dev/vda2        59G   16G   42G  28% / |
| Uptime | 17:36:31 up 24 days, 20:15,  2 users,  load average: 0.42, 0.41, 0.44 |
| PostgreSQL | active |

### Services
```
AdGuardHome.service        loaded active running AdGuard Home: Network-level blocker
  containerd.service         loaded active running containerd container runtime
  docker.service             loaded active running Docker Application Container Engine
  familyquest.service        loaded active running FamilyQuest Bot + API
  iron055-api.service        loaded active running IRON055 API
  iron055-bot.service        loaded active running IRON055 Telegram Bot
  multipathd.service         loaded active running Device-Mapper Multipath Device Controller
  nginx.service              loaded active running A high performance web server and a reverse proxy server
  onyx-backend.service       loaded active running ONYX Backend Uvicorn API
  payment-service.service    loaded active running Solo CTO OS Payment Service v2 (CryptoCloud + Auto-Delivery)
  postgresql@16-main.service loaded active running PostgreSQL Cluster 16-main
  qemu-guest-agent.service   loaded active running QEMU Guest Agent
  rsyslog.service            loaded active running System Logging Service
  solocto-bot.service        loaded active running Solo CTO OS Delivery Bot
  spot-pilot.service         loaded active running A_v12.5_SPOT_PILOT
  sylectus-bot.service       loaded active running Sylectus Bid Assistant - Telegram Bot + Scheduler
  sylectus-web.service       loaded active running Sylectus Bid Assistant - Web API
  udisks2.service            loaded active running Disk Manager
  user@0.service             loaded active running User Manager for UID 0
```

### Docker
```
NAMES     STATUS       PORTS
lifebot   Up 2 weeks
```

### Ports
```
127.0.0.54:53 users:(("systemd-resolve",pid=471,fd=17))
127.0.0.1:5432 users:(("postgres",pid=1000,fd=6))
0.0.0.0:8101 users:(("python",pid=2703492,fd=7))
0.0.0.0:8000 users:(("uvicorn",pid=1878556,fd=15))
0.0.0.0:8001 users:(("python",pid=1566999,fd=13))
0.0.0.0:8002 users:(("python3",pid=2599715,fd=6))
127.0.0.53%lo:53 users:(("systemd-resolve",pid=471,fd=15))
0.0.0.0:443 users:(("nginx",pid=2691679,fd=6),("nginx",pid=2691678,fd=6),("nginx",pid=3007,fd=6))
0.0.0.0:2222 users:(("sshd",pid=1400,fd=3),("systemd",pid=1,fd=90))
0.0.0.0:80 users:(("nginx",pid=2691679,fd=5),("nginx",pid=2691678,fd=5),("nginx",pid=3007,fd=5))
[::]:2222 users:(("sshd",pid=1400,fd=4),("systemd",pid=1,fd=98))
*:3000 users:(("AdGuardHome",pid=958,fd=10))
```

### Databases
```
/etc/x-ui/x-ui.db
/opt/AdGuardHome/data/sessions.db
/opt/sylectus/data/sylectus.db
/opt/spot_pilot/bot_state.db
/var/cache/man/uk/index.db
/var/cache/man/id/index.db
/var/cache/man/hu/index.db
/var/cache/man/sv/index.db
/var/cache/man/pt/index.db
/var/cache/man/fi/index.db
```

### .env Files
```
/opt/solocto-bot/.env
/opt/iron055/backend/.env
/opt/iron055/watchdog/.env
/opt/sylectus/.env
/opt/spot_pilot/.env
/opt/familyquest/.env
/opt/lifebot/.env
/root/payment_service/.env
```

### /opt/
```
total 40
drwxr-xr-x 10 root        root        4096 May  8 14:49 .
drwxr-xr-x 22 root        root        4096 Apr  5 15:12 ..
drwxr-xr-x  3 root        root        4096 Apr 16 22:42 AdGuardHome
drwx--x--x  4 root        root        4096 Apr  5 15:20 containerd
drwxr-xr-x  5 familyquest familyquest 4096 May  8 14:50 familyquest
drwxr-xr-x  9 iron055     iron055     4096 May  3 11:08 iron055
drwxr-xr-x  6        1001        1001 4096 May  1 13:26 lifebot
drwx------  3 root        root        4096 May  8 00:37 solocto-bot
drwxr-xr-x  5 root        root        4096 May 15 17:35 spot_pilot
drwxr-xr-x 10 www-data    www-data    4096 Apr 24 12:40 sylectus
```

### Systemd
```
/etc/systemd/system/3proxy.service
/etc/systemd/system/AdGuardHome.service
/etc/systemd/system/apt-daily.service
/etc/systemd/system/apt-daily-upgrade.service
/etc/systemd/system/dbus-org.freedesktop.resolve1.service
/etc/systemd/system/dbus-org.freedesktop.thermald.service
/etc/systemd/system/dbus-org.freedesktop.timesync1.service
/etc/systemd/system/familyquest.service
/etc/systemd/system/iron055-api.service
/etc/systemd/system/iron055-bot.service
/etc/systemd/system/iscsi.service
/etc/systemd/system/lifebot.service
/etc/systemd/system/networkd-dispatcher.service
/etc/systemd/system/onyx-backend.service
/etc/systemd/system/onyx-watchdog-daily.service
```

### X-UI
```
current panel settings as follows:
Warning: Panel is not secure with SSL
hasDefaultCredential: false
port: 2053
webBasePath: /
```

### Crontab
```
0 4 * * * cp /opt/sylectus/data/sylectus.db /var/backups/sylectus-db-$(date +\%Y\%m\%d).db 2>/dev/null; find /var/backups/ -name "sylectus-db-*.db" -mtime +7 -delete
*/5 * * * * cd /opt/sylectus && .venv/bin/python deploy/watchdog.py >> /var/log/sylectus-watchdog.log 2>&1
* * * * * /opt/iron055/backend/venv/bin/python /opt/iron055/backend/watchdog.py >> /var/log/onyx_watchdog.log 2>&1
0 5 * * 0 cd /opt/sylectus && .venv/bin/python -c "import sqlite3; c=sqlite3.connect('data/sylectus.db'); c.execute('VACUUM'); c.close(); print('VACUUM done')" >> /var/log/sylectus-watchdog.log 2>&1
```

### UFW
```
Status: active

To                         Action      From
--                         ------      ----
22                         DENY        Anywhere
```

---
## Iron (VPN Legacy)
**IP:** `62.60.229.187` | **SSH Port:** `2222` | **Hostname:** `exuberant-orange.ptr.network`

| Metric | Value |
|--------|-------|
| OS | PRETTY_NAME="Ubuntu 24.04.4 LTS" |
| Kernel | 6.8.0-107-generic |
| CPU | 2 cores |
| RAM | total        used        free      shared  buff/cache   available Mem:           3.8Gi       530Mi       2.4Gi       2.2Mi       1.2Gi       3.3Gi |
| Disk | /dev/vda2        59G  4.9G   53G   9% / |
| Uptime | 17:36:41 up 3 days, 22:47,  1 user,  load average: 0.03, 0.05, 0.07 |
| PostgreSQL | inactive
no postgres |

### Services
```
fail2ban.service            loaded active running Fail2Ban Service
  multipathd.service          loaded active running Device-Mapper Multipath Device Controller
  qemu-guest-agent.service    loaded active running QEMU Guest Agent
  rsyslog.service             loaded active running System Logging Service
  udisks2.service             loaded active running Disk Manager
  user@0.service              loaded active running User Manager for UID 0
  x-ui.service                loaded active running x-ui Service
```

### Ports
```
0.0.0.0:2222 users:(("sshd",pid=978,fd=3))
127.0.0.1:11111 users:(("xray-linux-amd6",pid=338488,fd=7))
127.0.0.53%lo:53 users:(("systemd-resolve",pid=637,fd=15))
127.0.0.1:62789 users:(("xray-linux-amd6",pid=338488,fd=3))
127.0.0.54:53 users:(("systemd-resolve",pid=637,fd=17))
*:2096 users:(("x-ui",pid=338479,fd=9))
*:2053 users:(("x-ui",pid=338479,fd=8))
[::]:2222 users:(("sshd",pid=978,fd=4))
*:443 users:(("xray-linux-amd6",pid=338488,fd=6))
```

### Databases
```
/etc/x-ui/x-ui.db
/var/cache/man/uk/index.db
/var/cache/man/id/index.db
/var/cache/man/hu/index.db
/var/cache/man/sv/index.db
/var/cache/man/pt/index.db
/var/cache/man/fi/index.db
/var/cache/man/sl/index.db
/var/cache/man/da/index.db
/var/cache/man/nl/index.db
```

### .env Files
```

```

### /opt/
```
total 8
drwxr-xr-x  2 root root 4096 Aug 27  2024 .
drwxr-xr-x 22 root root 4096 May 12 14:38 ..
```

### Systemd
```
/etc/systemd/system/apt-daily.service
/etc/systemd/system/apt-daily-upgrade.service
/etc/systemd/system/dbus-org.freedesktop.resolve1.service
/etc/systemd/system/dbus-org.freedesktop.thermald.service
/etc/systemd/system/dbus-org.freedesktop.timesync1.service
/etc/systemd/system/iscsi.service
/etc/systemd/system/networkd-dispatcher.service
/etc/systemd/system/sshd.service
/etc/systemd/system/syslog.service
/etc/systemd/system/systemd-networkd.service
/etc/systemd/system/systemd-networkd-wait-online.service
/etc/systemd/system/vmtoolsd.service
/etc/systemd/system/vpn-bot.service
/etc/systemd/system/x-ui.service
```

### X-UI
```
current panel settings as follows:
Panel is secure with SSL
hasDefaultCredential: false
port: 2053
webBasePath: /
```

### Xray
```
338488 bin/xray-linux-amd64 -c bin/config.json
```

### Crontab
```
5 13 * * * "/root/.acme.sh"/acme.sh --cron --home "/root/.acme.sh" > /dev/null
0 4 * * * systemctl restart x-ui # OOM prevention
```

### UFW
```
Status: active

To                         Action      From
--                         ------      ----
443/tcp                    ALLOW       Anywhere
```

---
## Onyx2 (VPN Primary)
**IP:** `83.147.192.178` | **SSH Port:** `2222` | **Hostname:** `onyx2.ptr.network`

| Metric | Value |
|--------|-------|
| OS | PRETTY_NAME="Ubuntu 24.04.1 LTS" |
| Kernel | 6.8.0-48-generic |
| CPU | 2 cores |
| RAM | total        used        free      shared  buff/cache   available Mem:           3.8Gi       522Mi       1.7Gi       2.2Mi       1.9Gi       3.3Gi |
| Disk | /dev/vda2        59G  4.5G   54G   8% / |
| Uptime | 17:36:52 up 24 days, 20:15,  1 user,  load average: 0.04, 0.03, 0.00 |
| PostgreSQL | inactive
no postgres |

### Services
```
multipathd.service        loaded active running Device-Mapper Multipath Device Controller
  qemu-guest-agent.service  loaded active running QEMU Guest Agent
  rsyslog.service           loaded active running System Logging Service
  udisks2.service           loaded active running Disk Manager
  user@0.service            loaded active running User Manager for UID 0
  x-ui.service              loaded active running x-ui Service
```

### Ports
```
127.0.0.1:62789 users:(("xray-linux-amd6",pid=507021,fd=3))
127.0.0.1:11111 users:(("xray-linux-amd6",pid=507021,fd=7))
*:2222 users:(("sshd",pid=33286,fd=3),("systemd",pid=1,fd=103))
*:2053 users:(("x-ui",pid=507012,fd=8))
*:2096 users:(("x-ui",pid=507012,fd=9))
*:443 users:(("xray-linux-amd6",pid=507021,fd=6))
```

### Databases
```
/etc/x-ui/x-ui.db
/var/cache/man/uk/index.db
/var/cache/man/id/index.db
/var/cache/man/hu/index.db
/var/cache/man/sv/index.db
/var/cache/man/pt/index.db
/var/cache/man/fi/index.db
/var/cache/man/sl/index.db
/var/cache/man/da/index.db
/var/cache/man/nl/index.db
```

### .env Files
```

```

### /opt/
```
total 8
drwxr-xr-x  2 root root 4096 Aug 27  2024 .
drwxr-xr-x 22 root root 4096 Apr 12 22:32 ..
```

### Systemd
```
/etc/systemd/system/apt-daily.service
/etc/systemd/system/apt-daily-upgrade.service
/etc/systemd/system/dbus-org.freedesktop.thermald.service
/etc/systemd/system/dbus-org.freedesktop.timesync1.service
/etc/systemd/system/iscsi.service
/etc/systemd/system/networkd-dispatcher.service
/etc/systemd/system/syslog.service
/etc/systemd/system/systemd-networkd.service
/etc/systemd/system/systemd-networkd-wait-online.service
/etc/systemd/system/vmtoolsd.service
/etc/systemd/system/x-ui.service
```

### X-UI
```
current panel settings as follows:
Panel is secure with SSL
hasDefaultCredential: false
port: 2053
webBasePath: /
```

### Xray
```
507021 bin/xray-linux-amd64 -c bin/config.json
```

### Crontab
```
19 20 * * * "/root/.acme.sh"/acme.sh --cron --home "/root/.acme.sh" > /dev/null
0 4 * * * systemctl restart x-ui
```

### UFW
```
Status: inactive
```

---
## ForgeBot
**IP:** `193.233.210.152` | **SSH Port:** `2222` | **Hostname:** `innocentapricot.aeza.network`

| Metric | Value |
|--------|-------|
| OS | PRETTY_NAME="Ubuntu 24.04.1 LTS" |
| Kernel | 6.8.0-48-generic |
| CPU | 2 cores |
| RAM | total        used        free      shared  buff/cache   available Mem:           3.8Gi       583Mi       2.8Gi       2.1Mi       724Mi       3.3Gi |
| Disk | /dev/vda2        59G  3.6G   55G   7% / |
| Uptime | 17:36:58 up 18 days,  5:40,  1 user,  load average: 0.00, 0.00, 0.00 |
| PostgreSQL | inactive
no postgres |

### Services
```
botforge-leads.service    loaded active running BotForge Leads Bot
  iperf3.service            loaded active running iperf3 server
  multipathd.service        loaded active running Device-Mapper Multipath Device Controller
  qemu-guest-agent.service  loaded active running QEMU Guest Agent
  rsyslog.service           loaded active running System Logging Service
  udisks2.service           loaded active running Disk Manager
  user@0.service            loaded active running User Manager for UID 0
  x-ui.service              loaded active running x-ui Service
```

### Ports
```
127.0.0.1:11111 users:(("xray-linux-amd6",pid=224527,fd=6))
127.0.0.54:53 users:(("systemd-resolve",pid=439,fd=17))
127.0.0.53%lo:53 users:(("systemd-resolve",pid=439,fd=15))
127.0.0.1:62789 users:(("xray-linux-amd6",pid=224527,fd=3))
*:5201 users:(("iperf3",pid=890,fd=3))
*:2096 users:(("x-ui",pid=224511,fd=9))
*:2053 users:(("x-ui",pid=224511,fd=8))
*:2222 users:(("sshd",pid=947,fd=3),("systemd",pid=1,fd=79))
```

### Databases
```
/etc/x-ui/x-ui.db
/opt/botforge/leads_payments.db
/opt/botforge/demo_leads.db
/var/cache/man/uk/index.db
/var/cache/man/id/index.db
/var/cache/man/hu/index.db
/var/cache/man/sv/index.db
/var/cache/man/pt/index.db
/var/cache/man/fi/index.db
/var/cache/man/sl/index.db
```

### .env Files
```
/opt/botforge/bots/leads_bot/.env
```

### /opt/
```
total 12
drwxr-xr-x  3 root     root     4096 Apr 11 14:04 .
drwxr-xr-x 22 root     root     4096 Nov  2  2024 ..
drwxr-xr-x  7 botforge botforge 4096 Apr 12 06:13 botforge
```

### Systemd
```
/etc/systemd/system/apt-daily.service
/etc/systemd/system/apt-daily-upgrade.service
/etc/systemd/system/botforge-leads.service
/etc/systemd/system/dbus-org.freedesktop.resolve1.service
/etc/systemd/system/dbus-org.freedesktop.thermald.service
/etc/systemd/system/dbus-org.freedesktop.timesync1.service
/etc/systemd/system/iscsi.service
/etc/systemd/system/networkd-dispatcher.service
/etc/systemd/system/syslog.service
/etc/systemd/system/systemd-networkd.service
/etc/systemd/system/systemd-networkd-wait-online.service
/etc/systemd/system/vmtoolsd.service
/etc/systemd/system/x-ui.service
```

### X-UI
```
current panel settings as follows:
Panel is secure with SSL
hasDefaultCredential: false
port: 2053
webBasePath: /
```

### Xray
```
224527 bin/xray-linux-amd64 -c bin/config.json
```

### Crontab
```
40 8 * * * "/root/.acme.sh"/acme.sh --cron --home "/root/.acme.sh" > /dev/null
```

### UFW
```
Status: inactive
```

---
## Onyx3
**IP:** `193.233.138.146` | **SSH Port:** `2222` | **Hostname:** `frightened-harle.ptr.network`

| Metric | Value |
|--------|-------|
| OS | PRETTY_NAME="Ubuntu 24.04.1 LTS" |
| Kernel | 6.8.0-48-generic |
| CPU | 2 cores |
| RAM | total        used        free      shared  buff/cache   available Mem:           3.8Gi       450Mi       3.0Gi       2.2Mi       594Mi       3.4Gi |
| Disk | /dev/vda2        59G  3.3G   55G   6% / |
| Uptime | 17:37:03 up 24 days, 20:15,  2 users,  load average: 0.00, 0.00, 0.00 |
| PostgreSQL | inactive
no postgres |

### Services
```
iperf3.service            loaded active running iperf3 server
  multipathd.service        loaded active running Device-Mapper Multipath Device Controller
  qemu-guest-agent.service  loaded active running QEMU Guest Agent
  rsyslog.service           loaded active running System Logging Service
  udisks2.service           loaded active running Disk Manager
  user@0.service            loaded active running User Manager for UID 0
  x-ui.service              loaded active running x-ui Service
```

### Ports
```
127.0.0.1:11111 users:(("xray-linux-amd6",pid=105274,fd=6))
0.0.0.0:2222 users:(("sshd",pid=59424,fd=3))
127.0.0.54:53 users:(("systemd-resolve",pid=432,fd=17))
127.0.0.53%lo:53 users:(("systemd-resolve",pid=432,fd=15))
127.0.0.1:62789 users:(("xray-linux-amd6",pid=105274,fd=3))
*:14987 users:(("x-ui",pid=105259,fd=8))
*:2096 users:(("x-ui",pid=105259,fd=9))
[::]:2222 users:(("sshd",pid=59424,fd=4))
*:5201 users:(("iperf3",pid=884,fd=3))
```

### Databases
```
/etc/x-ui/x-ui.db
/var/cache/man/uk/index.db
/var/cache/man/id/index.db
/var/cache/man/hu/index.db
/var/cache/man/sv/index.db
/var/cache/man/pt/index.db
/var/cache/man/fi/index.db
/var/cache/man/sl/index.db
/var/cache/man/da/index.db
/var/cache/man/nl/index.db
```

### .env Files
```

```

### /opt/
```
total 8
drwxr-xr-x  2 root root 4096 Aug 27  2024 .
drwxr-xr-x 22 root root 4096 Apr 13 13:37 ..
```

### Systemd
```
/etc/systemd/system/apt-daily.service
/etc/systemd/system/apt-daily-upgrade.service
/etc/systemd/system/dbus-org.freedesktop.resolve1.service
/etc/systemd/system/dbus-org.freedesktop.thermald.service
/etc/systemd/system/dbus-org.freedesktop.timesync1.service
/etc/systemd/system/iscsi.service
/etc/systemd/system/networkd-dispatcher.service
/etc/systemd/system/sshd.service
/etc/systemd/system/syslog.service
/etc/systemd/system/systemd-networkd.service
/etc/systemd/system/systemd-networkd-wait-online.service
/etc/systemd/system/vmtoolsd.service
/etc/systemd/system/x-ui.service
```

### X-UI
```
current panel settings as follows:
Panel is secure with SSL
hasDefaultCredential: false
port: 14987
webBasePath: /vSzEf2tN7B0ASKextj/
```

### Xray
```
105274 bin/xray-linux-amd64 -c bin/config.json
```

### Crontab
```
48 0 * * * "/root/.acme.sh"/acme.sh --cron --home "/root/.acme.sh" > /dev/null
```

### UFW
```
Status: inactive
```

---
## Sylectus (Hetzner)
**IP:** `65.109.58.108` | **SSH Port:** `22` | **Hostname:** `Ubuntu-2204-jammy-amd64-base`

| Metric | Value |
|--------|-------|
| OS | PRETTY_NAME="Ubuntu 22.04.5 LTS" |
| Kernel | 5.15.0-176-generic |
| CPU | 24 cores |
| RAM | total        used        free      shared  buff/cache   available Mem:            62Gi       5.2Gi        51Gi       1.0Mi       6.1Gi        56Gi |
| Disk | /dev/md2        906G  9.2G  850G   2% / |
| Uptime | 17:37:13 up 19 days,  3:58,  0 users,  load average: 0.00, 0.00, 0.00 |
| PostgreSQL | inactive
no postgres |

### Services
```
atd.service                 loaded active running Deferred execution scheduler
  fail2ban.service            loaded active running Fail2Ban Service
  irqbalance.service          loaded active running irqbalance daemon
  mdmonitor.service           loaded active running MD array monitor
  multipathd.service          loaded active running Device-Mapper Multipath Device Controller
  nginx.service               loaded active running A high performance web server and a reverse proxy server
  packagekit.service          loaded active running PackageKit Daemon
  rsyslog.service             loaded active running System Logging Service
  sylectus-bot.service        loaded active running Sylectus Bid Assistant - Telegram Bot + Scheduler
  sylectus-web.service        loaded active running Sylectus Bid Assistant - Web API
  user@0.service              loaded active running User Manager for UID 0
  warp-svc.service            loaded active running Cloudflare Zero Trust Client Daemon
  x-ui.service                loaded active running x-ui Service
```

### Ports
```
127.0.0.1:40000 users:(("warp-svc",pid=907,fd=644))
127.0.0.1:11111 users:(("xray-linux-amd6",pid=3391944,fd=8))
0.0.0.0:8443 users:(("nginx",pid=330060,fd=6),("nginx",pid=330059,fd=6),("nginx",pid=330058,fd=6),("nginx",pid=330057,fd=6),("nginx",pid=330056,fd=6),("nginx",pid=330055,fd=6),("nginx",pid=330054,fd=6),("nginx",pid=330053,fd=6),("nginx",pid=330052,fd=6),("nginx",pid=330051,fd=6),("nginx",pid=330050,fd=6),("nginx",pid=330049,fd=6),("nginx",pid=330048,fd=6),("nginx",pid=330047,fd=6),("nginx",pid=330046,fd=6),("nginx",pid=330045,fd=6),("nginx",pid=330044,fd=6),("nginx",pid=330043,fd=6),("nginx",pid=330042,fd=6),("nginx",pid=330041,fd=6),("nginx",pid=330040,fd=6),("nginx",pid=330039,fd=6),("nginx",pid=330038,fd=6),("nginx",pid=330037,fd=6),("nginx",pid=330035,fd=6))
127.0.0.53%lo:53 users:(("systemd-resolve",pid=894,fd=14))
127.0.0.1:62789 users:(("xray-linux-amd6",pid=3391944,fd=4))
0.0.0.0:80 users:(("nginx",pid=330060,fd=7),("nginx",pid=330059,fd=7),("nginx",pid=330058,fd=7),("nginx",pid=330057,fd=7),("nginx",pid=330056,fd=7),("nginx",pid=330055,fd=7),("nginx",pid=330054,fd=7),("nginx",pid=330053,fd=7),("nginx",pid=330052,fd=7),("nginx",pid=330051,fd=7),("nginx",pid=330050,fd=7),("nginx",pid=330049,fd=7),("nginx",pid=330048,fd=7),("nginx",pid=330047,fd=7),("nginx",pid=330046,fd=7),("nginx",pid=330045,fd=7),("nginx",pid=330044,fd=7),("nginx",pid=330043,fd=7),("nginx",pid=330042,fd=7),("nginx",pid=330041,fd=7),("nginx",pid=330040,fd=7),("nginx",pid=330039,fd=7),("nginx",pid=330038,fd=7),("nginx",pid=330037,fd=7),("nginx",pid=330035,fd=7))
0.0.0.0:22 users:(("sshd",pid=952370,fd=3))
0.0.0.0:8001 users:(("python",pid=3391258,fd=6))
*:2053 users:(("x-ui",pid=3391924,fd=9))
*:2096 users:(("x-ui",pid=3391924,fd=10))
[::]:22 users:(("sshd",pid=952370,fd=4))
*:443 users:(("xray-linux-amd6",pid=3391944,fd=7))
```

### Databases
```
/etc/x-ui/x-ui.db
/var/cache/snapd/commands.db
/var/cache/man/it/index.db
/var/cache/man/sv/index.db
/var/cache/man/ru/index.db
/var/cache/man/uk/index.db
/var/cache/man/da/index.db
/var/cache/man/id/index.db
/var/cache/man/fi/index.db
/var/cache/man/tr/index.db
```

### .env Files
```
/opt/sylectus/.env
```

### /opt/
```
total 12
drwxr-xr-x  3 root     root     4096 May 14 12:24 .
drwxr-xr-x 20 root     root     4096 Apr 13 20:20 ..
drwxr-xr-x 15 www-data www-data 4096 May  6 13:07 sylectus
```

### Systemd
```
/etc/systemd/system/dbus-org.freedesktop.resolve1.service
/etc/systemd/system/dbus-org.freedesktop.thermald.service
/etc/systemd/system/dbus-org.freedesktop.timesync1.service
/etc/systemd/system/iscsi.service
/etc/systemd/system/multipath-tools.service
/etc/systemd/system/sshd.service
/etc/systemd/system/sudo.service
/etc/systemd/system/sylectus-bot.service
/etc/systemd/system/sylectus-web.service
/etc/systemd/system/syslog.service
/etc/systemd/system/vmtoolsd.service
/etc/systemd/system/x-ui.service
```

### X-UI
```
current panel settings as follows:
Panel is secure with SSL
hasDefaultCredential: false
port: 2053
webBasePath: /YB2gwjwkQvdnKCa9Zl/
```

### Xray
```
3391944 bin/xray-linux-amd64 -c bin/config.json
```

### Crontab
```
12 4 * * * "/root/.acme.sh"/acme.sh --cron --home "/root/.acme.sh" > /dev/null
0 12 * * * cd /opt/sylectus && /opt/sylectus/venv/bin/python scripts/cron_onboarding.py >> /var/log/sylectus_onboarding.log 2>&1
```

### UFW
```
Status: inactive
```