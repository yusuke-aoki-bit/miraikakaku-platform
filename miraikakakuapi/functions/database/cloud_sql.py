"""
Cloud SQL接続とデータベース操作
本格的なデータベース統合機能
"""

import os
import logging
from typing import Optional, Dict, List, Any
from datetime import datetime
import json

import sqlalchemy
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import NullPool
from google.cloud.sql.connector import Connector
import pandas as pd

logger = logging.getLogger(__name__)


class CloudSQLManager:
    """Cloud SQL接続管理クラス"""

    def __init__(self):
        self.connector = None
        self.engine = None
        self.SessionLocal = None
        self._initialize_connection()

    def _initialize_connection(self):
        """データベース接続を初期化"""
        try:
            # Cloud SQL接続情報
            project_id = os.getenv("GOOGLE_CLOUD_PROJECT", "pricewise-huqkr")
            region = os.getenv("CLOUD_SQL_REGION", "us-central1")
            instance_name = os.getenv("CLOUD_SQL_INSTANCE", "miraikakaku")
            database_name = os.getenv("CLOUD_SQL_DATABASE", "miraikakaku_prod")
            db_user = os.getenv("CLOUD_SQL_USER", "root")
            db_password = os.getenv("CLOUD_SQL_PASSWORD")

            # Cloud SQL Connectorを使用
            self.connector = Connector()

            def get_conn():
                conn = self.connector.connect(
                    f"{project_id}:{region}:{instance_name}",
                    "pymysql",
                    user=db_user,
                    password=db_password,
                    db=database_name,
                )
                return conn

            # SQLAlchemy エンジンの作成
            self.engine = create_engine(
                "mysql+pymysql://",
                creator=get_conn,
                poolclass=NullPool,  # Cloud Runでは接続プールを無効化
                echo=False,
            )

            # セッションファクトリー作成
            self.SessionLocal = sessionmaker(
                autocommit=False, autoflush=False, bind=self.engine
            )

            # 接続テスト
            with self.engine.connect() as conn:
                result = conn.execute(text("SELECT 1"))
                logger.info("Cloud SQL connection established successfully")

        except Exception as e:
            logger.error(f"Failed to connect to Cloud SQL: {e}")
            # フォールバック: SQLite接続
            self._fallback_to_sqlite()

    def _fallback_to_sqlite(self):
        """SQLiteへのフォールバック"""
        logger.warning("Falling back to SQLite database")
        sqlite_path = os.getenv("SQLITE_PATH", "/tmp/miraikakaku.db")
        self.engine = create_engine(f"sqlite:///{sqlite_path}")
        self.SessionLocal = sessionmaker(
            autocommit=False, autoflush=False, bind=self.engine
        )

    def get_session(self) -> Session:
        """データベースセッション取得"""
        return self.SessionLocal()

    def close_connection(self):
        """接続をクローズ"""
        if self.connector:
            self.connector.close()


# グローバルインスタンス
db_manager = CloudSQLManager()


def get_db():
    """データベースセッション依存性注入"""
    db = db_manager.get_session()
    try:
        yield db
    finally:
        db.close()


