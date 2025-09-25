"""
Stock Symbol Manager - 銘柄の確認と追加
PostgreSQL対応版
"""

import os
import sys
import logging
import psycopg2
from psycopg2.extras import RealDictCursor
import yfinance as yf
from datetime import datetime
from typing import List, Dict, Optional

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class StockSymbolManager:
    """銘柄マスタの管理クラス"""

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

    def verify_existing_symbols(self) -> Dict:
        """既存銘柄の確認"""
        try:
            # 既存銘柄数を取得
            self.cursor.execute("""
                SELECT
                    COUNT(*) as total,
                    COUNT(DISTINCT exchange) as exchanges,
                    COUNT(DISTINCT sector) as sectors
                FROM stock_master
                WHERE is_active = true
            """)
            stats = dict(self.cursor.fetchone())

            # 交換所別の統計
            self.cursor.execute("""
                SELECT exchange, COUNT(*) as count
                FROM stock_master
                WHERE is_active = true
                GROUP BY exchange
                ORDER BY count DESC
            """)
            exchange_stats = self.cursor.fetchall()

            logger.info(f"📊 既存銘柄統計:")
            logger.info(f"  - 総銘柄数: {stats['total']}")
            logger.info(f"  - 取引所数: {stats['exchanges']}")
            logger.info(f"  - セクター数: {stats['sectors']}")

            for exchange in exchange_stats[:5]:
                logger.info(f"  - {exchange['exchange']}: {exchange['count']}銘柄")

            return {
                'stats': stats,
                'exchanges': exchange_stats
            }

        except Exception as e:
            logger.error(f"❌ 銘柄確認エラー: {e}")
            return None

    def validate_symbol(self, symbol: str) -> Optional[Dict]:
        """銘柄の検証（Yahoo Finance）"""
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info

            if not info or 'symbol' not in info:
                return None

            return {
                'symbol': symbol,
                'company_name': info.get('longName', info.get('shortName', '')),
                'exchange': info.get('exchange', ''),
                'sector': info.get('sector', ''),
                'industry': info.get('industry', ''),
                'market_cap': info.get('marketCap', 0),
                'currency': info.get('currency', 'USD')
            }

        except Exception as e:
            logger.debug(f"Symbol validation failed for {symbol}: {e}")
            return None

    def add_new_symbols(self, symbols: List[str]) -> Dict:
        """新規銘柄の追加"""
        added = []
        skipped = []
        errors = []

        for symbol in symbols:
            try:
                # 既存チェック
                self.cursor.execute(
                    "SELECT symbol FROM stock_master WHERE symbol = %s",
                    (symbol,)
                )

                if self.cursor.fetchone():
                    skipped.append(symbol)
                    continue

                # 銘柄情報取得
                info = self.validate_symbol(symbol)
                if not info:
                    errors.append(symbol)
                    continue

                # データベースに追加
                self.cursor.execute("""
                    INSERT INTO stock_master (
                        symbol, company_name, exchange, sector,
                        industry, market_cap, currency, is_active,
                        created_at, updated_at
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    info['symbol'],
                    info['company_name'][:255] if info['company_name'] else None,
                    info['exchange'][:50] if info['exchange'] else None,
                    info['sector'][:100] if info['sector'] else None,
                    info['industry'][:100] if info['industry'] else None,
                    info['market_cap'],
                    info['currency'][:10] if info['currency'] else 'USD',
                    True,
                    datetime.now(),
                    datetime.now()
                ))

                added.append(symbol)
                logger.info(f"✅ 追加成功: {symbol} - {info.get('company_name', '')}")

            except Exception as e:
                logger.error(f"❌ 追加エラー {symbol}: {e}")
                errors.append(symbol)

        # コミット
        if added:
            self.connection.commit()

        return {
            'added': added,
            'skipped': skipped,
            'errors': errors,
            'summary': {
                'added_count': len(added),
                'skipped_count': len(skipped),
                'error_count': len(errors)
            }
        }

    def update_inactive_symbols(self) -> int:
        """非アクティブ銘柄の更新"""
        try:
            # 30日以上価格更新がない銘柄を非アクティブ化
            self.cursor.execute("""
                UPDATE stock_master
                SET is_active = false, updated_at = NOW()
                WHERE symbol IN (
                    SELECT sm.symbol
                    FROM stock_master sm
                    LEFT JOIN stock_price_history sph
                        ON sm.symbol = sph.symbol
                    WHERE sm.is_active = true
                    GROUP BY sm.symbol
                    HAVING MAX(sph.date) < NOW() - INTERVAL '30 days'
                        OR MAX(sph.date) IS NULL
                )
            """)

            affected = self.cursor.rowcount
            self.connection.commit()

            logger.info(f"📝 {affected}銘柄を非アクティブ化")
            return affected

        except Exception as e:
            logger.error(f"❌ 非アクティブ化エラー: {e}")
            self.connection.rollback()
            return 0


def main():
    """メイン処理"""
    logger.info("🚀 Stock Symbol Manager開始")

    # バッチモードの取得
    mode = os.getenv('BATCH_MODE', 'verify')

    manager = StockSymbolManager()

    if not manager.connect():
        logger.error("データベース接続失敗")
        sys.exit(1)

    try:
        if mode == 'verify':
            # 既存銘柄の確認
            result = manager.verify_existing_symbols()
            if result:
                logger.info(f"✅ 確認完了: {result['stats']['total']}銘柄")

        elif mode == 'add':
            # 新規銘柄の追加
            # 環境変数から銘柄リストを取得
            symbols_str = os.getenv('SYMBOLS_TO_ADD', '')
            if symbols_str:
                symbols = [s.strip() for s in symbols_str.split(',')]
                result = manager.add_new_symbols(symbols)
                logger.info(f"✅ 追加結果: {result['summary']}")
            else:
                # デフォルトの主要銘柄
                default_symbols = [
                    'AAPL', 'GOOGL', 'MSFT', 'AMZN', 'NVDA',
                    'TSLA', 'META', 'JPM', 'V', 'JNJ',
                    '7203.T', '9984.T', '6758.T', '8306.T', '9432.T'  # 日本株
                ]
                result = manager.add_new_symbols(default_symbols)
                logger.info(f"✅ デフォルト銘柄追加: {result['summary']}")

        elif mode == 'update':
            # 非アクティブ銘柄の更新
            count = manager.update_inactive_symbols()
            logger.info(f"✅ 更新完了: {count}銘柄")

        else:
            logger.warning(f"不明なモード: {mode}")

    except Exception as e:
        logger.error(f"❌ 処理エラー: {e}")
        sys.exit(1)

    finally:
        manager.disconnect()
        logger.info("✅ Stock Symbol Manager完了")


if __name__ == "__main__":
    main()