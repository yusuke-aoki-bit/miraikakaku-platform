import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
from ..core.cache import cache
from ..core.database import db
from ..core.exceptions import (
    APIError, ExternalAPIError, StockNotFoundError,
    handle_service_error, create_error_response
)
from ..core.logging_config import (
    get_logger, log_execution_time,
    log_external_api_call, log_business_event
)

logger = get_logger(__name__)


class StockService:
    """Service for handling stock data operations."""

    @log_execution_time()
    async def get_stock_price_history(self, symbol: str, days: int = 730) -> List[Dict]:
        """Get stock price history with caching."""
        operation = f"get_stock_price_history({symbol}, {days})"

        try:
            # Validate input
            if not symbol or not isinstance(symbol, str):
                raise APIError(
                    "Invalid symbol provided",
                    category="validation",
                    status_code=400,
                    details={"symbol": symbol}
                )

            # Try cache first
            cached_data = await cache.get_stock_prices(symbol, days)
            if cached_data:
                log_business_event(
                    "stock_price_cache_hit",
                    {"symbol": symbol, "days": days, "data_points": len(cached_data)},
                    symbol=symbol
                )
                return cached_data

            # Calculate start date
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)

            # Fetch from yfinance
            import time
            api_start = time.time()

            ticker = yf.Ticker(symbol)
            hist_data = ticker.history(
                start=start_date.strftime('%Y-%m-%d'),
                end=end_date.strftime('%Y-%m-%d')
            )

            api_duration = time.time() - api_start
            log_external_api_call(
                "yfinance",
                f"ticker/{symbol}/history",
                "GET",
                200 if not hist_data.empty else 404,
                api_duration,
                symbol=symbol,
                days=days
            )

            if hist_data.empty:
                logger.warning(f"No price history data found for {symbol}")
                raise StockNotFoundError(symbol)

            # Convert to required format
            price_history = []
            for date, row in hist_data.iterrows():
                try:
                    price_history.append({
                        "date": date.strftime('%Y-%m-%d'),
                        "open_price": float(row['Open']),
                        "high_price": float(row['High']),
                        "low_price": float(row['Low']),
                        "close_price": float(row['Close']),
                        "volume": int(row['Volume']),
                        "adjusted_close": float(row['Close'])
                    })
                except (ValueError, KeyError) as e:
                    logger.warning(f"Invalid data point for {symbol} on {date}: {e}")
                    continue

            if not price_history:
                raise StockNotFoundError(symbol)

            # Cache the results
            try:
                await cache.set_stock_prices(symbol, days, price_history, ttl=600)
            except Exception as cache_error:
                logger.warning(f"Failed to cache price history for {symbol}: {cache_error}")

            log_business_event(
                "stock_price_fetched",
                {"symbol": symbol, "days": days, "data_points": len(price_history)},
                symbol=symbol
            )

            return price_history

        except APIError:
            raise
        except Exception as e:
            api_error = handle_service_error(e, operation, {"symbol": symbol, "days": days})
            raise api_error

    @log_execution_time()
    async def get_stock_details(self, symbol: str) -> Optional[Dict]:
        """Get detailed stock information with caching."""
        operation = f"get_stock_details({symbol})"

        try:
            # Validate input
            if not symbol or not isinstance(symbol, str):
                raise APIError(
                    "Invalid symbol provided",
                    category="validation",
                    status_code=400,
                    details={"symbol": symbol}
                )

            cached_data = await cache.get_stock_data(symbol)
            if cached_data:
                log_business_event(
                    "stock_details_cache_hit",
                    {"symbol": symbol},
                    symbol=symbol
                )
                return cached_data

            import time
            api_start = time.time()

            ticker = yf.Ticker(symbol)
            info = ticker.info

            api_duration = time.time() - api_start

            if not info or 'regularMarketPrice' not in info:
                log_external_api_call(
                    "yfinance",
                    f"ticker/{symbol}/info",
                    "GET",
                    404,
                    api_duration,
                    symbol=symbol
                )
                logger.warning(f"No stock details found for {symbol}")
                raise StockNotFoundError(symbol)

            log_external_api_call(
                "yfinance",
                f"ticker/{symbol}/info",
                "GET",
                200,
                api_duration,
                symbol=symbol
            )

            # Extract relevant information with validation
            stock_details = {
                "symbol": symbol,
                "longName": info.get("longName"),
                "shortName": info.get("shortName"),
                "sector": info.get("sector"),
                "industry": info.get("industry"),
                "country": info.get("country"),
                "website": info.get("website"),
                "longBusinessSummary": info.get("longBusinessSummary"),
                "marketCap": info.get("marketCap"),
                "beta": info.get("beta"),
                "trailingPE": info.get("trailingPE"),
                "dividendYield": info.get("dividendYield"),
                "previousClose": info.get("previousClose"),
                "dayHigh": info.get("dayHigh"),
                "dayLow": info.get("dayLow"),
                "fiftyTwoWeekHigh": info.get("fiftyTwoWeekHigh"),
                "fiftyTwoWeekLow": info.get("fiftyTwoWeekLow"),
                "volume": info.get("volume"),
                "regularMarketPrice": info.get("regularMarketPrice")
            }

            # Cache the results
            try:
                await cache.set_stock_data(symbol, stock_details, ttl=300)
            except Exception as cache_error:
                logger.warning(f"Failed to cache stock details for {symbol}: {cache_error}")

            log_business_event(
                "stock_details_fetched",
                {"symbol": symbol, "market_cap": stock_details.get("marketCap")},
                symbol=symbol
            )

            return stock_details

        except APIError:
            raise
        except Exception as e:
            api_error = handle_service_error(e, operation, {"symbol": symbol})
            raise api_error

    @log_execution_time()
    async def search_stocks(self, query: str, limit: int = 10) -> List[Dict]:
        """Search for stocks by query."""
        operation = f"search_stocks({query}, {limit})"

        try:
            # Validate input
            if not query or not isinstance(query, str) or len(query.strip()) < 1:
                raise APIError(
                    "Invalid search query provided",
                    category="validation",
                    status_code=400,
                    details={"query": query}
                )

            if limit <= 0 or limit > 50:
                raise APIError(
                    "Invalid limit value. Must be between 1 and 50",
                    category="validation",
                    status_code=400,
                    details={"limit": limit}
                )

            query = query.strip()

            # Use yfinance's Ticker.info for basic search
            # This is a simplified implementation - in production you'd want a proper search API
            potential_symbols = [
                query.upper(),
                f"{query.upper()}.TO",  # Toronto
                f"{query.upper()}.L",   # London
            ]

            results = []
            failed_symbols = []

            for symbol in potential_symbols[:limit]:
                try:
                    import time
                    api_start = time.time()

                    ticker = yf.Ticker(symbol)
                    info = ticker.info

                    api_duration = time.time() - api_start

                    if info and 'longName' in info:
                        log_external_api_call(
                            "yfinance",
                            f"ticker/{symbol}/info",
                            "GET",
                            200,
                            api_duration,
                            symbol=symbol
                        )

                        results.append({
                            "symbol": symbol,
                            "name": info.get("longName", symbol),
                            "sector": info.get("sector"),
                            "market": info.get("exchange"),
                            "currency": info.get("currency", "USD")
                        })
                    else:
                        log_external_api_call(
                            "yfinance",
                            f"ticker/{symbol}/info",
                            "GET",
                            404,
                            api_duration,
                            symbol=symbol
                        )
                        failed_symbols.append(symbol)

                    if len(results) >= limit:
                        break

                except Exception as e:
                    logger.debug(f"Symbol {symbol} not found: {e}")
                    failed_symbols.append(symbol)
                    continue

            log_business_event(
                "stock_search_completed",
                {
                    "query": query,
                    "results_count": len(results),
                    "failed_symbols": failed_symbols
                }
            )

            return results

        except APIError:
            raise
        except Exception as e:
            api_error = handle_service_error(e, operation, {"query": query, "limit": limit})
            raise api_error

    async def get_growth_rankings(self) -> List[Dict]:
        """Get growth potential rankings."""
        cache_key = "rankings:growth"

        # Try cache first
        cached_data = await cache.get_rankings("growth")
        if cached_data:
            return cached_data

        try:
            # Popular growth stocks (this would be database-driven in production)
            growth_symbols = [
                "AAPL", "MSFT", "GOOGL", "AMZN", "TSLA",
                "NVDA", "META", "NFLX", "ADBE", "CRM"
            ]

            rankings = []

            for symbol in growth_symbols:
                try:
                    ticker = yf.Ticker(symbol)
                    info = ticker.info

                    if info and 'longName' in info:
                        rankings.append({
                            "symbol": symbol,
                            "name": info.get("longName", symbol),
                            "sector": info.get("sector"),
                            "marketCap": info.get("marketCap", 0),
                            "beta": info.get("beta", 1.0),
                            "trailingPE": info.get("trailingPE"),
                            "priceChange": np.random.uniform(-5, 15)  # Mock data
                        })

                except Exception as e:
                    logger.debug(f"Error fetching data for {symbol}: {e}")
                    continue

            # Sort by market cap
            rankings.sort(key=lambda x: x["marketCap"] or 0, reverse=True)

            # Cache the results
            await cache.set_rankings("growth", rankings[:10], ttl=1800)

            return rankings[:10]

        except Exception as e:
            logger.error(f"Error fetching growth rankings: {e}")
            return []

    async def get_validated_symbols(self) -> List[str]:
        """Get list of validated trading symbols."""
        cache_key = "validated_symbols"

        # Try cache first
        cached_data = await cache.get(cache_key)
        if cached_data:
            return cached_data

        try:
            # In production, this would come from database
            # For now, return popular symbols
            symbols = [
                "AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "META", "NVDA",
                "NFLX", "ADBE", "CRM", "PYPL", "INTC", "AMD", "QCOM",
                "SPY", "QQQ", "IWM", "VTI", "VXUS"
            ]

            # Cache for 1 hour
            await cache.set(cache_key, symbols, ttl=3600)

            return symbols

        except Exception as e:
            logger.error(f"Error loading validated symbols: {e}")
            return []