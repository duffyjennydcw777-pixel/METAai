# 📋 Solution Patterns — Библиотека проверенных решений

> AI ОБЯЗАН проверить этот файл ПЕРЕД написанием кода.
> Если есть подходящий паттерн → использовать его, а не изобретать велосипед.

---

## 🤖 Bot Commands (aiogram 3)

### PAT-001: Простой command handler
```python
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

router = Router()

@router.message(Command("mycommand"))
async def cmd_handler(message: Message):
    """Описание команды."""
    # 1. Validate (если нужно)
    # 2. Business logic (через сервис, НЕ в хендлере)
    result = await some_service.do_work(message.from_user.id)
    # 3. Response
    await message.answer(f"Результат: {result}")
```
- **Complexity**: Level 2
- **Чеклист**: [x] логика в сервисе [x] обработка ошибок [x] логирование
- **Использован в**: ONYX /start, Sylectus /subscribe

### PAT-002: Callback handler с data
```python
from aiogram import Router, F
from aiogram.types import CallbackQuery

router = Router()

@router.callback_query(F.data.startswith("action:"))
async def callback_handler(callback: CallbackQuery):
    """Handle callback с парсингом data."""
    action_data = callback.data.split(":", 1)[1]
    
    try:
        result = await service.process(action_data)
        await callback.message.edit_text(f"✅ {result}")
    except Exception as e:
        logger.error(f"Callback error: {e}")
        await callback.answer("❌ Ошибка", show_alert=True)
    finally:
        await callback.answer()  # ВСЕГДА отвечать на callback
```
- **Complexity**: Level 2
- **Важно**: `callback.answer()` ОБЯЗАТЕЛЕН, иначе "часики" крутятся вечно

---

## 🌐 API Endpoints (FastAPI)

### PAT-003: CRUD endpoint с обработкой ошибок
```python
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/api/v1")

@router.get("/items/{item_id}")
async def get_item(item_id: int, session: AsyncSession = Depends(get_session)):
    """Get item by ID."""
    item = await session.get(Item, item_id)
    if not item:
        raise HTTPException(status_code=404, detail=f"Item {item_id} not found")
    return item
```
- **Complexity**: Level 2
- **Чеклист**: [x] 404 обработка [x] DI для session [x] type hints

---

## 🗄️ Database (SQLAlchemy async)

### PAT-004: Async session factory
```python
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

engine = create_async_engine(DATABASE_URL, echo=False, pool_size=5)
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def get_session() -> AsyncSession:
    async with async_session() as session:
        yield session
```
- **Complexity**: Level 2
- **Важно**: `expire_on_commit=False` — иначе lazy load после commit крашится

### PAT-005: Alembic миграция (стандарт)
```bash
# Создать миграцию
alembic revision --autogenerate -m "add_phone_to_user"

# Применить
alembic upgrade head

# Откатить
alembic downgrade -1
```
- **Complexity**: Level 3 (production data!)
- **НИКОГДА**: create_all() в production

---

## 🚀 Deploy (systemd + VPS)

### PAT-006: systemd unit файл
```ini
[Unit]
Description=MyBot Service
After=network.target postgresql.service

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/mybot
ExecStart=/opt/mybot/.venv/bin/python -m bot.main
Restart=always
RestartSec=5
EnvironmentFile=/opt/mybot/.env

[Install]
WantedBy=multi-user.target
```
- **Complexity**: Level 2
- **После деплоя**: `chmod 600 .env && chown www-data:www-data .env`

---

## 🔄 Обновление

- При нахождении нового проверенного решения → добавить PAT-XXX
- При обнаружении что паттерн устарел → пометить DEPRECATED
- Нумерация сквозная по всем категориям
