"""
Unit tests for database models
"""
import pytest
from datetime import datetime
from decimal import Decimal
from functions.database.models.stock_master import StockMaster
from functions.database.models.stock_predictions import StockPredictions
from functions.database.models.stock_price_history import StockPriceHistory

@pytest.mark.unit
class TestStockMaster:
    """Test StockMaster model"""

    def test_create_stock_master(self, db_session):
        """Test creating a StockMaster instance"""
        stock = StockMaster(
            symbol="AAPL",
            name="Apple Inc.",
            exchange="NASDAQ",
            market_cap=3000000000000,
            sector="Technology"
        )

        db_session.add(stock)
        db_session.commit()

        assert stock.symbol == "AAPL"
        assert stock.name == "Apple Inc."
        assert stock.exchange == "NASDAQ"
        assert stock.is_active is True
        assert stock.created_at is not None

    def test_stock_master_relationships(self, db_session):
        """Test StockMaster relationships"""
        stock = StockMaster(symbol="TSLA", name="Tesla Inc.")
        db_session.add(stock)
        db_session.commit()

        # Add price history
        price = StockPriceHistory(
            symbol="TSLA",
            date=datetime.now(),
            open_price=Decimal("800.00"),
            close_price=Decimal("810.00"),
            volume=1000000
        )
        db_session.add(price)
        db_session.commit()

        # Test relationship
        assert len(stock.price_history) == 1
        assert stock.price_history[0].symbol == "TSLA"

@pytest.mark.unit
class TestStockPredictions:
    """Test StockPredictions model"""

    def test_create_prediction(self, db_session):
        """Test creating a prediction"""
        # First create stock master
        stock = StockMaster(symbol="GOOGL", name="Alphabet Inc.")
        db_session.add(stock)
        db_session.commit()

        prediction = StockPredictions(
            symbol="GOOGL",
            prediction_date=datetime.now(),
            target_date=datetime.now(),
            predicted_price=Decimal("2800.00"),
            current_price=Decimal("2750.00"),
            confidence_score=Decimal("0.85"),
            model_name="LSTM_v1"
        )

        db_session.add(prediction)
        db_session.commit()

        assert prediction.symbol == "GOOGL"
        assert prediction.predicted_price == Decimal("2800.00")
        assert prediction.model_name == "LSTM_v1"
        assert prediction.is_active is True

@pytest.mark.unit
class TestStockPriceHistory:
    """Test StockPriceHistory model"""

    def test_create_price_history(self, db_session):
        """Test creating price history"""
        # First create stock master
        stock = StockMaster(symbol="MSFT", name="Microsoft Corp.")
        db_session.add(stock)
        db_session.commit()

        price = StockPriceHistory(
            symbol="MSFT",
            date=datetime(2023, 1, 1),
            open_price=Decimal("250.00"),
            high_price=Decimal("255.00"),
            low_price=Decimal("248.00"),
            close_price=Decimal("252.00"),
            volume=5000000,
            adjusted_close=Decimal("252.00")
        )

        db_session.add(price)
        db_session.commit()

        assert price.symbol == "MSFT"
        assert price.open_price == Decimal("250.00")
        assert price.volume == 5000000
        assert price.created_at is not None