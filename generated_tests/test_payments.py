import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta
from app.database import User, Subscription, Payment
from app.routers.payments import (
    create_invoice, 
    resolve_plan_id, 
    activate_subscription, 
    process_successful_payment,
    CreateInvoiceRequest
)
from app.config import settings

@pytest.fixture
def mock_db():
    return AsyncMock(spec=AsyncSession)

@pytest.fixture
def mock_user():
    user = MagicMock(spec=User)
    user.id = 123
    user.referred_by = None
    return user

@pytest.fixture
def mock_bot():
    return AsyncMock()

@pytest.mark.asyncio
async def test_resolve_plan_id_direct_match():
    """Test resolving a plan ID that directly exists in PRICES"""
    assert resolve_plan_id("onyx-monthly") == "onyx-monthly"

@pytest.mark.asyncio
async def test_resolve_plan_id_alias():
    """Test resolving a plan ID using an alias"""
    assert resolve_plan_id("onyx") == "onyx-monthly"
    assert resolve_plan_id("lite") == "vpn-lite"

@pytest.mark.asyncio
async def test_resolve_plan_id_unknown():
    """Test resolving an unknown plan ID returns the original input"""
    assert resolve_plan_id("unknown-plan") == "unknown-plan"

@pytest.mark.asyncio
async def test_activate_subscription_new_subscription(mock_db, mock_user):
    """Test activating a new subscription"""
    service = "vpn"
    plan = "onyx"
    days = 30
    
    # Mock database query to return None (no existing subscription)
    mock_db.execute.return_value.scalar_one_or_none.return_value = None
    
    await activate_subscription(mock_user.id, service, plan, days, mock_db)
    
    # Verify subscription was added
    assert mock_db.add.called
    assert mock_db.commit.called

@pytest.mark.asyncio
async def test_activate_subscription_extend_existing(mock_db, mock_user):
    """Test extending an existing active subscription"""
    service = "vpn"
    plan = "onyx"
    days = 30
    
    # Create a mock existing subscription
    existing_sub = MagicMock(spec=Subscription)
    existing_sub.expires_at = datetime.utcnow() + timedelta(days=10)
    
    mock_db.execute.return_value.scalar_one_or_none.return_value = existing_sub
    
    await activate_subscription(mock_user.id, service, plan, days, mock_db)
    
    # Verify subscription was extended
    assert existing_sub.expires_at > datetime.utcnow() + timedelta(days=30)
    assert existing_sub.plan == plan
    assert mock_db.commit.called

@pytest.mark.asyncio
async def test_create_invoice_happy_path(mock_db, mock_user, mock_bot):
    """Test creating an invoice with a valid plan"""
    with patch('app.routers.payments.create_invoice_link', new_callable=AsyncMock) as mock_create_link, \
         patch('app.routers.payments.log_audit', new_callable=AsyncMock):
        
        # Prepare request
        req = CreateInvoiceRequest(plan_id="onyx-monthly")
        
        # Mock settings to use YooKassa
        with patch('app.routers.payments.settings', MagicMock(payment_provider_token="test_token")):
            # Mock bot and invoice link creation
            mock_create_link.return_value = "https://test-invoice-link"
            
            # Call the function
            result = await create_invoice(
                req, 
                MagicMock(), 
                user=mock_user, 
                db=mock_db
            )
        
        # Assertions
        assert result['invoice_link'] == "https://test-invoice-link"
        assert result['plan'] == "onyx-monthly"
        assert mock_db.add.called
        assert mock_db.commit.called

@pytest.mark.asyncio
async def test_create_invoice_rate_limited(mock_db, mock_user):
    """Test rate limiting for invoice creation"""
    # Simulate multiple rapid requests
    req = CreateInvoiceRequest(plan_id="onyx-monthly")
    
    with pytest.raises(Exception) as excinfo:
        # Simulate 6 requests in quick succession
        for _ in range(6):
            await create_invoice(
                req, 
                MagicMock(), 
                user=mock_user, 
                db=mock_db
            )
    
    assert "Too many payment requests" in str(excinfo.value)

@pytest.mark.asyncio
async def test_process_successful_payment_first_payment(mock_db, mock_user):
    """Test processing a successful payment with referral bonus"""
    # Prepare mocks
    payment = MagicMock(spec=Payment)
    payment.id = 456
    payment.status = "pending"
    
    mock_db.execute.return_value.scalar_one_or_none.side_effect = [
        payment,  # Payment query
        mock_user,  # User query
        MagicMock(scalar=lambda: 0)  # Payment count query
    ]
    
    # Mock referral scenario
    mock_user.referred_by = 789
    
    with patch('app.routers.payments.notify_admin', new_callable=AsyncMock):
        await process_successful_payment(
            mock_user.id, 
            "onyx-monthly", 
            payment.id, 
            "charge_123", 
            mock_db
        )
    
    # Verify payment was marked as paid
    assert payment.status == "paid"
    assert payment.provider_payment_id == "charge_123"
    
    # Verify database commit
    assert mock_db.commit.called

@pytest.mark.asyncio
async def test_create_invoice_unknown_plan(mock_db, mock_user):
    """Test creating an invoice with an unknown plan"""
    req = CreateInvoiceRequest(plan_id="unknown-plan")
    
    with pytest.raises(Exception) as excinfo:
        await create_invoice(
            req, 
            MagicMock(), 
            user=mock_user, 
            db=mock_db
        )
    
    assert "Unknown plan" in str(excinfo.value)