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
from sqlalchemy.pool import NullPool, QueuePool
from google.cloud.sql.connector import Connector
import pandas as pd

from .secure_config import get_secure_db_config, get_secure_database_url

logger = logging.getLogger(__name__)


class CloudSQLManager:
    """Cloud SQL接続管理クラス"""

    def __init__(self):
        self.connector = None
        self.engine = None
        self.SessionLocal = None
        self.connection_error = None
        self._initialize_connection()

    def _initialize_connection(self):
        """データベース接続を初期化（Secure Config使用）"""
        try:
            # 環境変数から接続情報取得
            database_url = os.getenv("DATABASE_URL")

            if database_url:
                # DATABASE_URLが設定されている場合は直接接続を試行
                logger.info("Using DATABASE_URL for direct connection")
                self.engine = create_engine(
                    database_url,
                    poolclass=QueuePool,
                    pool_size=20,  # 最適化: pool_sizeを10から20に増加
                    max_overflow=40,  # 最適化: max_overflowを20から40に増加
                    pool_timeout=30,
                    pool_recycle=3600,
                    pool_pre_ping=True,
                    echo=False,
                )
            else:
                # Secure Config使用（Secret Manager統合）
                try:
                    secure_db_url = get_secure_database_url()
                    logger.info("Using secure database configuration from Secret Manager")
                    self.engine = create_engine(
                        secure_db_url,
                        poolclass=QueuePool,
                        pool_size=20,
                        max_overflow=40,
                        pool_timeout=30,
                        pool_recycle=3600,
                        pool_pre_ping=True,
                        echo=False,
                    )
                except Exception as secure_error:
                    logger.warning(f"Secure config failed, falling back to legacy method: {secure_error}")

                    # Legacy Cloud SQL Connector（フォールバック）
                    project_id = os.getenv("GCP_PROJECT_ID", os.getenv("GOOGLE_CLOUD_PROJECT", "pricewise-huqkr"))
                    region = os.getenv("CLOUD_SQL_REGION", "us-central1")
                    instance_name = os.getenv("CLOUD_SQL_INSTANCE", "miraikakaku-postgres")
                    database_name = os.getenv("POSTGRES_DATABASE", os.getenv("CLOUD_SQL_DATABASE", "miraikakaku"))
                    db_user = os.getenv("POSTGRES_USER", os.getenv("CLOUD_SQL_USER"))
                    db_password = os.getenv("POSTGRES_PASSWORD", os.getenv("CLOUD_SQL_PASSWORD"))

                    # Clean password to avoid encoding issues
                    if db_password:
                        db_password = ''.join(char for char in db_password if ord(char) >= 32 and ord(char) != 127)

                    # Cloud SQL Connectorを使用
                    self.connector = Connector()

                    def get_conn():
                        conn = self.connector.connect(
                            f"{project_id}:{region}:{instance_name}",
                            "pg8000",
                            user=db_user,
                            password=db_password,
                            db=database_name,
                        )
                        return conn

                    # SQLAlchemy エンジンの作成
                    self.engine = create_engine(
                        "postgresql+pg8000://",
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
            # Store error for later retrieval but don't raise
            self.connection_error = str(e)
            logger.warning("Database connection failed, continuing with limited functionality")

    def is_connected(self) -> bool:
        """Check if database connection is available"""
        return self.SessionLocal is not None and self.connection_error is None

    def get_connection_error(self) -> str:
        """Get the connection error message if any"""
        return self.connection_error

    def get_session(self) -> Session:
        """データベースセッション取得"""
        if not self.is_connected():
            raise ConnectionError(f"Database not available: {self.connection_error}")
        return self.SessionLocal()

    def close_connection(self):
        """接続をクローズ"""
        if self.connector:
            self.connector.close()


# グローバルインスタンス
db_manager = CloudSQLManager()


def get_db():
    """データベースセッション依存性注入"""
    if not db_manager.is_connected():
        raise ConnectionError("Database connection not available")
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
                # PostgreSQL用のON CONFLICT構文
                insert_query = text(
                    """
                    INSERT INTO stock_prices
                    (symbol, date, open_price, high_price, low_price, close_price, volume, adjusted_close)
                    VALUES (:symbol, :date, :open_price, :high_price, :low_price, :close_price, :volume, :adjusted_close)
                    ON CONFLICT (symbol, date) DO NOTHING
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
        """予測結果を挿入（既存スキーマ対応）"""
        try:
            records_inserted = 0

            insert_query = text(
                """
                INSERT INTO stock_predictions
                (symbol, prediction_date, predicted_price, predicted_change,
                 predicted_change_percent, confidence_score, model_type,
                 model_version, prediction_horizon, is_active, created_at)
                VALUES (:symbol, :prediction_date, :predicted_price, :predicted_change,
                        :predicted_change_percent, :confidence_score, :model_type,
                        :model_version, :prediction_horizon, :is_active, :created_at)
            """
            )

            for pred in predictions_data:
                predicted_price = pred.get("predicted_price", 0)
                current_price = pred.get("current_price", 0)
                
                # 変化量と変化率を計算
                predicted_change = predicted_price - current_price if current_price > 0 else 0
                predicted_change_percent = (predicted_change / current_price * 100) if current_price > 0 else 0
                
                self.db.execute(
                    insert_query,
                    {
                        "symbol": pred["symbol"],
                        "prediction_date": datetime.now(),
                        "predicted_price": float(predicted_price),
                        "predicted_change": float(predicted_change),
                        "predicted_change_percent": float(predicted_change_percent),
                        "confidence_score": float(pred.get("confidence_score", 0)),
                        "model_type": pred.get("model_type", "LSTM-Integrated"),
                        "model_version": pred.get("model_version", "v1.0"),
                        "prediction_horizon": pred.get("prediction_horizon", 1),
                        "is_active": True,
                        "created_at": datetime.now()
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
        """最新の予測結果を取得（既存スキーマ対応）"""
        try:
            query = """
                SELECT symbol, prediction_date, predicted_price, predicted_change,
                       predicted_change_percent, confidence_score, model_type, 
                       model_version, prediction_horizon, is_active, created_at
                FROM stock_predictions
                WHERE is_active = true
            """
            params = {}

            if symbol:
                query += " AND symbol = :symbol"
                params["symbol"] = symbol

            query += " ORDER BY created_at DESC LIMIT :limit"
            params["limit"] = limit

            result = self.db.execute(text(query), params)
            predictions = []

            for row in result:
                predictions.append(
                    {
                        "symbol": row.symbol,
                        "prediction_date": row.prediction_date.strftime('%Y-%m-%d') if row.prediction_date else None,
                        "predicted_price": float(row.predicted_price) if row.predicted_price else 0,
                        "predicted_change": float(row.predicted_change) if row.predicted_change else 0,
                        "predicted_change_percent": float(row.predicted_change_percent) if row.predicted_change_percent else 0,
                        "confidence_score": float(row.confidence_score) if row.confidence_score else 0,
                        "model_type": row.model_type,
                        "model_version": row.model_version,
                        "prediction_horizon": f"{row.prediction_horizon}d" if row.prediction_horizon else "1d",
                        "is_active": bool(row.is_active),
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
                query += " WHERE is_active = true"  # PostgreSQL boolean true instead of 1

            result = self.db.execute(text(query))
            return [row.symbol for row in result]

        except Exception as e:
            logger.error(f"Failed to get stock symbols: {e}")
            return []

    def __del__(self):
        """デストラクタ"""
        if hasattr(self, "db") and self.db:
            self.db.close()
