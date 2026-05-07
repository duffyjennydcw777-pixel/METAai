#!/bin/bash
# Deploy payment-service as systemd service
set -e

echo "=== Stopping nohup process ==="
pkill -f 'payment_service/venv/bin/python3 main.py' 2>/dev/null || true
sleep 2

echo "=== Installing systemd unit ==="
cp /root/payment_service/payment-service.service /etc/systemd/system/payment-service.service
systemctl daemon-reload
systemctl enable payment-service
systemctl start payment-service
sleep 3

echo "=== Status ==="
systemctl status payment-service --no-pager

echo "=== Health check ==="
curl -s http://localhost:8002/health
echo ""
echo "=== DONE ==="
