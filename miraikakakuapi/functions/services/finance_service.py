from sqlalchemy.orm import Session
from repositories.stock_repository import StockRepository
from datetime import datetime, timedelta
import yfinance as yf
import pandas as pd
import numpy as np
from typing import List, Optional, Dict, Any
import logging
import asyncio
from concurrent.futures import ThreadPoolExecutor

logger = logging.getLogger(__name__)

class FinanceService:
    def __init__(self, db: Session):
        self.db = db
        self.stock_repo = StockRepository(db)
        self.executor = ThreadPoolExecutor(max_workers=4)
    
    async def fetch_comprehensive_stock_data(self, symbol: str) -> Optional[Dict[str, Any]]:
        """包括的な株式データを取得（基本情報+財務データ）"""
        try:
            ticker = yf.Ticker(symbol)
            
            # 並列でデータを取得
            tasks = [
                asyncio.create_task(self._get_stock_info(ticker)),
                asyncio.create_task(self._get_price_history(ticker)),
                asyncio.create_task(self._get_financial_data(ticker))
            ]
            
            info, history, financials = await asyncio.gather(*tasks, return_exceptions=True)
            
            return {
                "symbol": symbol.upper(),
                "info": info if not isinstance(info, Exception) else None,
                "history": history if not isinstance(history, Exception) else None,
                "financials": financials if not isinstance(financials, Exception) else None,
                "timestamp": datetime.utcnow()
            }
            
        except Exception as e:
            logger.error(f"包括的データ取得エラー {symbol}: {e}")
            return None

    async def _get_stock_info(self, ticker) -> Dict[str, Any]:
        """基本情報を取得"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(self.executor, lambda: ticker.info)

    async def _get_price_history(self, ticker, period: str = "1y") -> pd.DataFrame:
        """価格履歴を取得"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(self.executor, lambda: ticker.history(period=period))

    async def _get_financial_data(self, ticker) -> Dict[str, Any]:
        """財務データを取得"""
        loop = asyncio.get_event_loop()
        
        def fetch_financials():
            try:
                return {
                    "financials": ticker.financials,
                    "balance_sheet": ticker.balance_sheet,
                    "cashflow": ticker.cashflow,
                    "earnings": ticker.earnings
                }
            except:
                return {}
                
        return await loop.run_in_executor(self.executor, fetch_financials)

    async def update_stock_master_with_financials(self, symbol: str) -> bool:
        """財務データを含む株式マスター情報を更新"""
        try:
            data = await self.fetch_comprehensive_stock_data(symbol)
            if not data or not data['info']:
                return False
            
            info = data['info']
            
            stock_data = {
                'symbol': symbol.upper(),
                'company_name': info.get('longName', symbol),
                'exchange': info.get('exchange', 'Unknown'),
                'sector': info.get('sector'),
                'industry': info.get('industry'),
                'market_cap': info.get('marketCap'),
                'currency': info.get('currency', 'USD'),
                'country': info.get('country', 'US'),
                'pe_ratio': info.get('trailingPE'),
                'dividend_yield': info.get('dividendYield'),
                'beta': info.get('beta'),
                'description': info.get('longBusinessSummary')
            }
            
            self.stock_repo.create_or_update_stock(stock_data)
            logger.info(f"株式マスター更新完了: {symbol}")
            return True
            
        except Exception as e:
            logger.error(f"株式マスター更新エラー {symbol}: {e}")
            return False

    async def update_bulk_price_history(self, symbols: List[str], period: str = "30d") -> Dict[str, bool]:
        """複数銘柄の株価履歴を一括更新"""
        results = {}
        
        async def update_single_stock(symbol: str):
            try:
                data = await self.fetch_comprehensive_stock_data(symbol)
                if not data or data['history'] is None or data['history'].empty:
                    return False
                
                history = data['history']
                price_records = []
                
                for date, row in history.iterrows():
                    # 既存データチェック
                    existing = self.stock_repo.get_price_history(
                        symbol, 
                        start_date=date.date(),
                        end_date=date.date()
                    )
                    
                    if not existing:
                        price_records.append({
                            'symbol': symbol.upper(),
                            'date': date.date(),
                            'open_price': float(row['Open']) if not pd.isna(row['Open']) else None,
                            'high_price': float(row['High']) if not pd.isna(row['High']) else None,
                            'low_price': float(row['Low']) if not pd.isna(row['Low']) else None,
                            'close_price': float(row['Close']),
                            'adjusted_close': float(row['Close']),
                            'volume': int(row['Volume']) if not pd.isna(row['Volume']) else None,
                            'data_source': 'yfinance'
                        })
                
                if price_records:
                    count = self.stock_repo.bulk_insert_price_history(price_records)
                    logger.info(f"価格データ挿入: {symbol} - {count}件")
                
                return True
                
            except Exception as e:
                logger.error(f"価格履歴更新エラー {symbol}: {e}")
                return False
        
        # 並列処理で更新
        tasks = [update_single_stock(symbol) for symbol in symbols]
        results_list = await asyncio.gather(*tasks, return_exceptions=True)
        
        for i, result in enumerate(results_list):
            results[symbols[i]] = result if not isinstance(result, Exception) else False
        
        return results

    async def calculate_technical_indicators(self, symbol: str, period: int = 50) -> Optional[Dict[str, Any]]:
        """テクニカル指標を計算"""
        try:
            prices = self.stock_repo.get_price_history(symbol, limit=period)
            if len(prices) < 20:
                return None
            
            df = pd.DataFrame([{
                'date': p.date,
                'close': float(p.close_price),
                'high': float(p.high_price or p.close_price),
                'low': float(p.low_price or p.close_price),
                'volume': p.volume or 0
            } for p in reversed(prices)])
            
            # テクニカル指標計算
            indicators = {
                'sma_5': df['close'].rolling(5).mean().iloc[-1] if len(df) >= 5 else None,
                'sma_20': df['close'].rolling(20).mean().iloc[-1] if len(df) >= 20 else None,
                'sma_50': df['close'].rolling(50).mean().iloc[-1] if len(df) >= 50 else None,
                'rsi': self._calculate_rsi(df['close']).iloc[-1] if len(df) >= 14 else None,
                'macd': self._calculate_macd(df['close']) if len(df) >= 26 else None,
                'bollinger_bands': self._calculate_bollinger_bands(df['close']) if len(df) >= 20 else None,
                'volatility_1w': df['close'].tail(7).std() if len(df) >= 7 else None,
                'volatility_1m': df['close'].tail(30).std() if len(df) >= 30 else None,
            }
            
            return indicators
            
        except Exception as e:
            logger.error(f"テクニカル指標計算エラー {symbol}: {e}")
            return None

    def _calculate_rsi(self, prices: pd.Series, period: int = 14) -> pd.Series:
        """RSI計算"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs))

    def _calculate_macd(self, prices: pd.Series) -> Dict[str, float]:
        """MACD計算"""
        ema_12 = prices.ewm(span=12).mean()
        ema_26 = prices.ewm(span=26).mean()
        macd_line = ema_12 - ema_26
        signal_line = macd_line.ewm(span=9).mean()
        histogram = macd_line - signal_line
        
        return {
            'macd': macd_line.iloc[-1] if not macd_line.empty else 0,
            'signal': signal_line.iloc[-1] if not signal_line.empty else 0,
            'histogram': histogram.iloc[-1] if not histogram.empty else 0
        }

    def _calculate_bollinger_bands(self, prices: pd.Series, period: int = 20) -> Dict[str, float]:
        """ボリンジャーバンド計算"""
        sma = prices.rolling(period).mean()
        std = prices.rolling(period).std()
        
        return {
            'upper': (sma + (std * 2)).iloc[-1] if not sma.empty else 0,
            'middle': sma.iloc[-1] if not sma.empty else 0,
            'lower': (sma - (std * 2)).iloc[-1] if not sma.empty else 0
        }