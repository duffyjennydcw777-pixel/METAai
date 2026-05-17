@echo off
:: SSH Tunnel для PostgreSQL доступа к ONYX production
:: Запускать ПЕРЕД работой с Antigravity если нужен доступ к БД
:: PostgreSQL слушает только localhost на сервере, поэтому нужен туннель
:: v2: добавлен keepalive для стабильности

echo [*] Starting SSH tunnel to ONYX Production PostgreSQL...
echo [*] Local port 15432 -^> 92.246.137.35:5432
echo [*] Keepalive: every 30s, max 3 retries
echo [*] Press Ctrl+C to stop
echo.

ssh -N -L 15432:127.0.0.1:5432 -p 2222 -o ServerAliveInterval=30 -o ServerAliveCountMax=3 -o ExitOnForwardFailure=yes root@92.246.137.35
