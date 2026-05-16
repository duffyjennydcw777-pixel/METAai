#!/bin/bash
echo "===HOSTNAME==="
hostname
echo "===UPTIME==="
uptime
echo "===OS==="
cat /etc/os-release 2>/dev/null | head -4
echo "===KERNEL==="
uname -r
echo "===CPU==="
nproc
echo "===RAM==="
free -h | head -2
echo "===DISK==="
df -h / | tail -1
echo "===SERVICES==="
systemctl list-units --type=service --state=running --no-pager --no-legend 2>/dev/null | grep -vE 'getty|ssh|system|cron|dbus|network|udev|journal|login|polkit|snap|unattended|fwupd|pkg|cloud|ModemManager' | head -20
echo "===DOCKER==="
docker ps --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}' 2>/dev/null || echo "no docker"
echo "===LISTENING_PORTS==="
ss -tlnp 2>/dev/null | grep LISTEN | awk '{print $4, $6}' | head -20
echo "===DATABASES==="
find / -maxdepth 5 \( -name '*.db' -o -name '*.sqlite' \) -not -path '*/proc/*' -not -path '*/sys/*' -not -path '*/lib/*' -not -path '*/share/*' -not -path '*/containerd/*' -not -path '*/docker/*' -not -path '*/buildkit/*' 2>/dev/null | head -10
echo "===ENVFILES==="
find /opt /root -maxdepth 4 -name '.env' 2>/dev/null | head -10
echo "===OPTDIR==="
ls -la /opt/ 2>/dev/null
echo "===SYSTEMD_CUSTOM==="
ls /etc/systemd/system/*.service 2>/dev/null | grep -v wants | head -15
echo "===XUI==="
/usr/local/x-ui/x-ui setting -show 2>/dev/null || echo "no x-ui"
echo "===XRAY==="
pgrep -a xray 2>/dev/null || echo "no xray"
echo "===CRONTAB==="
crontab -l 2>/dev/null || echo "no crontab"
echo "===UFW==="
ufw status 2>/dev/null | head -5
echo "===POSTGRES==="
systemctl is-active postgresql 2>/dev/null || echo "no postgres"
echo "===END==="
