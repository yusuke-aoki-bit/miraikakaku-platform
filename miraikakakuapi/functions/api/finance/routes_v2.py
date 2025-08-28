"""
Finance API Routes V2 - Database first, Yahoo Finance fallback
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import text
from database.database import get_db
from datetime import datetime, timedelta
from typing import Optional
import yfinance as yf
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


async def get_stock_data_from_db(db: Session, symbol: str, days: int):
    """Get stock data from database"""
    try:
        # Try stock_price_history table (where actual data exists)
        query = text(
            """
            SELECT symbol, date, open_price, high_price, low_price,
                   close_price, volume
            FROM stock_price_history
            WHERE symbol = :symbol
            AND date >= :start_date
            ORDER BY date DESC
        """
        )
        start_date = datetime.now() - timedelta(days=days)
        result = db.execute(
            query, {
                "symbol": symbol, "start_date": start_date})
        rows = result.fetchall()

        if rows:
            return [
                {
                    "date": (
                        row[1].strftime("%Y-%m-%d")
                        if hasattr(row[1], "strftime")
                        else str(row[1])
                    ),
                    "open": float(row[2]) if row[2] else None,
                    "high": float(row[3]) if row[3] else None,
                    "low": float(row[4]) if row[4] else None,
                    "close": float(row[5]) if row[5] else None,
                    "volume": int(row[6]) if row[6] else 0,
                    "source": "database",
                }
                for row in rows
            ]

        return None
    except Exception as e:
        logger.warning(f"Database fetch failed for {symbol}: {e}")
        return None


async def get_stock_data_from_yfinance(symbol: str, days: int):
    """Fallback to Yahoo Finance if not in database"""
    try:
        ticker = yf.Ticker(symbol)
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)

        hist = ticker.history(start=start_date, end=end_date)

        if hist.empty:
            return None

        data = []
        for date, row in hist.iterrows():
            data.append(
                {
                    "date": date.strftime("%Y-%m-%d"),
                    "open": float(row["Open"]),
                    "high": float(row["High"]),
                    "low": float(row["Low"]),
                    "close": float(row["Close"]),
                    "volume": int(row["Volume"]) if row["Volume"] else 0,
                    "source": "yahoo_finance",
                }
            )

        return data
    except Exception as e:
        logger.error(f"Yahoo Finance fetch failed for {symbol}: {e}")
        return None


@router.get("/v2/stocks/{symbol}/price")
async def get_stock_price(
    symbol: str, days: int = Query(30, ge=1, le=365), db: Session = Depends(get_db)
):
    """
    Get stock price data
    1. First try database
    2. If not found, fallback to Yahoo Finance
    3. Optionally cache Yahoo data to database
    """
    # Map index symbols if needed
    SYMBOL_MAP = {
        "nikkei": "^N225",
        "topix": "^N225",  # Using Nikkei as fallback
        "dow": "^DJI",
        "sp500": "^GSPC",
    }

    mapped_symbol = SYMBOL_MAP.get(symbol.lower(), symbol.upper())

    # Step 1: Try database first
    logger.info(f"Fetching {mapped_symbol} from database...")
    db_data = await get_stock_data_from_db(db, mapped_symbol, days)

    if db_data:
        logger.info(
            f"Found {len(db_data)} records in database for {mapped_symbol}")
        return {
            "symbol": mapped_symbol,
            "data": db_data,
            "count": len(db_data),
            "source": "database",
        }

    # Step 2: Fallback to Yahoo Finance
    logger.info(
        f"No database data for {mapped_symbol}, trying Yahoo Finance...")
    yf_data = await get_stock_data_from_yfinance(mapped_symbol, days)

    if yf_data:
        logger.info(
            f"Found {len(yf_data)} records from Yahoo Finance for {mapped_symbol}"
        )

        # Optionally save to database for future use
        try:
            # Save last 10 records as sample
            for record in yf_data[:10]:
                insert_query = text(
                    """
                    INSERT IGNORE INTO stock_price_history
                    (symbol, date, open_price, high_price, low_price,
                     close_price, volume)
                    VALUES (:symbol, :date, :open_price, :high_price,
                            :low_price, :close_price, :volume)
                """
                )
                db.execute(
                    insert_query,
                    {
                        "symbol": mapped_symbol,
                        "date": record["date"],
                        "open_price": record["open"],
                        "high_price": record["high"],
                        "low_price": record["low"],
                        "close_price": record["close"],
                        "volume": record["volume"],
                    },
                )
            db.commit()
            logger.info(f"Cached {len(yf_data[:10])} records to database")
        except Exception as e:
            logger.warning(f"Failed to cache data: {e}")
            db.rollback()

        return {
            "symbol": mapped_symbol,
            "data": yf_data,
            "count": len(yf_data),
            "source": "yahoo_finance",
        }

    # Step 3: No data available
    raise HTTPException(
        status_code=404,
        detail=f"No data available for {symbol}")


@router.get("/v2/stocks/{symbol}/predictions")
async def get_stock_predictions(
    symbol: str, days: int = Query(30, ge=1, le=365), db: Session = Depends(get_db)
):
    """
    Get stock predictions with historical predictions
    1. Get actual data from DB or Yahoo
    2. Get predictions from DB
    3. Generate mock predictions if none exist
    """
    import numpy as np

    # Get actual price data first
    price_response = await get_stock_price(symbol, days, db)
    actual_data = price_response["data"]

    if not actual_data:
        raise HTTPException(status_code=404, detail="No data available")

    # Try to get predictions from database
    try:
        pred_query = text(
            """
            SELECT prediction_date, predicted_price, confidence_score,
                   model_version
            FROM stock_predictions
            WHERE symbol = :symbol
            AND prediction_date >= :start_date
            ORDER BY prediction_date DESC
        """
        )

        start_date = datetime.now() - timedelta(days=days)
        result = db.execute(
            pred_query, {"symbol": symbol.upper(), "start_date": start_date}
        )
        db_predictions = result.fetchall()

        if db_predictions:
            historical_predictions = [
                {
                    "date": (
                        row[0].strftime("%Y-%m-%d")
                        if hasattr(row[0], "strftime")
                        else str(row[0])
                    ),
                    "value": float(row[1]),
                    "confidence": float(row[2]) if row[2] else 0.8,
                    "type": "historical_prediction",
                }
                for row in db_predictions
            ]
        else:
            # Generate mock historical predictions
            historical_predictions = []
            for i in range(min(7, len(actual_data))):
                if i < len(actual_data):
                    data_point = actual_data[i]
                    historical_predictions.append(
                        {
                            "date": data_point["date"],
                            "value": (
                                data_point["close"] *
                                (1 + np.random.normal(0, 0.02))
                            ),
                            "confidence": round(np.random.uniform(0.7, 0.95), 2),
                            "type": "historical_prediction",
                        }
                    )
    except Exception as e:
        logger.warning(f"Failed to get predictions from DB: {e}")
        historical_predictions = []

    # Generate future predictions
    future_predictions = []
    if actual_data:
        last_price = actual_data[0]["close"]  # Most recent price
        last_date = datetime.strptime(actual_data[0]["date"], "%Y-%m-%d")

        for i in range(1, 8):  # 7 days of future predictions
            future_date = last_date + timedelta(days=i)
            trend = np.random.normal(0.001, 0.01)
            predicted_value = last_price * (1 + trend * i)

            future_predictions.append(
                {
                    "date": future_date.strftime("%Y-%m-%d"),
                    "value": round(float(predicted_value), 2),
                    "confidence": round(max(0.5, 0.9 - i * 0.05), 2),
                    "type": "future_prediction",
                }
            )

    # Format actual data for response
    actual_formatted = [
        {"date": item["date"], "value": item["close"], "type": "actual"}
        for item in actual_data
    ]

    return {
        "symbol": price_response["symbol"],
        "data": {
            "actual": actual_formatted,
            "historical_predictions": historical_predictions,
            "future_predictions": future_predictions,
        },
        "summary": {
            "actual_count": len(actual_formatted),
            "historical_predictions_count": (len(historical_predictions)),
            "future_predictions_count": len(future_predictions),
            "data_source": price_response["source"],
        },
    }


@router.get("/v2/available-stocks")
async def get_available_stocks(
    market: Optional[str] = Query(None, description="Filter by market"),
    country: Optional[str] = Query(None, description="Filter by country"),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
):
    """Get list of available stocks from database"""
    try:
        query = "SELECT symbol, name, market, country FROM stock_master " "WHERE 1=1"
        params = {}

        if market:
            query += " AND market = :market"
            params["market"] = market

        if country:
            query += " AND country = :country"
            params["country"] = country

        query += f" LIMIT {limit}"

        result = db.execute(text(query), params)
        stocks = result.fetchall()

        return {
            "count": len(stocks),
            "stocks": [
                {
                    "symbol": stock[0],
                    "name": stock[1],
                    "market": stock[2],
                    "country": stock[3],
                }
                for stock in stocks
            ],
        }
    except Exception as e:
        logger.error(f"Failed to get available stocks: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/v2/stats")
async def get_database_stats(db: Session = Depends(get_db)):
    """Get database statistics"""
    try:
        stats = {}

        # Count stocks
        result = db.execute(text("SELECT COUNT(*) FROM stock_master"))
        stats["total_stocks"] = result.scalar()

        # Count by market
        result = db.execute(
            text(
                "SELECT market, COUNT(*) as count FROM stock_master " "GROUP BY market"
            )
        )
        stats["by_market"] = {row[0]: row[1] for row in result}

        # Count by country
        result = db.execute(
            text(
                "SELECT country, COUNT(*) as count FROM stock_master "
                "GROUP BY country"
            )
        )
        stats["by_country"] = {row[0]: row[1] for row in result}

        # Count price data
        result = db.execute(text("SELECT COUNT(*) FROM stock_price_history"))
        stats["total_price_records"] = result.scalar()

        # Count predictions
        result = db.execute(text("SELECT COUNT(*) FROM stock_predictions"))
        stats["total_predictions"] = result.scalar()

        return stats

    except Exception as e:
        logger.error(f"Failed to get stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))
