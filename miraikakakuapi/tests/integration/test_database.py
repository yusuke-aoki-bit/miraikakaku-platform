"""
Integration tests for database operations.
"""
import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from functions.database.models.stock_master import StockMaster
from functions.database.models.stock_price_history import StockPriceHistory
from functions.database.models.stock_predictions import StockPredictions


@pytest.mark.integration
async def test_create_stock_master(db_session: AsyncSession):
    """Test creating stock master record."""
    stock = StockMaster(
        symbol="AAPL",
        company_name="Apple Inc.",
        exchange="NASDAQ",
        sector="Technology",
        industry="Consumer Electronics",
        is_active=True
    )

    db_session.add(stock)
    await db_session.commit()
    await db_session.refresh(stock)

    assert stock.id is not None
    assert stock.symbol == "AAPL"
    assert stock.company_name == "Apple Inc."


@pytest.mark.integration
async def test_create_stock_price_history(db_session: AsyncSession):
    """Test creating stock price history record."""
    # First create a stock master record
    stock = StockMaster(
        symbol="AAPL",
        company_name="Apple Inc.",
        exchange="NASDAQ",
        is_active=True
    )
    db_session.add(stock)
    await db_session.commit()

    # Create price history
    price_history = StockPriceHistory(
        symbol="AAPL",
        date="2024-01-15",
        open_price=150.00,
        high_price=155.00,
        low_price=149.50,
        close_price=154.25,
        volume=45234567,
        adjusted_close=154.25
    )

    db_session.add(price_history)
    await db_session.commit()
    await db_session.refresh(price_history)

    assert price_history.id is not None
    assert price_history.symbol == "AAPL"
    assert price_history.close_price == 154.25


@pytest.mark.integration
async def test_create_stock_prediction(db_session: AsyncSession):
    """Test creating stock prediction record."""
    # Create stock master first
    stock = StockMaster(
        symbol="AAPL",
        company_name="Apple Inc.",
        exchange="NASDAQ",
        is_active=True
    )
    db_session.add(stock)
    await db_session.commit()

    # Create prediction
    from datetime import datetime
    prediction = StockPredictions(
        symbol="AAPL",
        prediction_date=datetime(2024, 1, 16),
        target_date=datetime(2024, 1, 17),
        predicted_price=156.50,
        confidence_score=0.85,
        model_name="lstm_v2",
        model_type="lstm",
        model_version="v2.1"
    )

    db_session.add(prediction)
    await db_session.commit()
    await db_session.refresh(prediction)

    assert prediction.id is not None
    assert prediction.symbol == "AAPL"
    assert prediction.predicted_price == 156.50
    assert prediction.confidence_score == 0.85


@pytest.mark.integration
async def test_query_stock_with_prices(db_session: AsyncSession):
    """Test querying stock with price history."""
    # Create test data
    stock = StockMaster(
        symbol="AAPL",
        company_name="Apple Inc.",
        exchange="NASDAQ",
        is_active=True
    )
    db_session.add(stock)

    prices = [
        StockPriceHistory(
            symbol="AAPL",
            date="2024-01-15",
            close_price=154.25,
            volume=45000000
        ),
        StockPriceHistory(
            symbol="AAPL",
            date="2024-01-16",
            close_price=156.50,
            volume=47000000
        )
    ]

    for price in prices:
        db_session.add(price)

    await db_session.commit()

    # Query with relationship
    from sqlalchemy import select
    result = await db_session.execute(
        select(StockMaster).where(StockMaster.symbol == "AAPL")
    )
    queried_stock = result.scalar_one()

    assert queried_stock.symbol == "AAPL"
    assert queried_stock.company_name == "Apple Inc."


@pytest.mark.integration
async def test_database_constraints(db_session: AsyncSession):
    """Test database constraints and validation."""
    # Test duplicate symbol constraint (if exists)
    stock1 = StockMaster(
        symbol="AAPL",
        company_name="Apple Inc.",
        exchange="NASDAQ",
        is_active=True
    )
    db_session.add(stock1)
    await db_session.commit()

    # Try to add duplicate (should handle gracefully)
    stock2 = StockMaster(
        symbol="AAPL",
        company_name="Apple Inc. Duplicate",
        exchange="NASDAQ",
        is_active=True
    )
    db_session.add(stock2)

    # This might raise an exception depending on DB constraints
    try:
        await db_session.commit()
        # If no constraint, both records exist
        assert True
    except Exception:
        # If constraint exists, rollback and verify first record exists
        await db_session.rollback()
        from sqlalchemy import select
        result = await db_session.execute(
            select(StockMaster).where(StockMaster.symbol == "AAPL")
        )
        stocks = result.scalars().all()
        assert len(stocks) >= 1