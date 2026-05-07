#!/bin/bash
# Deploy payment-service v2 — full redeploy
set -e

echo "=== Stopping old service ==="
systemctl stop payment-service 2>/dev/null || true
pkill -f 'payment_service/venv/bin/python3 main.py' 2>/dev/null || true
sleep 2

echo "=== Installing systemd unit ==="
cp /root/payment_service/payment-service.service /etc/systemd/system/payment-service.service
systemctl daemon-reload
systemctl enable payment-service

echo "=== Installing dependencies ==="
cd /root/payment_service
(python3 -m venv venv 2>/dev/null || true)
venv/bin/pip install fastapi uvicorn httpx python-dotenv -q

echo "=== Starting service ==="
systemctl start payment-service
sleep 3

echo "=== Status ==="
systemctl status payment-service --no-pager
echo ""
echo "=== Health ==="
curl -s http://localhost:8002/pay/health
echo ""
echo "=== DONE ==="
