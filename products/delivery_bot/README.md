# 🤖 Delivery Bot — Solo CTO OS

Telegram бот для автоматической доставки ZIP после верификации USDT оплаты.

## Как работает

```
Покупатель → /start → инструкции
Покупатель платит USDT → берёт txid из кошелька
Покупатель → /pay <txid>
Бот → проверяет транзакцию через TronGrid API (бесплатно)
Бот → отправляет ZIP если всё ок
Ты → получаешь уведомление о продаже
```

## Настройка

### 1. Создай бота у @BotFather
```
/newbot
→ имя: Solo CTO OS
→ username: solocto_os_bot (или любой свободный)
→ скопируй токен
```

### 2. Узнай свой Telegram ID
Напиши @userinfobot — скопируй id.

### 3. Настрой .env
```bash
cp .env.example .env
# заполни BOT_TOKEN и ADMIN_CHAT_ID
```

### 4. Положи ZIP рядом с bot.py
```bash
# Скопируй ZIP из products/dist/
cp ../dist/solocto-os-pro-v1.0.zip ./
```

### 5. Установи зависимости
```bash
pip install -r requirements.txt
```

### 6. Запусти
```bash
python bot.py
```

## Деплой на VPS (Onyx)
```bash
# Скопировать на сервер
scp -P 2222 -r delivery_bot/ root@YOUR_IP:/opt/solocto-bot/

# На сервере
cd /opt/solocto-bot
pip install -r requirements.txt
cp .env.example .env
nano .env  # заполни токен и ID

# Запустить как systemd сервис
nano /etc/systemd/system/solocto-bot.service
```

### systemd unit
```ini
[Unit]
Description=Solo CTO OS Delivery Bot
After=network.target

[Service]
Type=simple
WorkingDirectory=/opt/solocto-bot
EnvironmentFile=/opt/solocto-bot/.env
ExecStart=/usr/bin/python3 bot.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
systemctl enable solocto-bot
systemctl start solocto-bot
systemctl status solocto-bot
```

## Обновление лэндинга

После создания бота — обнови ссылку в `landing/index.html`:
```html
<!-- Было: -->
<a href="https://t.me/IrattaRazma">Buy via Telegram</a>

<!-- Стало: -->
<a href="https://t.me/solocto_os_bot">Buy — Auto Delivery</a>
```

## Команды бота

| Команда | Кто | Что делает |
|---------|-----|-----------|
| `/start` | Покупатель | Инструкции по оплате |
| `/pay <txid>` | Покупатель | Верификация и доставка |
| `/check <txid>` | Только admin | Ручная проверка txid |
