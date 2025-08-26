#!/usr/bin/env python3
"""
リアルタイム市場データ更新 - 正確な日経平均、TOPIX、主要株価を取得
Yahoo Finance APIから実際の価格データを取得してデータベースを更新
"""

import yfinance as yf
import pymysql
import pandas as pd
import logging
from datetime import datetime, timedelta
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RealMarketDataUpdater:
    def __init__(self):
        self.db_config = {
            "host": "34.58.103.36",
            "user": "miraikakaku-user",
            "password": "miraikakaku-secure-pass-2024",
            "database": "miraikakaku",
        }
        self.updated_count = 0

    def get_connection(self):
        return pymysql.connect(**self.db_config)

    def update_major_japanese_indices(self):
        """主要日本株指数の実データ更新"""
        logger.info("=== 主要日本株指数のリアルデータ更新開始 ===")

        # 日本の主要指数と対応するYahoo Financeシンボル
        major_indices = {
            # 日経225関連
            "1321": "^N225",  # 日経225ETF -> 日経225指数
            "1330": "^N225",  # 上場インデックスファンド225
            # TOPIX関連
            "1306": "^TPX",  # TOPIX ETF -> TOPIX
            "1308": "^TPX",  # 上場インデックスファンドTOPIX
            # 主要個別株
            "7203": "7203.T",  # トヨタ自動車
            "6758": "6758.T",  # ソニーグループ
            "9984": "9984.T",  # ソフトバンクグループ
            "6861": "6861.T",  # キーエンス
            "4519": "4519.T",  # 中外製薬
            "9432": "9432.T",  # NTT
            "8306": "8306.T",  # 三菱UFJフィナンシャル・グループ
            "2914": "2914.T",  # 日本たばこ産業
            "4063": "4063.T",  # 信越化学工業
            "8001": "8001.T",  # 伊藤忠商事
        }

        connection = self.get_connection()
        try:
            for db_symbol, yahoo_symbol in major_indices.items():
                logger.info(f"更新中: {db_symbol} <- {yahoo_symbol}")
                self._update_stock_data(connection, db_symbol, yahoo_symbol)
                time.sleep(1)  # レート制限対応

        finally:
            connection.close()

    def _update_stock_data(self, connection, db_symbol, yahoo_symbol):
        """個別銘柄のデータを更新"""
        try:
            # Yahoo Financeから最新データを取得（テスト用に7日分）
            end_date = datetime.now()
            start_date = end_date - timedelta(days=7)  # テスト用に7日分

            hist = yf.download(
                yahoo_symbol, start=start_date, end=end_date, progress=False
            )

            if hist.empty:
                logger.warning(f"⚠️  {yahoo_symbol}: 価格データなし")
                return

            # 企業情報更新
            try:
                ticker = yf.Ticker(yahoo_symbol)
                info = ticker.info
                company_name = info.get(
                    "longName", info.get("shortName", f"{db_symbol} Corporation")
                )
                sector = info.get("sector", "Financial Services")
                industry = info.get("industry", "Asset Management")

                with connection.cursor() as cursor:
                    cursor.execute(
                        """
                        UPDATE stock_master 
                        SET name = %s, sector = %s, industry = %s
                        WHERE symbol = %s
                    """,
                        (company_name, sector, industry, db_symbol),
                    )

            except Exception as e:
                logger.warning(f"企業情報更新スキップ {db_symbol}: {e}")

            # 既存の価格データを削除（最新データに置き換える）
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    DELETE FROM stock_price_history 
                    WHERE symbol = %s AND date >= %s
                """,
                    (db_symbol, start_date.date()),
                )

                # 新しい価格データを挿入
                insert_count = 0

                for date_idx in hist.index:
                    try:
                        # 日付処理
                        if hasattr(date_idx, "strftime"):
                            date_str = date_idx.strftime("%Y-%m-%d")
                        elif hasattr(date_idx, "date"):
                            date_str = date_idx.date().strftime("%Y-%m-%d")
                        else:
                            date_str = str(date_idx)[:10]

                        # データ取得（MultiIndex対応）
                        if len(hist.columns.levels) > 1:
                            # MultiIndex の場合
                            open_val = hist.loc[date_idx, ("Open", yahoo_symbol)]
                            high_val = hist.loc[date_idx, ("High", yahoo_symbol)]
                            low_val = hist.loc[date_idx, ("Low", yahoo_symbol)]
                            close_val = hist.loc[date_idx, ("Close", yahoo_symbol)]
                            volume_val = hist.loc[date_idx, ("Volume", yahoo_symbol)]
                            adj_close_val = close_val  # Adjusted Closeは使わない
                        else:
                            # 通常のDataFrameの場合
                            open_val = hist.loc[date_idx, "Open"]
                            high_val = hist.loc[date_idx, "High"]
                            low_val = hist.loc[date_idx, "Low"]
                            close_val = hist.loc[date_idx, "Close"]
                            adj_close_val = (
                                hist.loc[date_idx, "Adj Close"]
                                if "Adj Close" in hist.columns
                                else close_val
                            )
                            volume_val = hist.loc[date_idx, "Volume"]

                        cursor.execute(
                            """
                            INSERT INTO stock_price_history 
                            (symbol, date, open_price, high_price, low_price, close_price, 
                             adjusted_close, volume, data_source, created_at)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        """,
                            (
                                db_symbol,
                                date_str,
                                float(open_val) if not pd.isna(open_val) else None,
                                float(high_val) if not pd.isna(high_val) else None,
                                float(low_val) if not pd.isna(low_val) else None,
                                float(close_val) if not pd.isna(close_val) else None,
                                (
                                    float(adj_close_val)
                                    if not pd.isna(adj_close_val)
                                    else None
                                ),
                                int(volume_val) if not pd.isna(volume_val) else None,
                                "yfinance_real",
                                datetime.now(),
                            ),
                        )
                        insert_count += 1

                    except Exception as e:
                        logger.error(
                            f"価格データ挿入エラー {db_symbol} {date_idx}: {e}"
                        )

                connection.commit()
                self.updated_count += 1

                # 最新価格を取得して表示
                if not hist.empty:
                    if len(hist.columns.levels) > 1:
                        # MultiIndex の場合
                        latest_price = float(hist[("Close", yahoo_symbol)].iloc[-1])
                    else:
                        # 通常のDataFrameの場合
                        latest_price = float(hist["Close"].iloc[-1])
                    logger.info(
                        f"✅ {db_symbol}: {insert_count}件更新 (最新価格: ¥{latest_price:,.2f})"
                    )
                else:
                    logger.info(f"✅ {db_symbol}: {insert_count}件更新")

        except Exception as e:
            logger.error(f"データ更新エラー {db_symbol}: {e}")

    def update_us_major_stocks(self):
        """主要米国株のリアルデータ更新"""
        logger.info("=== 主要米国株のリアルデータ更新開始 ===")

        # 主要米国株
        us_major_stocks = [
            "AAPL",
            "MSFT",
            "GOOGL",
            "AMZN",
            "TSLA",
            "NVDA",
            "META",
            "NFLX",
            "UBER",
            "ZOOM",
            "ROKU",
            "SHOP",
            "CRWD",
            "OKTA",
            "SNOW",
            "DDOG",
        ]

        connection = self.get_connection()
        try:
            for symbol in us_major_stocks[:10]:  # 最初の10銘柄のみ更新
                logger.info(f"更新中: {symbol}")
                self._update_stock_data(connection, symbol, symbol)
                time.sleep(1)  # レート制限対応

        finally:
            connection.close()

    def verify_updates(self):
        """更新結果の確認"""
        logger.info("=== 更新結果の確認 ===")

        connection = self.get_connection()
        try:
            with connection.cursor(pymysql.cursors.DictCursor) as cursor:
                # 日経225ETFの最新価格確認
                cursor.execute(
                    """
                    SELECT symbol, date, close_price, data_source
                    FROM stock_price_history 
                    WHERE symbol = '1321' AND data_source = 'yfinance_real'
                    ORDER BY date DESC LIMIT 1
                """
                )
                result = cursor.fetchone()

                if result:
                    logger.info(
                        f"✅ 1321(日経225ETF): ¥{result['close_price']:,.2f} ({result['date']})"
                    )
                else:
                    logger.warning("⚠️  1321の実データが見つかりません")

                # TOPIX ETFの最新価格確認
                cursor.execute(
                    """
                    SELECT symbol, date, close_price, data_source
                    FROM stock_price_history 
                    WHERE symbol = '1306' AND data_source = 'yfinance_real'
                    ORDER BY date DESC LIMIT 1
                """
                )
                result = cursor.fetchone()

                if result:
                    logger.info(
                        f"✅ 1306(TOPIX ETF): ¥{result['close_price']:,.2f} ({result['date']})"
                    )

                # 主要銘柄の確認
                cursor.execute(
                    """
                    SELECT p.symbol, m.name, p.close_price, p.date
                    FROM stock_price_history p
                    JOIN stock_master m ON p.symbol = m.symbol
                    WHERE p.symbol IN ('7203', '6758', '9984') 
                    AND p.data_source = 'yfinance_real'
                    AND p.date = (SELECT MAX(ph2.date) FROM stock_price_history ph2 WHERE ph2.symbol = p.symbol AND ph2.data_source = 'yfinance_real')
                    ORDER BY p.symbol
                """
                )
                results = cursor.fetchall()

                for row in results:
                    logger.info(
                        f"✅ {row['symbol']}({row['name']}): ¥{row['close_price']:,.2f}"
                    )

        finally:
            connection.close()

    def execute_update(self):
        """全体のデータ更新実行"""
        logger.info("🔄 リアルタイム市場データ更新開始")
        start_time = datetime.now()

        try:
            # 日本の主要指数・個別株を更新
            self.update_major_japanese_indices()

            # 主要米国株を更新
            self.update_us_major_stocks()

            # 更新結果確認
            self.verify_updates()

        except Exception as e:
            logger.error(f"更新プロセスエラー: {e}")

        end_time = datetime.now()
        duration = end_time - start_time

        logger.info("🎯 リアルタイム市場データ更新完了")
        logger.info(f"実行時間: {duration}")
        logger.info(f"更新銘柄数: {self.updated_count}")


if __name__ == "__main__":
    updater = RealMarketDataUpdater()
    updater.execute_update()
