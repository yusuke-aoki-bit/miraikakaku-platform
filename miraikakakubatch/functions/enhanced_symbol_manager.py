"""
Enhanced Stock Symbol Manager - 米国株・ETF・為替対応版
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


class EnhancedSymbolManager:
    """拡張版銘柄マスタの管理クラス（米国株・ETF・為替対応）"""

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

        # 主要銘柄リスト
        self.symbol_categories = {
            'us_mega_cap': [
                'AAPL', 'MSFT', 'GOOGL', 'GOOG', 'AMZN', 'NVDA', 'TSLA', 'META',
                'BRK-B', 'UNH', 'JNJ', 'V', 'WMT', 'XOM', 'JPM', 'PG', 'MA', 'HD',
                'CVX', 'LLY', 'ABBV', 'BAC', 'ORCL', 'KO', 'ASML', 'AVGO', 'MRK',
                'PEP', 'TMO', 'COST', 'ACN', 'MCD', 'ABT', 'CSCO', 'CRM', 'ADBE',
                'DHR', 'VZ', 'NEE', 'TXN', 'NKE', 'DIS', 'LIN', 'PM', 'WFC', 'BMY'
            ],
            'us_tech_stocks': [
                'NFLX', 'INTC', 'AMD', 'CRM', 'NOW', 'ORCL', 'IBM', 'QCOM', 'AMAT',
                'ADI', 'LRCX', 'KLAC', 'MRVL', 'MCHP', 'SNPS', 'CDNS', 'FTNT',
                'PANW', 'CRWD', 'ZS', 'OKTA', 'DDOG', 'NET', 'SNOW', 'PLTR'
            ],
            'us_financial': [
                'JPM', 'BAC', 'WFC', 'C', 'GS', 'MS', 'USB', 'PNC', 'TFC', 'COF',
                'AXP', 'BLK', 'SCHW', 'CB', 'MMC', 'AON', 'SPGI', 'MCO', 'ICE', 'CME'
            ],
            'us_healthcare': [
                'JNJ', 'UNH', 'PFE', 'ABBV', 'TMO', 'ABT', 'MRK', 'DHR', 'BMY',
                'LLY', 'AMGN', 'GILD', 'CVS', 'MDT', 'CI', 'ISRG', 'ZTS', 'SYK'
            ],
            'etf_broad_market': [
                'SPY', 'QQQ', 'IWM', 'VTI', 'VOO', 'VEA', 'VWO', 'IEFA', 'IEMG',
                'AGG', 'BND', 'TLT', 'IEF', 'LQD', 'HYG', 'EMB', 'VTEB', 'MUB'
            ],
            'etf_sector': [
                'XLK', 'XLF', 'XLV', 'XLE', 'XLI', 'XLY', 'XLP', 'XLU', 'XLB',
                'XLRE', 'XLC', 'GDX', 'SLV', 'GLD', 'USO', 'UNG', 'DBA', 'FXI',
                'EWJ', 'EWZ', 'EEM', 'VGK', 'FEZ', 'EWG', 'EWT', 'EWY', 'INDA'
            ],
            'etf_thematic': [
                'ARKK', 'ARKQ', 'ARKW', 'ARKG', 'ARKF', 'ICLN', 'PBW', 'KWEB',
                'SOXX', 'SMH', 'IBB', 'XBI', 'FINX', 'ROBO', 'ESPO', 'HERO',
                'UFO', 'MOON', 'HACK', 'CIBR', 'BUG', 'CLOU', 'SKYY', 'WFH'
            ],
            'forex_major': [
                'EURUSD=X', 'USDJPY=X', 'GBPUSD=X', 'AUDUSD=X', 'USDCAD=X',
                'USDCHF=X', 'NZDUSD=X', 'EURGBP=X', 'EURJPY=X', 'GBPJPY=X',
                'AUDJPY=X', 'CADJPY=X', 'CHFJPY=X', 'NZDJPY=X', 'EURCHF=X'
            ],
            'forex_emerging': [
                'USDCNY=X', 'USDINR=X', 'USDBRL=X', 'USDMXN=X', 'USDKRW=X',
                'USDTWD=X', 'USDSGD=X', 'USDHKD=X', 'USDTHB=X', 'USDPHP=X'
            ],
            'crypto_major': [
                'BTC-USD', 'ETH-USD', 'BNB-USD', 'XRP-USD', 'SOL-USD', 'ADA-USD',
                'AVAX-USD', 'DOGE-USD', 'DOT-USD', 'MATIC-USD', 'LTC-USD', 'BCH-USD'
            ]
        }

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

    def classify_symbol(self, symbol: str) -> str:
        """銘柄の分類を判定"""
        if '=X' in symbol:
            return 'FOREX'
        elif '-USD' in symbol:
            return 'CRYPTO'
        elif symbol in self.get_all_etf_symbols():
            return 'ETF'
        else:
            return 'STOCK'

    def get_all_etf_symbols(self) -> List[str]:
        """全ETF銘柄のリストを取得"""
        etf_symbols = []
        for category in ['etf_broad_market', 'etf_sector', 'etf_thematic']:
            etf_symbols.extend(self.symbol_categories[category])
        return etf_symbols

    def validate_symbol_enhanced(self, symbol: str) -> Optional[Dict]:
        """拡張版銘柄検証（アセットタイプ対応）"""
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info

            if not info or len(info) < 3:  # 最小限のデータチェック
                return None

            asset_type = self.classify_symbol(symbol)

            # アセットタイプ別のデータ取得
            if asset_type == 'FOREX':
                return {
                    'symbol': symbol,
                    'company_name': info.get('longName', f'{symbol.replace("=X", "")} Exchange Rate'),
                    'exchange': 'FOREX',
                    'sector': 'Currency',
                    'industry': 'Foreign Exchange',
                    'market_cap': 0,
                    'currency': 'USD',
                    'asset_type': asset_type
                }
            elif asset_type == 'CRYPTO':
                return {
                    'symbol': symbol,
                    'company_name': info.get('longName', info.get('shortName', symbol.replace('-USD', ' USD'))),
                    'exchange': 'CRYPTO',
                    'sector': 'Cryptocurrency',
                    'industry': 'Digital Currency',
                    'market_cap': info.get('marketCap', 0),
                    'currency': 'USD',
                    'asset_type': asset_type
                }
            elif asset_type == 'ETF':
                return {
                    'symbol': symbol,
                    'company_name': info.get('longName', info.get('shortName', '')),
                    'exchange': info.get('exchange', 'ETF'),
                    'sector': 'ETF',
                    'industry': info.get('category', 'Exchange Traded Fund'),
                    'market_cap': info.get('totalAssets', 0),
                    'currency': info.get('currency', 'USD'),
                    'asset_type': asset_type
                }
            else:  # STOCK
                return {
                    'symbol': symbol,
                    'company_name': info.get('longName', info.get('shortName', '')),
                    'exchange': info.get('exchange', ''),
                    'sector': info.get('sector', ''),
                    'industry': info.get('industry', ''),
                    'market_cap': info.get('marketCap', 0),
                    'currency': info.get('currency', 'USD'),
                    'asset_type': asset_type
                }

        except Exception as e:
            logger.debug(f"Symbol validation failed for {symbol}: {e}")
            return None

    def add_symbol_category(self, category: str) -> Dict:
        """特定カテゴリの銘柄を追加"""
        if category not in self.symbol_categories:
            return {'error': f'Unknown category: {category}'}

        symbols = self.symbol_categories[category]
        return self.add_new_symbols_enhanced(symbols)

    def add_new_symbols_enhanced(self, symbols: List[str]) -> Dict:
        """拡張版新規銘柄追加"""
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
                info = self.validate_symbol_enhanced(symbol)
                if not info:
                    errors.append(symbol)
                    continue

                # データベースに追加（既存スキーマに合わせて調整）
                self.cursor.execute("""
                    INSERT INTO stock_master (
                        symbol, company_name, name, exchange, sector,
                        market_cap, currency, country, is_active,
                        created_at, updated_at
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    info['symbol'],
                    info['company_name'][:255] if info['company_name'] else None,
                    info['company_name'][:255] if info['company_name'] else None,  # name フィールド
                    info['exchange'][:50] if info['exchange'] else None,
                    info['sector'][:100] if info['sector'] else None,
                    info['market_cap'] if info['market_cap'] else 0,
                    info['currency'][:10] if info['currency'] else 'USD',
                    'US' if info['asset_type'] in ['STOCK', 'ETF'] else info['asset_type'],  # country フィールド
                    True,
                    datetime.now(),
                    datetime.now()
                ))

                added.append(f"{symbol} ({info['asset_type']})")
                logger.info(f"✅ 追加成功: {symbol} - {info.get('company_name', '')} ({info['asset_type']})")

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

    def verify_coverage_by_asset_type(self) -> Dict:
        """アセットタイプ別カバレッジ確認"""
        try:
            # 全体統計
            self.cursor.execute("""
                SELECT
                    COUNT(*) as total,
                    COUNT(DISTINCT exchange) as exchanges,
                    COUNT(DISTINCT sector) as sectors
                FROM stock_master
                WHERE is_active = true
            """)
            overall_stats = dict(self.cursor.fetchone())

            # 取引所別統計（アセットタイプの代理）
            self.cursor.execute("""
                SELECT
                    CASE
                        WHEN exchange = 'FOREX' THEN 'FOREX'
                        WHEN exchange = 'CRYPTO' THEN 'CRYPTO'
                        WHEN sector = 'ETF' THEN 'ETF'
                        ELSE 'STOCK'
                    END as asset_type,
                    COUNT(*) as count
                FROM stock_master
                WHERE is_active = true
                GROUP BY asset_type
                ORDER BY count DESC
            """)
            asset_type_stats = self.cursor.fetchall()

            # 主要カテゴリの存在確認
            coverage_report = {}
            for category, symbols in self.symbol_categories.items():
                self.cursor.execute("""
                    SELECT COUNT(*) as existing_count
                    FROM stock_master
                    WHERE symbol = ANY(%s) AND is_active = true
                """, (symbols,))

                existing = self.cursor.fetchone()['existing_count']
                coverage_report[category] = {
                    'total_symbols': len(symbols),
                    'existing_symbols': existing,
                    'coverage_percent': round((existing / len(symbols)) * 100, 1)
                }

            logger.info(f"📊 拡張版銘柄統計:")
            logger.info(f"  - 総銘柄数: {overall_stats['total']}")

            for asset_stat in asset_type_stats:
                logger.info(f"  - {asset_stat['asset_type']}: {asset_stat['count']}銘柄")

            return {
                'overall': overall_stats,
                'asset_types': asset_type_stats,
                'category_coverage': coverage_report
            }

        except Exception as e:
            logger.error(f"❌ カバレッジ確認エラー: {e}")
            return None


