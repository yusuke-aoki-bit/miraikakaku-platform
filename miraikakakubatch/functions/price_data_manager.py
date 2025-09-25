"""
Price Data Manager - 価格情報の確認と追加
PostgreSQL対応版
"""

import os
import sys
import logging
import psycopg2
from psycopg2.extras import RealDictCursor, execute_batch
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict, Optional

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class PriceDataManager:
    """価格データの管理クラス"""

    def __init__(self):
        self.db_config = {
            'host': os.getenv('DB_HOST', '34.173.9.214'),
            'database': os.getenv('DB_NAME', 'miraikakaku'),
            'user': os.getenv('DB_USER', 'postgres'),
            'password': os.getenv('DB_PASSWORD', 'miraikakaku-secure-pass-2024'),
            'port': os.getenv('DB_PORT', '5432')
        }
        self.connection = None
        self.cursor = None

    def connect(self):
        """データベース接続"""
        try:
            self.connection = psycopg2.connect(**self.db_config)
            self.cursor = self.connection.cursor(cursor_factory=RealDictCursor)
            logger.info("✅ PostgreSQL接続成功")
            return True
        except Exception as e:
            logger.error(f"❌ PostgreSQL接続エラー: {e}")
            return False

    def disconnect(self):
        """データベース切断"""
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()

    def verify_price_coverage(self) -> Dict:
        """価格データカバレッジの確認"""
        try:
            # 全体統計
            self.cursor.execute("""
                SELECT
                    COUNT(DISTINCT symbol) as symbols_with_prices,
                    COUNT(*) as total_price_records,
                    MIN(date) as earliest_date,
                    MAX(date) as latest_date,
                    AVG(volume) as avg_volume
                FROM stock_prices
            """)
            overall_stats = dict(self.cursor.fetchone())

            # アクティブ銘柄の価格カバレッジ
            self.cursor.execute("""
                SELECT
                    sm.symbol,
                    sm.company_name,
                    COUNT(sph.date) as price_days,
                    MAX(sph.date) as last_update,
                    MIN(sph.date) as first_date
                FROM stock_master sm
                LEFT JOIN stock_prices sph ON sm.symbol = sph.symbol
                WHERE sm.is_active = true
                GROUP BY sm.symbol, sm.company_name
                ORDER BY price_days DESC
                LIMIT 20
            """)
            top_symbols = self.cursor.fetchall()

            # カバレッジ不足の銘柄
            self.cursor.execute("""
                SELECT
                    sm.symbol,
                    sm.company_name,
                    COUNT(sph.date) as price_days
                FROM stock_master sm
                LEFT JOIN stock_prices sph ON sm.symbol = sph.symbol
                WHERE sm.is_active = true
                GROUP BY sm.symbol, sm.company_name
                HAVING COUNT(sph.date) < 30
                LIMIT 20
            """)
            low_coverage = self.cursor.fetchall()

            logger.info(f"📊 価格データ統計:")
            logger.info(f"  - 価格データがある銘柄: {overall_stats['symbols_with_prices']}")
            logger.info(f"  - 総レコード数: {overall_stats['total_price_records']:,}")
            logger.info(f"  - データ期間: {overall_stats['earliest_date']} ~ {overall_stats['latest_date']}")
            logger.info(f"  - 平均出来高: {overall_stats['avg_volume']:,.0f}" if overall_stats['avg_volume'] else "  - 平均出来高: N/A")

            return {
                'overall': overall_stats,
                'top_symbols': top_symbols,
                'low_coverage': low_coverage
            }

        except Exception as e:
            logger.error(f"❌ カバレッジ確認エラー: {e}")
            return None

    def fetch_price_data(self, symbol: str, days: int = 180) -> Optional[pd.DataFrame]:
        """Yahoo Financeから価格データ取得"""
        try:
            ticker = yf.Ticker(symbol)
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)

            df = ticker.history(start=start_date, end=end_date)

            if df.empty:
                return None

            # カラム名を調整
            df.reset_index(inplace=True)
            df.columns = [col.lower() for col in df.columns]

            # 必要なカラムのみ選択
            required_cols = ['date', 'open', 'high', 'low', 'close', 'volume']
            df = df[required_cols]

            return df

        except Exception as e:
            logger.debug(f"価格データ取得失敗 {symbol}: {e}")
            return None

    def update_price_data(self, symbols: Optional[List[str]] = None) -> Dict:
        """価格データの更新"""
        if not symbols:
            # アクティブな銘柄を取得
            self.cursor.execute("""
                SELECT symbol FROM stock_master
                WHERE is_active = true
                LIMIT 100
            """)
            symbols = [row['symbol'] for row in self.cursor.fetchall()]

        updated = []
        failed = []
        records_added = 0

        for symbol in symbols:
            try:
                # 最新の価格日付を取得
                self.cursor.execute("""
                    SELECT MAX(date) as last_date
                    FROM stock_prices
                    WHERE symbol = %s
                """, (symbol,))

                result = self.cursor.fetchone()
                last_date = result['last_date'] if result and result['last_date'] else None

                # 取得期間の決定
                if last_date:
                    days_needed = (datetime.now().date() - last_date).days + 1
                    if days_needed <= 1:
                        logger.debug(f"✓ {symbol}: 既に最新")
                        continue
                else:
                    days_needed = 180  # 新規の場合は180日分

                # 価格データ取得
                df = self.fetch_price_data(symbol, days_needed)

                if df is None or df.empty:
                    failed.append(symbol)
                    continue

                # 既存データとの重複を除外
                if last_date:
                    df = df[df['date'].dt.date > last_date]

                if df.empty:
                    continue

                # データベースに保存
                records = []
                for _, row in df.iterrows():
                    records.append((
                        symbol,
                        row['date'].date(),
                        float(row['open']),
                        float(row['high']),
                        float(row['low']),
                        float(row['close']),
                        int(row['volume']) if pd.notna(row['volume']) else 0,
                        datetime.now()
                    ))

                if records:
                    execute_batch(self.cursor, """
                        INSERT INTO stock_prices
                        (symbol, date, open, high, low, close, volume, created_at)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                        ON CONFLICT (symbol, date) DO UPDATE
                        SET open = EXCLUDED.open,
                            high = EXCLUDED.high,
                            low = EXCLUDED.low,
                            close = EXCLUDED.close,
                            volume = EXCLUDED.volume,
                            updated_at = NOW()
                    """, records)

                    records_added += len(records)
                    updated.append(symbol)
                    logger.info(f"✅ {symbol}: {len(records)}レコード追加")

            except Exception as e:
                logger.error(f"❌ 更新エラー {symbol}: {e}")
                failed.append(symbol)

        # コミット
        if updated:
            self.connection.commit()

        return {
            'updated': updated,
            'failed': failed,
            'summary': {
                'updated_count': len(updated),
                'failed_count': len(failed),
                'records_added': records_added
            }
        }

    def check_data_gaps(self) -> List[Dict]:
        """データギャップの確認"""
        try:
            # 最近30日で欠落日がある銘柄を検出
            self.cursor.execute("""
                WITH date_series AS (
                    SELECT generate_series(
                        CURRENT_DATE - INTERVAL '30 days',
                        CURRENT_DATE,
                        '1 day'::interval
                    )::date AS date
                ),
                symbol_dates AS (
                    SELECT
                        sm.symbol,
                        ds.date
                    FROM stock_master sm
                    CROSS JOIN date_series ds
                    WHERE sm.is_active = true
                        AND EXTRACT(dow FROM ds.date) NOT IN (0, 6)  -- 土日除外
                ),
                actual_data AS (
                    SELECT symbol, date
                    FROM stock_prices
                    WHERE date >= CURRENT_DATE - INTERVAL '30 days'
                )
                SELECT
                    sd.symbol,
                    COUNT(*) as missing_days
                FROM symbol_dates sd
                LEFT JOIN actual_data ad
                    ON sd.symbol = ad.symbol AND sd.date = ad.date
                WHERE ad.symbol IS NULL
                GROUP BY sd.symbol
                HAVING COUNT(*) > 5
                ORDER BY missing_days DESC
                LIMIT 20
            """)

            gaps = self.cursor.fetchall()

            logger.info(f"📊 データギャップ検出:")
            for gap in gaps:
                logger.info(f"  - {gap['symbol']}: {gap['missing_days']}日欠落")

            return gaps

        except Exception as e:
            logger.error(f"❌ ギャップ確認エラー: {e}")
            return []


