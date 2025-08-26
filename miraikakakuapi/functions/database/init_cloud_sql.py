#!/usr/bin/env python3
"""
Cloud SQL データベース初期化スクリプト
スキーマ作成とマスターデータ投入
"""

from sqlalchemy import text
from database.cloud_sql import db_manager
import os
import sys
import logging
from pathlib import Path
from dotenv import load_dotenv

# 現在のディレクトリをPythonパスに追加
sys.path.append(str(Path(__file__).parent.parent))


load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def execute_sql_file(filepath: str):
    """SQLファイルを実行"""
    try:
        with open(filepath, "r", encoding="utf-8") as file:
            sql_content = file.read()

        # セッション取得
        session = db_manager.get_session()

        try:
            # SQL文を分割して実行
            statements = [
                stmt.strip() for stmt in sql_content.split(";") if stmt.strip()
            ]

            for statement in statements:
                if statement:
                    logger.info(f"Executing: {statement[:100]}...")
                    session.execute(text(statement))

            session.commit()
            logger.info(f"Successfully executed SQL file: {filepath}")

        except Exception as e:
            session.rollback()
            logger.error(f"Error executing SQL file {filepath}: {e}")
            raise

        finally:
            session.close()

    except Exception as e:
        logger.error(f"Failed to read or execute SQL file {filepath}: {e}")
        raise


def init_database():
    """データベース初期化"""
    logger.info("Starting Cloud SQL database initialization...")

    # スキーマファイルのパス
    schema_file = Path(__file__).parent / "schema.sql"

    try:
        # スキーマ適用
        if schema_file.exists():
            logger.info("Applying database schema...")
            execute_sql_file(str(schema_file))
        else:
            logger.error(f"Schema file not found: {schema_file}")
            return False

        logger.info("Database initialization completed successfully!")
        return True

    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        return False


def test_connection():
    """接続テスト"""
    try:
        session = db_manager.get_session()

        # 簡単なクエリ実行
        result = session.execute(text("SELECT 1 as test"))
        row = result.fetchone()

        if row and row.test == 1:
            logger.info("Database connection test successful!")

            # テーブル存在確認
            tables_query = """
                SELECT TABLE_NAME
                FROM INFORMATION_SCHEMA.TABLES
                WHERE TABLE_SCHEMA = DATABASE()
            """
            result = session.execute(text(tables_query))
            tables = [row[0] for row in result.fetchall()]

            logger.info(f"Found tables: {tables}")
            return True
        else:
            logger.error("Database connection test failed!")
            return False

    except Exception as e:
        logger.error(f"Connection test failed: {e}")
        return False

    finally:
        session.close()


def verify_data():
    """データ確認"""
    try:
        session = db_manager.get_session()

        # stock_master テーブルの確認
        result = session.execute(text("SELECT COUNT(*) as count FROM stock_master"))
        stock_count = result.fetchone().count
        logger.info(f"Stock master records: {stock_count}")

        # market_indices テーブルの確認
        result = session.execute(text("SELECT COUNT(*) as count FROM market_indices"))
        index_count = result.fetchone().count
        logger.info(f"Market indices records: {index_count}")

        return stock_count > 0

    except Exception as e:
        logger.error(f"Data verification failed: {e}")
        return False

    finally:
        session.close()


if __name__ == "__main__":
    logger.info("=== Cloud SQL Database Initialization ===")

    # 1. 接続テスト
    if not test_connection():
        logger.error("Connection test failed. Exiting.")
        sys.exit(1)

    # 2. データベース初期化
    if not init_database():
        logger.error("Database initialization failed. Exiting.")
        sys.exit(1)

    # 3. データ確認
    if verify_data():
        logger.info("Database initialization completed successfully!")
    else:
        logger.warning("Database initialized but data verification failed.")

    logger.info("=== Initialization Complete ===")
