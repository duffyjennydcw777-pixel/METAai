import pytest
from unittest.mock import AsyncMock, patch
from datetime import datetime, timedelta, timezone
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.tables import User, Subscription, PointsTransaction
from src.subscription import (
    get_plan,
    has_active_subscription,
    activate_trial,
    activate_subscription,
    get_active_subscription,
    check_and_expire_subscriptions,
    get_subscription_history,
    award_points,
    award_bid_streak_points,
    get_points_history,
    PLANS,
    TRIAL_DAYS,
    TRIAL_TIER
)

@pytest.fixture
def mock_session():
    return AsyncMock(spec=AsyncSession)

@pytest.fixture
def mock_user():
    user = AsyncMock(spec=User)
    user.id = 1
    user.points_balance = 500
    return user

# ── Plan Tests ─────────────────────────────────────────────

def test_get_plan_valid_days():
    """Test retrieving an existing plan by days."""
    plan = get_plan(30)
    assert plan is not None
    assert plan["days"] == 30
    assert plan["tier"] == "scout"

def test_get_plan_invalid_days():
    """Test retrieving a non-existent plan."""
    plan = get_plan(999)
    assert plan is None

# ── Subscription Activation Tests ─────────────────────────

@pytest.mark.asyncio
async def test_activate_trial_first_time(mock_session, mock_user):
    """Test successful trial activation for a new user."""
    # Mock no existing subscriptions
    mock_session.execute.return_value.scalar_one_or_none.return_value = None

    # Activate trial
    sub = await activate_trial(mock_session, mock_user)

    assert sub is not None
    assert sub.user_id == mock_user.id
    assert sub.plan_days == TRIAL_DAYS
    assert sub.amount_usd == 0.0
    assert sub.is_active is True

@pytest.mark.asyncio
async def test_activate_trial_duplicate_prevents_second_trial(mock_session, mock_user):
    """Test preventing trial for a user with existing subscription."""
    # Mock existing subscription
    mock_session.execute.return_value.scalar_one_or_none.return_value = Subscription()

    # Attempt trial activation
    sub = await activate_trial(mock_session, mock_user)

    assert sub is None

@pytest.mark.asyncio
async def test_activate_subscription_happy_path(mock_session, mock_user):
    """Test successful subscription activation."""
    # Setup
    plan_days = 30
    mock_session.execute.return_value.scalars.return_value.all.return_value = []

    # Activate subscription
    sub = await activate_subscription(mock_session, mock_user, plan_days)

    assert sub is not None
    assert sub.plan_days == plan_days
    assert sub.is_active is True
    assert sub.amount_usd == PLANS[plan_days]["price_usd"]

@pytest.mark.asyncio
async def test_activate_subscription_with_points_discount(mock_session, mock_user):
    """Test subscription activation with points discount."""
    # Setup
    plan_days = 30
    original_price = PLANS[plan_days]["price_usd"]
    discount_points = 100  # $1 off

    # Activate subscription with points
    sub = await activate_subscription(
        mock_session, mock_user, plan_days, 
        discount_points=discount_points
    )

    assert sub.amount_usd < original_price
    assert mock_user.points_balance < 500

@pytest.mark.asyncio
async def test_activate_subscription_invalid_plan(mock_session, mock_user):
    """Test activation with invalid plan raises ValueError."""
    with pytest.raises(ValueError, match="Invalid plan"):
        await activate_subscription(mock_session, mock_user, 999)

# ── Subscription Queries Tests ─────────────────────────

@pytest.mark.asyncio
async def test_has_active_subscription_true(mock_session, mock_user):
    """Test has_active_subscription returns True for active sub."""
    mock_session.execute.return_value.scalar_one_or_none.return_value = Subscription(is_active=True)
    
    result = await has_active_subscription(mock_session, mock_user.id)
    assert result is True

@pytest.mark.asyncio
async def test_has_active_subscription_false(mock_session, mock_user):
    """Test has_active_subscription returns False when no active sub."""
    mock_session.execute.return_value.scalar_one_or_none.return_value = None
    
    result = await has_active_subscription(mock_session, mock_user.id)
    assert result is False

@pytest.mark.asyncio
async def test_get_active_subscription(mock_session, mock_user):
    """Test retrieving active subscription."""
    mock_sub = Subscription(
        user_id=mock_user.id, 
        is_active=True, 
        expires_at=datetime.now(timezone.utc) + timedelta(days=30)
    )
    mock_session.execute.return_value.scalar_one_or_none.return_value = mock_sub

    sub = await get_active_subscription(mock_session, mock_user.id)
    assert sub is not None
    assert sub.user_id == mock_user.id

# ── Points Tests ─────────────────────────────────────────

@pytest.mark.asyncio
async def test_award_points_happy_path(mock_session, mock_user):
    """Test successful points award."""
    initial_balance = mock_user.points_balance
    
    txn = await award_points(
        mock_session, mock_user, 
        amount=50, 
        reason="test_award", 
        description="Test points award"
    )

    assert txn is not None
    assert mock_user.points_balance == initial_balance + 50
    assert txn.amount == 50
    assert txn.reason == "test_award"

@pytest.mark.asyncio
async def test_award_points_invalid_amount(mock_session, mock_user):
    """Test awarding invalid (non-positive) points raises error."""
    with pytest.raises(ValueError, match="Points amount must be positive"):
        await award_points(
            mock_session, mock_user, 
            amount=0, 
            reason="test_award"
        )

@pytest.mark.asyncio
async def test_award_bid_streak_points(mock_session, mock_user):
    """Test bid streak points award."""
    txn = await award_bid_streak_points(mock_session, mock_user, consecutive_bids=3)
    
    assert txn is not None
    assert txn.amount == 5
    assert txn.reason == "bid_streak"

@pytest.mark.asyncio
async def test_award_bid_streak_points_no_award(mock_session, mock_user):
    """Test no points awarded for insufficient streak."""
    txn = await award_bid_streak_points(mock_session, mock_user, consecutive_bids=2)
    
    assert txn is None

# Add more comprehensive tests for other functions...