#!/usr/bin/env python3
"""
シンプルなデータ取得パイプライン
株価データを取得してCloud SQLに保存
"""

import logging
import pymysql
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import os
import random
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SimpleDataPipelineService:
    def __init__(self):
        self.db_config = {
            "host": "34.58.103.36",
            "user": "miraikakaku-user",
            "password": "miraikakaku-secure-pass-2024",
            "database": "miraikakaku",
        }

    def get_connection(self):
        """データベース接続を取得"""
        return pymysql.connect(**self.db_config)

    def get_active_symbols(self):
        """アクティブな銘柄リストを取得"""
        connection = self.get_connection()
        try:
            with connection.cursor() as cursor:
                # まずはNASDAQの銘柄から開始（データ取得しやすいため）
                cursor.execute(
                    """
                    SELECT symbol FROM stock_master 
                    WHERE is_active = 1 AND exchange = 'NASDAQ'
                    ORDER BY symbol
                    LIMIT 50
                """
                )
                nasdaq_symbols = [row[0] for row in cursor.fetchall()]

                # 日本株の主要銘柄も追加
                cursor.execute(
                    """
                    SELECT symbol FROM stock_master 
                    WHERE is_active = 1 
                    AND exchange IN ('Prime Market (Domestic)', 'Standard Market(Domestic)')
                    AND symbol REGEXP '^[0-9]+$'
                    ORDER BY symbol
                    LIMIT 30
                """
                )
                jp_symbols = [
                    row[0] + ".T" for row in cursor.fetchall()
                ]  # 日本株にはサフィックス追加

                return nasdaq_symbols + jp_symbols
        finally:
            connection.close()

    def fetch_stock_data(self, symbol, days=90):
        """Yahoo Financeから株価データを取得"""
        try:
            ticker = yf.Ticker(symbol)
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)

            hist = ticker.download(start=start_date, end=end_date, progress=False)

            if hist.empty:
                logger.warning(f"データなし: {symbol}")
                return None

            # データを整形
            hist.reset_index(inplace=True)
            hist["symbol"] = symbol.replace(".T", "")  # サフィックスを除去

            return hist
        except Exception as e:
            logger.error(f"データ取得エラー {symbol}: {e}")
            return None

    def save_stock_data(self, df, symbol):
        """株価データをデータベースに保存"""
        if df is None or df.empty:
            return 0

        connection = self.get_connection()
        saved_count = 0

        try:
            with connection.cursor() as cursor:
                for _, row in df.iterrows():
                    try:
                        # 重複チェック
                        cursor.execute(
                            """
                            SELECT COUNT(*) FROM stock_price_history 
                            WHERE symbol = %s AND date = %s
                        """,
                            (
                                symbol.replace(".T", ""),
                                row["Date"].strftime("%Y-%m-%d"),
                            ),
                        )

                        if cursor.fetchone()[0] > 0:
                            continue  # 既存データはスキップ

                        # データ挿入
                        cursor.execute(
                            """
                            INSERT INTO stock_price_history 
                            (symbol, date, open_price, high_price, low_price, close_price, 
                             adjusted_close, volume, data_source, created_at)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        """,
                            (
                                symbol.replace(".T", ""),
                                row["Date"].strftime("%Y-%m-%d"),
                                float(row["Open"]) if pd.notna(row["Open"]) else None,
                                float(row["High"]) if pd.notna(row["High"]) else None,
                                float(row["Low"]) if pd.notna(row["Low"]) else None,
                                float(row["Close"]) if pd.notna(row["Close"]) else None,
                                (
                                    float(row["Adj Close"])
                                    if pd.notna(row["Adj Close"])
                                    else None
                                ),
                                int(row["Volume"]) if pd.notna(row["Volume"]) else None,
                                "yfinance",
                                datetime.now(),
                            ),
                        )
                        saved_count += 1
                    except Exception as e:
                        logger.error(f"データ保存エラー {symbol} {row['Date']}: {e}")
                        continue

                connection.commit()
                logger.info(f"{symbol}: {saved_count}件のデータを保存")

        except Exception as e:
            logger.error(f"データベース操作エラー {symbol}: {e}")
            connection.rollback()
        finally:
            connection.close()

        return saved_count

    def generate_simple_predictions(self, symbol, latest_price):
        """シンプルな予測データを生成"""
        connection = self.get_connection()
        prediction_count = 0

        try:
            with connection.cursor() as cursor:
                # 既存の予測をクリア
                cursor.execute(
                    """
                    UPDATE stock_predictions 
                    SET is_active = 0 
                    WHERE symbol = %s
                """,
                    (symbol.replace(".T", ""),),
                )

                # 今後7日間の予測を生成
                for i in range(1, 8):
                    prediction_date = datetime.now() + timedelta(days=i)

                    # シンプルなランダムウォークモデル
                    change_percent = random.uniform(-0.05, 0.05)  # ±5%の変動
                    predicted_price = latest_price * (1 + change_percent)
                    confidence = random.uniform(0.6, 0.8)

                    cursor.execute(
                        """
                        INSERT INTO stock_predictions 
                        (symbol, prediction_date, created_at, predicted_price, 
                         predicted_change, predicted_change_percent, confidence_score,
                         model_type, model_version, prediction_horizon, is_active)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """,
                        (
                            symbol.replace(".T", ""),
                            prediction_date,
                            datetime.now(),
                            predicted_price,
                            predicted_price - latest_price,
                            change_percent * 100,
                            confidence,
                            "simple_trend",
                            "1.0.0",
                            i,
                            True,
                        ),
                    )
                    prediction_count += 1

                connection.commit()
                logger.info(f"{symbol}: {prediction_count}件の予測を生成")

        except Exception as e:
            logger.error(f"予測生成エラー {symbol}: {e}")
            connection.rollback()
        finally:
            connection.close()

        return prediction_count

    def execute(self):
        """データパイプライン実行"""
        logger.info("=== データパイプライン開始 ===")

        symbols = self.get_active_symbols()
        total_processed = 0
        total_saved = 0
        total_predictions = 0

        for symbol in symbols:
            try:
                logger.info(f"処理中: {symbol}")

                # 株価データ取得
                stock_data = self.fetch_stock_data(symbol)

                if stock_data is not None and not stock_data.empty:
                    # データベースに保存
                    saved_count = self.save_stock_data(stock_data, symbol)
                    total_saved += saved_count

                    # 最新価格で予測生成
                    latest_price = float(stock_data["Close"].iloc[-1])
                    pred_count = self.generate_simple_predictions(symbol, latest_price)
                    total_predictions += pred_count

                total_processed += 1

                # レート制限対策
                time.sleep(0.1)

            except Exception as e:
                logger.error(f"銘柄処理エラー {symbol}: {e}")
                continue

        logger.info(f"=== データパイプライン完了 ===")
        logger.info(f"処理銘柄数: {total_processed}")
        logger.info(f"保存データ数: {total_saved}")
        logger.info(f"生成予測数: {total_predictions}")

        return {
            "processed_symbols": total_processed,
            "saved_records": total_saved,
            "generated_predictions": total_predictions,
        }


# 互換性のためのエイリアス
DataPipelineService = SimpleDataPipelineService