def main():
    """メイン処理"""
    logger.info("🚀 Enhanced Symbol Manager開始（米国株・ETF・為替対応）")

    # バッチモードの取得
    mode = os.getenv('BATCH_MODE', 'verify')
    category = os.getenv('SYMBOL_CATEGORY', '')

    manager = EnhancedSymbolManager()

    if not manager.connect():
        logger.error("データベース接続失敗")
        sys.exit(1)

    try:
        if mode == 'verify':
            # 拡張版カバレッジ確認
            result = manager.verify_coverage_by_asset_type()
            if result:
                logger.info(f"✅ 拡張版確認完了")
                for category, stats in result['category_coverage'].items():
                    logger.info(f"  - {category}: {stats['coverage_percent']}% ({stats['existing_symbols']}/{stats['total_symbols']})")

        elif mode == 'add_category':
            # カテゴリ別追加
            if category:
                result = manager.add_symbol_category(category)
                logger.info(f"✅ {category} カテゴリ追加結果: {result['summary']}")
            else:
                logger.error("SYMBOL_CATEGORY環境変数が必要です")

        elif mode == 'add_all':
            # 全カテゴリ追加
            total_added = 0
            for category_name in manager.symbol_categories.keys():
                logger.info(f"🔄 {category_name} カテゴリを追加中...")
                result = manager.add_symbol_category(category_name)
                total_added += result['summary']['added_count']
                logger.info(f"  - 追加: {result['summary']['added_count']}, スキップ: {result['summary']['skipped_count']}, エラー: {result['summary']['error_count']}")

            logger.info(f"✅ 全カテゴリ追加完了: 合計 {total_added} 銘柄追加")

        else:
            logger.warning(f"不明なモード: {mode}")

    except Exception as e:
        logger.error(f"❌ 処理エラー: {e}")
        sys.exit(1)

    finally:
        manager.disconnect()
        logger.info("✅ Enhanced Symbol Manager完了")


if __name__ == "__main__":
    main()