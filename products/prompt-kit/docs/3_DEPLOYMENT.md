# 🚀 Deployment — Как запускать

> Инструкция деплоя. Новый человек (или AI) должен суметь задеплоить за 15 минут.

---

## Требования

- Python 3.10+ (или Node 18+)
- PostgreSQL 14+
- Linux VPS (Ubuntu 22.04 рекомендуется)

## Локальный запуск

```bash
# 1. Клонировать
git clone [URL] && cd [project]

# 2. Виртуальное окружение
python -m venv venv && source venv/bin/activate  # Linux
python -m venv venv && .\venv\Scripts\activate   # Windows

# 3. Зависимости
pip install -r requirements.txt

# 4. Окружение
cp .env.example .env
# Заполнить .env

# 5. База данных
python -c "from app.models import create_tables; create_tables()"

# 6. Запуск
python main.py
```

## Production деплой

```bash
# 1. Залить файлы
scp -P 2222 -r ./src user@IP:/opt/project/

# 2. Установить зависимости
ssh -p 2222 user@IP "cd /opt/project && pip install -r requirements.txt"

# 3. Перезапустить сервис
ssh -p 2222 user@IP "sudo systemctl restart project.service"

# 4. Проверить
ssh -p 2222 user@IP "sudo systemctl status project.service"
```

## Переменные окружения

| Переменная | Описание | Обязательная |
|-----------|----------|:------------:|
| `DATABASE_URL` | PostgreSQL connection string | ✅ |
| `BOT_TOKEN` | Telegram Bot Token | ✅ |
| `SECRET_KEY` | JWT secret | ✅ |

## Мониторинг

- Логи: `journalctl -u project.service -f`
- Health: `curl http://localhost:8000/health`