class StockDataRepository:
    """株価データリポジトリ"""

    def __init__(self, db_session: Session = None):
        self.db = db_session or db_manager.get_session()

    def insert_stock_prices(self, symbol: str,
                            price_data: pd.DataFrame) -> int:
        """株価データを挿入"""
        try:
            records_inserted = 0

            for index, row in price_data.iterrows():
                # 重複チェックと挿入
                insert_query = text(
                    """
                    INSERT IGNORE INTO stock_prices
                    (symbol, date, open_price, high_price, low_price, close_price, volume, adjusted_close)
                    VALUES (:symbol, :date, :open_price, :high_price, :low_price, :close_price, :volume, :adjusted_close)
                """
                )

                result = self.db.execute(
                    insert_query,
                    {
                        "symbol": symbol,
                        "date": index.strftime("%Y-%m-%d"),
                        "open_price": float(row.get("Open", 0)),
                        "high_price": float(row.get("High", 0)),
                        "low_price": float(row.get("Low", 0)),
                        "close_price": float(row.get("Close", 0)),
                        "volume": int(row.get("Volume", 0)),
                        "adjusted_close": float(
                            row.get("Adj Close", row.get("Close", 0))
                        ),
                    },
                )

                if result.rowcount > 0:
                    records_inserted += 1

            self.db.commit()
            logger.info(
                f"Inserted {records_inserted} price records for {symbol}")
            return records_inserted

        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to insert stock prices for {symbol}: {e}")
            raise

    def get_stock_prices(
        self, symbol: str, start_date: str = None, end_date: str = None
    ) -> pd.DataFrame:
        """株価データを取得"""
        try:
            query = """
                SELECT date, open_price, high_price, low_price, close_price, volume, adjusted_close
                FROM stock_prices
                WHERE symbol = :symbol
            """
            params = {"symbol": symbol}

            if start_date:
                query += " AND date >= :start_date"
                params["start_date"] = start_date

            if end_date:
                query += " AND date <= :end_date"
                params["end_date"] = end_date

            query += " ORDER BY date ASC"

            df = pd.read_sql(query, self.db.bind, params=params)

            if not df.empty:
                df["date"] = pd.to_datetime(df["date"])
                df.set_index("date", inplace=True)
                # カラム名をyfinance形式に合わせる
                df.columns = [
                    "Open",
                    "High",
                    "Low",
                    "Close",
                    "Volume",
                    "Adj Close"]

            return df

        except Exception as e:
            logger.error(f"Failed to get stock prices for {symbol}: {e}")
            return pd.DataFrame()

    def insert_predictions(
            self, predictions_data: List[Dict[str, Any]]) -> int:
        """予測結果を挿入"""
        try:
            records_inserted = 0

            insert_query = text(
                """
                INSERT INTO stock_predictions
                (symbol, prediction_date, prediction_days, current_price, predicted_price,
                 confidence_score, prediction_range_low, prediction_range_high,
                 model_version, model_accuracy, features_used)
                VALUES (:symbol, :prediction_date, :prediction_days, :current_price, :predicted_price,
                        :confidence_score, :prediction_range_low, :prediction_range_high,
                        :model_version, :model_accuracy, :features_used)
            """
            )

            for pred in predictions_data:
                predicted_prices = pred.get("predicted_prices", [])
                if predicted_prices:
                    self.db.execute(
                        insert_query,
                        {
                            "symbol": pred["symbol"],
                            "prediction_date": datetime.now().date(),
                            "prediction_days": pred.get("prediction_days", 7),
                            "current_price": pred.get("current_price", 0),
                            # 最終日の予測価格
                            "predicted_price": predicted_prices[-1],
                            "confidence_score": pred.get("confidence_score", 0),
                            "prediction_range_low": min(
                                pred.get("prediction_range", {}).get("low", [])
                            ),
                            "prediction_range_high": max(
                                pred.get(
                                    "prediction_range", {}).get(
                                    "high", [])
                            ),
                            "model_version": pred.get("model_version", "LSTM_v1.0"),
                            "model_accuracy": pred.get("model_accuracy", 0),
                            "features_used": json.dumps(pred.get("features_used", [])),
                        },
                    )
                    records_inserted += 1

            self.db.commit()
            logger.info(f"Inserted {records_inserted} prediction records")
            return records_inserted

        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to insert predictions: {e}")
            raise

    def get_latest_predictions(self, symbol: str = None,
                               limit: int = 10) -> List[Dict]:
        """最新の予測結果を取得"""
        try:
            query = """
                SELECT symbol, prediction_date, prediction_days, current_price, predicted_price,
                       confidence_score, prediction_range_low, prediction_range_high,
                       model_version, created_at
                FROM stock_predictions
            """
            params = {}

            if symbol:
                query += " WHERE symbol = :symbol"
                params["symbol"] = symbol

            query += " ORDER BY created_at DESC LIMIT :limit"
            params["limit"] = limit

            result = self.db.execute(text(query), params)
            predictions = []

            for row in result:
                predictions.append(
                    {
                        "symbol": row.symbol,
                        "prediction_date": row.prediction_date,
                        "prediction_days": row.prediction_days,
                        "current_price": float(row.current_price),
                        "predicted_price": float(row.predicted_price),
                        "confidence_score": float(row.confidence_score),
                        "prediction_range": {
                            "low": float(row.prediction_range_low),
                            "high": float(row.prediction_range_high),
                        },
                        "model_version": row.model_version,
                        "created_at": row.created_at,
                    }
                )

            return predictions

        except Exception as e:
            logger.error(f"Failed to get predictions: {e}")
            return []

    def insert_batch_log(self, batch_type: str, status: str, **kwargs) -> int:
        """バッチログを挿入"""
        try:
            insert_query = text(
                """
                INSERT INTO batch_logs
                (batch_type, status, records_processed, error_message, details)
                VALUES (:batch_type, :status, :records_processed, :error_message, :details)
            """
            )

            result = self.db.execute(
                insert_query,
                {
                    "batch_type": batch_type,
                    "status": status,
                    "records_processed": kwargs.get("records_processed", 0),
                    "error_message": kwargs.get("error_message"),
                    "details": json.dumps(kwargs.get("details", {})),
                },
            )

            self.db.commit()
            return result.lastrowid

        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to insert batch log: {e}")
            raise

    def update_batch_log(self, log_id: int, status: str, **kwargs):
        """バッチログを更新"""
        try:
            update_query = text(
                """
                UPDATE batch_logs
                SET status = :status, end_time = CURRENT_TIMESTAMP,
                    records_processed = :records_processed, error_message = :error_message
                WHERE id = :log_id
            """
            )

            self.db.execute(
                update_query,
                {
                    "log_id": log_id,
                    "status": status,
                    "records_processed": kwargs.get("records_processed", 0),
                    "error_message": kwargs.get("error_message"),
                },
            )

            self.db.commit()

        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to update batch log: {e}")
            raise

    def insert_analysis_report(self, report_data: Dict[str, Any]) -> int:
        """分析レポートを挿入"""
        try:
            insert_query = text(
                """
                INSERT INTO analysis_reports
                (report_type, report_date, symbols_analyzed, market_sentiment,
                 top_performers, predictions_accuracy, key_insights, report_data)
                VALUES (:report_type, :report_date, :symbols_analyzed, :market_sentiment,
                        :top_performers, :predictions_accuracy, :key_insights, :report_data)
            """
            )

            result = self.db.execute(
                insert_query,
                {
                    "report_type": "daily_analysis",
                    "report_date": datetime.now().date(),
                    "symbols_analyzed": json.dumps(
                        report_data.get("symbols_analyzed", [])
                    ),
                    "market_sentiment": report_data.get("market_sentiment", "neutral"),
                    "top_performers": json.dumps(report_data.get("top_performers", [])),
                    "predictions_accuracy": report_data.get("predictions_accuracy", 0),
                    "key_insights": json.dumps(report_data.get("key_insights", [])),
                    "report_data": json.dumps(report_data),
                },
            )

            self.db.commit()
            return result.lastrowid

        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to insert analysis report: {e}")
            raise

    def get_stock_symbols(self, active_only: bool = True) -> List[str]:
        """登録済み株式シンボル一覧を取得"""
        try:
            query = "SELECT symbol FROM stock_master"
            if active_only:
                query += " WHERE is_active = 1"

            result = self.db.execute(text(query))
            return [row.symbol for row in result]

        except Exception as e:
            logger.error(f"Failed to get stock symbols: {e}")
            return []

    def __del__(self):
        """デストラクタ"""
        if hasattr(self, "db") and self.db:
            self.db.close()
