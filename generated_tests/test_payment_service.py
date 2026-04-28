import pytest
import asyncio
from unittest.mock import AsyncMock, patch
from aiogram.types import LabeledPrice
from app.config import settings
from app.services.payment_service import (
    create_invoice_link, 
    get_plan_title, 
    get_plan_description,
    PLAN_TITLES,
    PLAN_DESCRIPTIONS
)

@pytest.fixture
def mock_bot():
    bot = AsyncMock()
    bot.create_invoice_link = AsyncMock()
    return bot

@pytest.mark.asyncio
async def test_create_invoice_link_happy_path(mock_bot):
    """
    Test successful invoice link creation with default parameters
    """
    # Arrange
    mock_bot.create_invoice_link.return_value = "https://t.me/invoice/test"
    title = "Test Invoice"
    description = "Test Description"
    payload = "test_payload"
    amount = 10000  # 100.00 RUB
    
    # Act
    result = await create_invoice_link(
        mock_bot, 
        title=title, 
        description=description, 
        payload=payload, 
        amount=amount
    )
    
    # Assert
    assert result == "https://t.me/invoice/test"
    mock_bot.create_invoice_link.assert_called_once_with(
        title=title,
        description=description,
        payload=payload,
        provider_token=settings.payment_provider_token,
        currency="RUB",
        prices=[LabeledPrice(label=title, amount=amount)]
    )

@pytest.mark.asyncio
async def test_create_invoice_link_stars_currency(mock_bot):
    """
    Test invoice link creation with Stars (XTR) currency
    """
    # Arrange
    mock_bot.create_invoice_link.return_value = "https://t.me/invoice/stars"
    title = "Stars Invoice"
    description = "Stars Description"
    payload = "stars_payload"
    amount = 100  # 100 Stars
    
    # Act
    result = await create_invoice_link(
        mock_bot, 
        title=title, 
        description=description, 
        payload=payload, 
        amount=amount,
        currency="XTR",
        provider_token=""
    )
    
    # Assert
    assert result == "https://t.me/invoice/stars"
    mock_bot.create_invoice_link.assert_called_once_with(
        title=title,
        description=description,
        payload=payload,
        provider_token="",
        currency="XTR",
        prices=[LabeledPrice(label=title, amount=amount)]
    )

@pytest.mark.asyncio
async def test_create_invoice_link_timeout(mock_bot):
    """
    Test invoice link creation timeout scenario
    """
    # Arrange
    mock_bot.create_invoice_link.side_effect = asyncio.TimeoutError()
    
    # Act & Assert
    with pytest.raises(Exception, match="Платёжная система не отвечает"):
        await create_invoice_link(
            mock_bot, 
            title="Timeout Test", 
            description="Timeout Description", 
            payload="timeout_payload", 
            amount=5000
        )

@pytest.mark.parametrize("plan_id,expected_title", [
    ("vpn-trial", "VPN Пробный (24ч)"),
    ("ai-pro", "AI Ассистент Pro"),
    ("unknown-plan", "ONYX — unknown-plan")
])
def test_get_plan_title(plan_id, expected_title):
    """
    Test plan title retrieval with various scenarios
    """
    assert get_plan_title(plan_id) == expected_title

@pytest.mark.parametrize("plan_id,expected_description", [
    ("vpn-lite", "VLESS + Reality VPN. Безлимитный трафик, 1 месяц."),
    ("proxy-pack5", "5 приватных прокси с ротацией."),
    ("unknown-plan", "Цифровой сервис ONYX")
])
def test_get_plan_description(plan_id, expected_description):
    """
    Test plan description retrieval with various scenarios
    """
    assert get_plan_description(plan_id) == expected_description

def test_plan_titles_consistency():
    """
    Verify that all plan titles are defined
    """
    assert len(PLAN_TITLES) > 0
    for plan_id in PLAN_TITLES:
        assert isinstance(PLAN_TITLES[plan_id], str)
        assert len(PLAN_TITLES[plan_id]) > 0

def test_plan_descriptions_consistency():
    """
    Verify that all plan descriptions are defined
    """
    assert len(PLAN_DESCRIPTIONS) > 0
    for plan_id in PLAN_DESCRIPTIONS:
        assert isinstance(PLAN_DESCRIPTIONS[plan_id], str)
        assert len(PLAN_DESCRIPTIONS[plan_id]) > 0