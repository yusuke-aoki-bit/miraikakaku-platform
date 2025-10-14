"""
セクター/業種データ取得スクリプト
===================================
全3,756銘柄のsector/industryデータをyfinanceから取得してDBに保存
"""
import psycopg2
from psycopg2.extras import RealDictCursor
import yfinance as yf
import time
import os
from dotenv import load_dotenv
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
import logging

# ログ設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

load_dotenv()

DB_CONFIG = {
    'host': 'localhost',
    'port': 5433,
    'database': 'miraikakaku',
    'user': 'postgres',
    'password': os.getenv('POSTGRES_PASSWORD', 'Miraikakaku2024!')
}

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    retry=retry_if_exception_type((psycopg2.OperationalError, psycopg2.DatabaseError)),
    reraise=True
)
def get_db_connection():
    """データベース接続を取得"""
    return psycopg2.connect(**DB_CONFIG)

def add_sector_industry_columns():
    """stock_masterテーブルにsector/industryカラムを追加"""
    conn = get_db_connection()
    cur = conn.cursor()

    try:
        logger.info("Adding sector and industry columns to stock_master table...")

        # sector列の追加
        cur.execute("""
            ALTER TABLE stock_master
            ADD COLUMN IF NOT EXISTS sector VARCHAR(100);
        """)

        # industry列の追加
        cur.execute("""
            ALTER TABLE stock_master
            ADD COLUMN IF NOT EXISTS industry VARCHAR(200);
        """)

        conn.commit()
        logger.info("✅ Columns added successfully")
    except Exception as e:
        logger.error(f"❌ Error adding columns: {e}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=5),
    reraise=False
)
def fetch_sector_industry(symbol: str) -> tuple:
    """yfinanceから銘柄のsector/industryを取得"""
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info

        sector = info.get('sector', None)
        industry = info.get('industry', None)

        if sector or industry:
            logger.debug(f"  {symbol}: sector={sector}, industry={industry}")

        return sector, industry
    except Exception as e:
        logger.debug(f"  {symbol}: Failed to fetch - {e}")
        return None, None

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    retry=retry_if_exception_type((psycopg2.OperationalError, psycopg2.DatabaseError)),
    reraise=True
)
def update_sector_industry(conn, symbol: str, sector: str, industry: str):
    """DBのsector/industryを更新"""
    cur = conn.cursor()
    try:
        cur.execute("""
            UPDATE stock_master
            SET sector = %s, industry = %s
            WHERE symbol = %s
        """, (sector, industry, symbol))
        conn.commit()
    except Exception as e:
        logger.error(f"Failed to update {symbol}: {e}")
        conn.rollback()
    finally:
        cur.close()

def fetch_all_sector_data(batch_size: int = 50):
    """全銘柄のsector/industryデータを取得してDBに保存"""
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    try:
        # アクティブな銘柄リストを取得
        cur.execute("""
            SELECT symbol, company_name, sector, industry
            FROM stock_master
            WHERE is_active = TRUE
            ORDER BY symbol
        """)
        stocks = cur.fetchall()
        total_stocks = len(stocks)

        logger.info(f"📊 Total stocks to process: {total_stocks}")

        # 既にsector/industryがあるかチェック
        cur.execute("""
            SELECT COUNT(*) as count
            FROM stock_master
            WHERE is_active = TRUE
            AND (sector IS NOT NULL OR industry IS NOT NULL)
        """)
        existing_count = cur.fetchone()['count']
        logger.info(f"✅ Already have data for: {existing_count}/{total_stocks} stocks")

        # sector/industryが未設定の銘柄のみ処理
        cur.execute("""
            SELECT symbol, company_name
            FROM stock_master
            WHERE is_active = TRUE
            AND sector IS NULL
            AND industry IS NULL
            ORDER BY symbol
        """)
        pending_stocks = cur.fetchall()
        pending_count = len(pending_stocks)

        logger.info(f"🔄 Pending stocks to fetch: {pending_count}")

        if pending_count == 0:
            logger.info("✅ All stocks already have sector/industry data!")
            return

        # バッチ処理
        updated_count = 0
        failed_count = 0

        for i, stock in enumerate(pending_stocks, 1):
            symbol = stock['symbol']
            company_name = stock['company_name']

            if i % batch_size == 0:
                logger.info(f"Progress: {i}/{pending_count} ({i/pending_count*100:.1f}%)")
                time.sleep(2)  # Rate limiting

            try:
                sector, industry = fetch_sector_industry(symbol)

                if sector or industry:
                    update_sector_industry(conn, symbol, sector, industry)
                    updated_count += 1
                    logger.info(f"✅ [{i}/{pending_count}] {symbol} ({company_name}): sector={sector}, industry={industry}")
                else:
                    failed_count += 1
                    logger.warning(f"⚠️  [{i}/{pending_count}] {symbol} ({company_name}): No data available")

                # Rate limiting (yfinance API制限対策)
                time.sleep(0.5)

            except Exception as e:
                failed_count += 1
                logger.error(f"❌ [{i}/{pending_count}] {symbol}: {e}")

        # 最終統計
        logger.info("=" * 60)
        logger.info("🎉 Data fetching completed!")
        logger.info(f"Total stocks processed: {pending_count}")
        logger.info(f"✅ Successfully updated: {updated_count}")
        logger.info(f"❌ Failed to fetch: {failed_count}")
        logger.info(f"📊 Success rate: {updated_count/pending_count*100:.1f}%")

        # 最終確認
        cur.execute("""
            SELECT COUNT(*) as count
            FROM stock_master
            WHERE is_active = TRUE
            AND (sector IS NOT NULL OR industry IS NOT NULL)
        """)
        final_count = cur.fetchone()['count']
        logger.info(f"📈 Final coverage: {final_count}/{total_stocks} stocks ({final_count/total_stocks*100:.1f}%)")

    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    logger.info("=" * 60)
    logger.info("Starting Sector/Industry Data Fetching...")
    logger.info("=" * 60)

    # Step 1: カラム追加
    add_sector_industry_columns()

    # Step 2: データ取得と保存
    fetch_all_sector_data(batch_size=50)

    logger.info("=" * 60)
    logger.info("✅ All tasks completed!")
    logger.info("=" * 60)
