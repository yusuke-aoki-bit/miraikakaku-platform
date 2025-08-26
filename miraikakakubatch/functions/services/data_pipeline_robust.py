import yfinance as yf
import pandas as pd
import numpy as np
from sqlalchemy.orm import Session
from database.database import get_db_session
from database.models import StockMaster, StockPriceHistory
from datetime import datetime, timedelta
import logging
from typing import List, Optional

logger = logging.getLogger(__name__)


class DataPipelineService:
    def __init__(self):
        self.db_session = get_db_session()

    def execute(self):
        """データパイプラインのメイン実行"""
        logger.info("データパイプライン開始")

        try:
            # アクティブな銘柄を取得
            active_symbols = self.get_active_symbols()
            logger.info(f"処理対象銘柄数: {len(active_symbols)}")

            # 各銘柄の株価データを更新
            success_count = 0
            for symbol in active_symbols:
                if self.update_stock_data(symbol):
                    success_count += 1

            logger.info(f"データ更新完了: {success_count}/{len(active_symbols)} 銘柄")

        except Exception as e:
            logger.error(f"データパイプラインエラー: {e}")
        finally:
            self.db_session.close()

    def get_active_symbols(self) -> List[str]:
        """アクティブな銘柄リストを取得"""
        try:
            stocks = (
                self.db_session.query(StockMaster)
                .filter(StockMaster.is_active == True)
                .all()
            )
            return [stock.symbol for stock in stocks]
        except Exception as e:
            logger.error(f"銘柄リスト取得エラー: {e}")
            # フォールバック用の主要銘柄
            return ["AAPL", "GOOGL", "MSFT", "TSLA", "AMZN", "NVDA", "META", "NFLX"]

    def update_stock_data(self, symbol: str) -> bool:
        """個別銘柄の株価データを更新"""
        try:
            # yfinanceから最新データを取得
            stock = yf.Ticker(symbol)
            hist = stock.history(period="5d")  # 過去5日分

            if hist.empty:
                logger.warning(f"データが取得できませんでした: {symbol}")
                return False

            # データベースに保存
            for date, row in hist.iterrows():
                existing = (
                    self.db_session.query(StockPriceHistory)
                    .filter(
                        StockPriceHistory.symbol == symbol,
                        StockPriceHistory.date == date.date(),
                    )
                    .first()
                )

                if not existing:
                    price_record = StockPriceHistory(
                        symbol=symbol,
                        date=date.date(),
                        open_price=(
                            float(row["Open"]) if not pd.isna(row["Open"]) else None
                        ),
                        high_price=(
                            float(row["High"]) if not pd.isna(row["High"]) else None
                        ),
                        low_price=(
                            float(row["Low"]) if not pd.isna(row["Low"]) else None
                        ),
                        close_price=float(row["Close"]),
                        volume=(
                            int(row["Volume"]) if not pd.isna(row["Volume"]) else None
                        ),
                        data_source="yfinance",
                    )
                    self.db_session.add(price_record)

            self.db_session.commit()
            logger.info(f"データ更新完了: {symbol}")
            return True

        except Exception as e:
            logger.error(f"データ更新エラー {symbol}: {e}")
            self.db_session.rollback()
            return False

    def seed_sample_stocks(self):
        """サンプル銘柄をマスターテーブルに登録"""
        sample_stocks = [
            {
                "symbol": "AAPL",
                "company_name": "Apple Inc.",
                "exchange": "NASDAQ",
                "sector": "Technology",
            },
            {
                "symbol": "GOOGL",
                "company_name": "Alphabet Inc.",
                "exchange": "NASDAQ",
                "sector": "Technology",
            },
            {
                "symbol": "MSFT",
                "company_name": "Microsoft Corporation",
                "exchange": "NASDAQ",
                "sector": "Technology",
            },
            {
                "symbol": "TSLA",
                "company_name": "Tesla Inc.",
                "exchange": "NASDAQ",
                "sector": "Automotive",
            },
            {
                "symbol": "AMZN",
                "company_name": "Amazon.com Inc.",
                "exchange": "NASDAQ",
                "sector": "E-commerce",
            },
            {
                "symbol": "NVDA",
                "company_name": "NVIDIA Corporation",
                "exchange": "NASDAQ",
                "sector": "Technology",
            },
            {
                "symbol": "META",
                "company_name": "Meta Platforms Inc.",
                "exchange": "NASDAQ",
                "sector": "Technology",
            },
            {
                "symbol": "NFLX",
                "company_name": "Netflix Inc.",
                "exchange": "NASDAQ",
                "sector": "Entertainment",
            },
        ]

        for stock_data in sample_stocks:
            existing = (
                self.db_session.query(StockMaster)
                .filter(StockMaster.symbol == stock_data["symbol"])
                .first()
            )

            if not existing:
                stock = StockMaster(**stock_data)
                self.db_session.add(stock)

        self.db_session.commit()
        logger.info("サンプル銘柄登録完了")
