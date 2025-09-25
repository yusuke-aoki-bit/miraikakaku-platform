#!/usr/bin/env python3
"""
新規銘柄をデータベースに登録
365銘柄 → 545銘柄への拡張分をDBに登録
"""

import psycopg2
import psycopg2.extras
import yfinance as yf
import logging
import time
from datetime import datetime
from typing import List, Dict, Set

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SymbolDatabaseRegistrar:
    """新規銘柄をデータベースに登録するクラス"""

    def __init__(self):
        self.db_config = {
            "host": "34.173.9.214",
            "user": "postgres",
            "password": "miraikakaku-postgres-secure-2024",
            "database": "miraikakaku",
            "port": 5432
        }

    def get_connection(self):
        """データベース接続を取得"""
        return psycopg2.connect(**self.db_config)

    def get_existing_symbols(self) -> Set[str]:
        """既存のDB内銘柄を取得"""
        try:
            connection = self.get_connection()
            with connection.cursor() as cursor:
                cursor.execute("SELECT symbol FROM stock_master WHERE is_active = 1")
                existing = set(row[0] for row in cursor.fetchall())
            connection.close()
            logger.info(f"DB内既存銘柄数: {len(existing)}")
            return existing
        except Exception as e:
            logger.error(f"既存銘柄取得エラー: {e}")
            return set()

    def load_expanded_symbols(self) -> List[str]:
        """拡張銘柄リストを読み込み"""
        try:
            with open('/mnt/c/Users/yuuku/cursor/miraikakaku/miraikakakubatch/expanded_verified_symbols.txt', 'r') as f:
                symbols = [line.strip() for line in f if line.strip()]
            logger.info(f"拡張銘柄リスト: {len(symbols)}銘柄")
            return symbols
        except Exception as e:
            logger.error(f"拡張銘柄リスト読み込みエラー: {e}")
            return []

    def get_symbol_info(self, symbol: str) -> Dict:
        """yfinanceから銘柄情報を取得"""
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            hist = ticker.history(period='5d')

            if hist.empty:
                return None

            latest_data = hist.iloc[-1]

            # 国・取引所の判定
            country = self.get_country_from_symbol(symbol)
            exchange = self.get_exchange_from_symbol(symbol)

            return {
                'symbol': symbol,
                'name': info.get('longName', info.get('shortName', symbol))[:200],
                'exchange': exchange,
                'sector': info.get('sector', 'Unknown')[:100] if info.get('sector') else 'Unknown',
                'industry': info.get('industry', 'Unknown')[:100] if info.get('industry') else 'Unknown',
                'country': country,
                'market_cap': info.get('marketCap', 0),
                'current_price': float(latest_data['Close']),
                'volume': int(latest_data['Volume']) if latest_data['Volume'] else 0,
                'date': hist.index[-1].strftime('%Y-%m-%d')
            }

        except Exception as e:
            logger.warning(f"銘柄情報取得エラー {symbol}: {e}")
            return None

    def get_country_from_symbol(self, symbol: str) -> str:
        """シンボルから国を判定"""
        if '.T' in symbol:
            return 'JP'
        elif '.SW' in symbol or '.DE' in symbol:
            return 'CH' if '.SW' in symbol else 'DE'
        elif '.L' in symbol:
            return 'UK'
        elif '.PA' in symbol:
            return 'FR'
        elif '.AS' in symbol:
            return 'NL'
        elif '.CO' in symbol:
            return 'DK'
        elif '.KS' in symbol:
            return 'KR'
        elif '.TO' in symbol:
            return 'CA'
        elif '.AX' in symbol:
            return 'AU'
        else:
            return 'US'

    def get_exchange_from_symbol(self, symbol: str) -> str:
        """シンボルから取引所を判定"""
        if '.T' in symbol:
            return 'TSE'
        elif '.SW' in symbol:
            return 'SWX'
        elif '.DE' in symbol:
            return 'XETRA'
        elif '.L' in symbol:
            return 'LSE'
        elif '.PA' in symbol:
            return 'EPA'
        elif '.AS' in symbol:
            return 'AMS'
        elif '.CO' in symbol:
            return 'CSE'
        elif '.KS' in symbol:
            return 'KRX'
        elif '.TO' in symbol:
            return 'TSX'
        elif '.AX' in symbol:
            return 'ASX'
        else:
            return 'NASDAQ'

    def register_symbol_to_db(self, symbol_info: Dict) -> bool:
        """銘柄をデータベースに登録"""
        try:
            connection = self.get_connection()

            with connection.cursor() as cursor:
                # stock_master に登録
                cursor.execute("""
                    INSERT INTO stock_master
                    (symbol, name, exchange, sector, industry, country, created_at, updated_at, is_active)
                    VALUES (%s, %s, %s, %s, %s, %s, NOW(), NOW(), 1)
                    ON DUPLICATE KEY UPDATE
                    name = VALUES(name),
                    exchange = VALUES(exchange),
                    sector = VALUES(sector),
                    industry = VALUES(industry),
                    country = VALUES(country),
                    updated_at = NOW()
                """, (
                    symbol_info['symbol'],
                    symbol_info['name'],
                    symbol_info['exchange'],
                    symbol_info['sector'],
                    symbol_info['industry'],
                    symbol_info['country']
                ))

                # stock_price_history に初期価格データを登録
                cursor.execute("""
                    INSERT INTO stock_price_history
                    (symbol, date, open_price, high_price, low_price, close_price, volume,
                     data_source, created_at, updated_at, is_valid, data_quality_score)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW(), 1, 0.95)
                    ON DUPLICATE KEY UPDATE
                    close_price = VALUES(close_price),
                    volume = VALUES(volume),
                    updated_at = NOW()
                """, (
                    symbol_info['symbol'],
                    symbol_info['date'],
                    symbol_info['current_price'],  # open として current_price を使用
                    symbol_info['current_price'],  # high として current_price を使用
                    symbol_info['current_price'],  # low として current_price を使用
                    symbol_info['current_price'],
                    symbol_info['volume'],
                    'Yahoo Finance - Initial Registration'
                ))

            connection.commit()
            connection.close()
            return True

        except Exception as e:
            logger.error(f"DB登録エラー {symbol_info['symbol']}: {e}")
            return False

    def register_new_symbols(self):
        """新規銘柄を一括登録"""
        logger.info("🚀 新規銘柄データベース登録開始")

        # 既存銘柄とファイル銘柄を比較
        existing_symbols = self.get_existing_symbols()
        all_symbols = self.load_expanded_symbols()

        # 新規銘柄を特定
        new_symbols = [s for s in all_symbols if s not in existing_symbols]
        logger.info(f"新規登録対象: {len(new_symbols)}銘柄")

        if not new_symbols:
            logger.info("✅ 新規登録対象銘柄なし")
            return

        # 各銘柄を登録
        success_count = 0
        error_count = 0

        for i, symbol in enumerate(new_symbols, 1):
            logger.info(f"処理中 ({i}/{len(new_symbols)}): {symbol}")

            # 銘柄情報取得
            symbol_info = self.get_symbol_info(symbol)
            if not symbol_info:
                error_count += 1
                logger.warning(f"❌ {symbol}: データ取得失敗")
                continue

            # DB登録
            if self.register_symbol_to_db(symbol_info):
                success_count += 1
                logger.info(f"✅ {symbol}: {symbol_info['name']} (${symbol_info['current_price']:.2f})")
            else:
                error_count += 1

            # レート制限対策
            time.sleep(0.2)

        # 結果サマリー
        logger.info(f"""
        ==========================================
        新規銘柄データベース登録完了
        ==========================================
        登録対象: {len(new_symbols)}銘柄
        成功登録: {success_count}銘柄
        エラー: {error_count}銘柄

        データベース内総銘柄数: {len(existing_symbols) + success_count}銘柄
        ==========================================
        """)

        return {
            'target_count': len(new_symbols),
            'success_count': success_count,
            'error_count': error_count,
            'total_db_symbols': len(existing_symbols) + success_count
        }

def main():
    """メイン実行"""
    registrar = SymbolDatabaseRegistrar()
    results = registrar.register_new_symbols()

    if results:
        print(f"""
        ✅ データベース登録完了

        📊 結果:
        - 新規登録: {results['success_count']}銘柄
        - 登録エラー: {results['error_count']}銘柄
        - DB内総銘柄数: {results['total_db_symbols']}銘柄

        すべて実在・検証済みの銘柄です。
        """)

if __name__ == "__main__":
    main()