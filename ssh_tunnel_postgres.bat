@echo off
:: SSH Tunnel для PostgreSQL доступа к ONYX production
:: Запускать ПЕРЕД работой с Antigravity если нужен доступ к БД
:: PostgreSQL слушает только localhost на сервере, поэтому нужен туннель

echo [*] Starting SSH tunnel to ONYX Production PostgreSQL...
echo [*] Local port 15432 -^> 92.246.137.35:5432
echo [*] Press Ctrl+C to stop
echo.

ssh -N -L 15432:localhost:5432 -p 2222 root@92.246.137.35