def main():
    """メイン処理"""
    logger.info("🚀 Price Data Manager開始")

    # バッチモードの取得
    mode = os.getenv('BATCH_MODE', 'verify')

    manager = PriceDataManager()

    if not manager.connect():
        logger.error("データベース接続失敗")
        sys.exit(1)

    try:
        if mode == 'verify':
            # 価格データカバレッジの確認
            result = manager.verify_price_coverage()
            if result:
                logger.info(f"✅ カバレッジ確認完了")

            # データギャップの確認
            gaps = manager.check_data_gaps()
            if gaps:
                logger.info(f"⚠️ {len(gaps)}銘柄にデータギャップあり")

        elif mode == 'update':
            # 価格データの更新
            symbols_str = os.getenv('SYMBOLS_TO_UPDATE', '')
            symbols = None

            if symbols_str:
                symbols = [s.strip() for s in symbols_str.split(',')]

            result = manager.update_price_data(symbols)
            logger.info(f"✅ 更新結果: {result['summary']}")

        else:
            logger.warning(f"不明なモード: {mode}")

    except Exception as e:
        logger.error(f"❌ 処理エラー: {e}")
        sys.exit(1)

    finally:
        manager.disconnect()
        logger.info("✅ Price Data Manager完了")


if __name__ == "__main__":
    main()