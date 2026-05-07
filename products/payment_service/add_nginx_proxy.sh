#!/bin/bash
# Add /pay/ proxy to ironyx.tech nginx config
# Proxies https://api.ironyx.tech/pay/* → http://127.0.0.1:8002/pay/*
set -e

CONF="/etc/nginx/sites-enabled/ironyx.tech"

# Check if /pay/ block already exists
if grep -q "location /pay/" "$CONF" 2>/dev/null; then
    echo "[~] /pay/ proxy already configured in $CONF"
else
    # Insert before the closing } of the server block
    # We add the location block right before the last closing brace
    sed -i '/location \/api\//i\
    # Solo CTO OS Payment Service (port 8002)\
    location /pay/ {\
        proxy_pass http://127.0.0.1:8002;\
        proxy_set_header Host $host;\
        proxy_set_header X-Real-IP $remote_addr;\
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;\
        proxy_set_header X-Forwarded-Proto $scheme;\
    }\
' "$CONF"
    echo "[+] Added /pay/ proxy to $CONF"
fi

# Test and reload
nginx -t && systemctl reload nginx
echo "[+] Nginx reloaded OK"

# Verify
echo "=== Testing ==="
curl -s http://localhost:8002/pay/health || echo "WARNING: payment service not responding on 8002"
echo ""
echo "=== Done ==="
