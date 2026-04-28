# 🚀 METAai — Deploy Runbook

> Пошаговая инструкция деплоя. Заполняется при первом деплое.

## Предусловия

- [ ] SSH доступ к серверу
- [ ] `.env` синхронизирован
- [ ] Тесты пройдены локально
- [ ] CHANGELOG обновлён
- [ ] Git закоммичен и запушен

## Шаги деплоя

```bash
# 1. Подключение
# ssh root@<IP> -p 2222

# 2. Обновление кода
# cd /opt/metaai && git pull

# 3. Зависимости
# pip install -r requirements.txt

# 4. Миграции
# alembic upgrade head

# 5. Перезапуск
# systemctl restart metaai

# 6. Проверка
# systemctl status metaai
# journalctl -u metaai -f --no-pager -n 50
```

## Откат

```bash
# git log --oneline -5
# git revert <commit>
# systemctl restart metaai
```

## Post-deploy

- [ ] chmod/chown после SCP
- [ ] Проверить логи (первые 2 минуты)
- [ ] Обновить BUSINESS_METRICS в Obsidian
- [ ] Обновить CHANGELOG
