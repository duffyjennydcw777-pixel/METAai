#!/bin/bash
cd /root/payment_service
pkill -f 'payment_service/venv/bin/python3 main.py' 2>/dev/null
sleep 1
nohup venv/bin/python3 main.py > payment.log 2>&1 &
sleep 5
echo "=== LOG ==="
cat payment.log
echo "=== PORT CHECK ==="
ss -tlnp | grep 8002
echo "=== PROCESS ==="
ps aux | grep 'payment_service' | grep -v grep
