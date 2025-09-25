"""
Stooq Japanese Stock Data Collector
SoftBank記事を参考にした日本株データ収集システム
pandas-datareaderのStooqデータソースを使用
"""

import os
import sys
import logging
import psycopg2
from psycopg2.extras import RealDictCursor, execute_batch
import pandas as pd
import pandas_datareader as pdr
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import time
import decimal

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class StooqJapaneseStockCollector:
    """Stooqを使った日本株データ収集クラス"""

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

        # 主要日本株銘柄リスト
        self.major_japanese_stocks = {
            # 日経225主要銘柄
            'technology': [
                '7203.JP',  # トヨタ自動車
                '6758.JP',  # ソニーグループ
                '9432.JP',  # NTT
                '9433.JP',  # KDDI
                '9434.JP',  # ソフトバンク
                '9984.JP',  # ソフトバンクグループ
                '6861.JP',  # キーエンス
                '6098.JP',  # リクルートホールディングス
                '7267.JP',  # ホンダ
                '7751.JP',  # キヤノン
                '6501.JP',  # 日立製作所
                '6503.JP',  # 三菱電機
                '6504.JP',  # 富士電機
                '6506.JP',  # 安川電機
                '6702.JP',  # 富士通
                '6753.JP',  # シャープ
                '6762.JP',  # TDK
                '6770.JP',  # アルプスアルパイン
                '6902.JP',  # デンソー
                '6954.JP',  # ファナック
                '7974.JP',  # 任天堂
                '4755.JP',  # 楽天グループ
                '3659.JP',  # ネクソン
                '2432.JP',  # DeNA
                '3938.JP',  # LINE
            ],
            'finance': [
                '8306.JP',  # 三菱UFJフィナンシャル
                '8316.JP',  # 三井住友フィナンシャル
                '8411.JP',  # みずほフィナンシャル
                '8331.JP',  # 千葉銀行
                '8354.JP',  # ふくおかフィナンシャル
                '8355.JP',  # 静岡銀行
                '8359.JP',  # 八十二銀行
                '8604.JP',  # 野村ホールディングス
                '8766.JP',  # 東京海上ホールディングス
                '8630.JP',  # SOMPOホールディングス
                '8725.JP',  # MS&ADインシュアランス
                '8795.JP',  # T&Dホールディングス
            ],
            'retail': [
                '9983.JP',  # ファーストリテイリング
                '3382.JP',  # セブン&アイ・ホールディングス
                '8267.JP',  # イオン
                '3092.JP',  # ZOZO
                '7453.JP',  # 良品計画
                '9843.JP',  # ニトリホールディングス
                '3086.JP',  # J.フロント リテイリング
                '3099.JP',  # 三越伊勢丹ホールディングス
                '7532.JP',  # パン・パシフィック
            ],
            'pharmaceutical': [
                '4502.JP',  # 武田薬品工業
                '4503.JP',  # アステラス製薬
                '4506.JP',  # 大日本住友製薬
                '4507.JP',  # 塩野義製薬
                '4519.JP',  # 中外製薬
                '4523.JP',  # エーザイ
                '4568.JP',  # 第一三共
                '4578.JP',  # 大塚ホールディングス
            ],
            'construction': [
                '1801.JP',  # 大成建設
                '1802.JP',  # 大林組
                '1803.JP',  # 清水建設
                '1808.JP',  # 長谷工コーポレーション
                '1812.JP',  # 鹿島建設
                '1925.JP',  # 大和ハウス工業
                '1928.JP',  # 積水ハウス
                '5201.JP',  # AGC
                '5202.JP',  # 板硝子
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

    def add_japanese_symbol(self, symbol: str, company_name: str, sector: str) -> bool:
        """日本株銘柄をデータベースに追加"""
        try:
            # 既存チェック
            self.cursor.execute(
                "SELECT symbol FROM stock_master WHERE symbol = %s",
                (symbol,)
            )

            if self.cursor.fetchone():
                logger.debug(f"✓ {symbol}: 既存")
                return False

            # 銘柄追加
            self.cursor.execute("""
                INSERT INTO stock_master (
                    symbol, company_name, name, exchange, sector,
                    market_cap, currency, country, is_active,
                    created_at, updated_at
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                symbol,
                company_name[:255],
                company_name[:255],
                'TSE',  # Tokyo Stock Exchange
                sector[:100],
                0,  # 後で更新
                'JPY',
                'Japan',
                True,
                datetime.now(),
                datetime.now()
            ))

            self.connection.commit()
            logger.info(f"✅ {symbol}: {company_name} を追加")
            return True

        except Exception as e:
            logger.error(f"❌ 銘柄追加エラー {symbol}: {e}")
            self.connection.rollback()
            return False

    def fetch_stooq_data(self, symbol: str, start_date: str = None, end_date: str = None) -> Optional[pd.DataFrame]:
        """Stooqから株価データ取得"""
        try:
            if not start_date:
                start_date = (datetime.now() - timedelta(days=730)).strftime('%Y-%m-%d')
            if not end_date:
                end_date = datetime.now().strftime('%Y-%m-%d')

            # Stooqから直接データ取得
            df = pdr.DataReader(symbol, 'stooq', start=start_date, end=end_date)

            if df.empty:
                logger.warning(f"⚠️ {symbol}: Stooqデータなし")
                return None

            # インデックスをDatetimeIndexに確保
            if not isinstance(df.index, pd.DatetimeIndex):
                df.index = pd.to_datetime(df.index)

            # カラム名を小文字に統一
            df.columns = [col.lower() for col in df.columns]

            # データ品質チェック
            if 'close' in df.columns:
                # 終値を整数に丸める（SoftBank記事参考）
                df['close_rounded'] = df['close'].apply(
                    lambda x: int(decimal.Decimal(str(x)).quantize(decimal.Decimal('1')))
                )

                # 移動平均線計算
                df['sma10'] = df['close'].rolling(window=10).mean()
                df['sma75'] = df['close'].rolling(window=75).mean()

            logger.info(f"✅ {symbol}: {len(df)}日分のデータ取得成功")
            return df

        except Exception as e:
            logger.error(f"❌ Stooqデータ取得エラー {symbol}: {e}")
            return None

    def store_price_data(self, symbol: str, df: pd.DataFrame) -> int:
        """価格データをデータベースに保存"""
        try:
            records = []

            for date, row in df.iterrows():
                # 日付がDatetimeIndexの場合、dateに変換
                if isinstance(date, pd.Timestamp):
                    date = date.date()

                records.append((
                    symbol.replace('.JP', '.T'),  # .JPを.Tに変換（データベース互換性）
                    date,
                    float(row.get('open', 0)),
                    float(row.get('high', 0)),
                    float(row.get('low', 0)),
                    float(row.get('close', 0)),
                    int(row.get('volume', 0)),
                    datetime.now()
                ))

            if records:
                execute_batch(self.cursor, """
                    INSERT INTO stock_prices
                    (symbol, date, open_price, high_price, low_price, close_price, volume, created_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (symbol, date) DO UPDATE
                    SET open_price = EXCLUDED.open_price,
                        high_price = EXCLUDED.high_price,
                        low_price = EXCLUDED.low_price,
                        close_price = EXCLUDED.close_price,
                        volume = EXCLUDED.volume
                """, records)

                self.connection.commit()
                logger.info(f"✅ {symbol}: {len(records)}レコード保存")
                return len(records)

            return 0

        except Exception as e:
            logger.error(f"❌ 価格データ保存エラー {symbol}: {e}")
            self.connection.rollback()
            return 0

    def collect_all_japanese_stocks(self) -> Dict:
        """全主要日本株データ収集"""
        results = {
            'symbols_added': [],
            'prices_added': {},
            'errors': [],
            'summary': {}
        }

        total_records = 0

        for sector, symbols in self.major_japanese_stocks.items():
            logger.info(f"📊 {sector}セクター処理開始...")

            for symbol in symbols:
                try:
                    # 企業名生成（簡易版）
                    code = symbol.split('.')[0]
                    company_name = f"Japanese Company {code}"

                    # 銘柄追加（.JP → .T変換）
                    db_symbol = symbol.replace('.JP', '.T')
                    if self.add_japanese_symbol(db_symbol, company_name, sector):
                        results['symbols_added'].append(db_symbol)

                    # Stooqからデータ取得
                    df = self.fetch_stooq_data(symbol)

                    if df is not None:
                        # 価格データ保存
                        records = self.store_price_data(symbol, df)
                        if records > 0:
                            results['prices_added'][db_symbol] = records
                            total_records += records

                    # API制限対応
                    time.sleep(0.5)

                except Exception as e:
                    logger.error(f"❌ エラー {symbol}: {e}")
                    results['errors'].append(f"{symbol}: {str(e)}")

        results['summary'] = {
            'symbols_added': len(results['symbols_added']),
            'symbols_with_prices': len(results['prices_added']),
            'total_price_records': total_records,
            'errors': len(results['errors'])
        }

        return results


def main():
    """メイン処理"""
    logger.info("🚀 Stooq Japanese Stock Data Collector開始")

    mode = os.getenv('BATCH_MODE', 'collect')

    collector = StooqJapaneseStockCollector()

    if not collector.connect():
        logger.error("データベース接続失敗")
        sys.exit(1)

    try:
        if mode == 'collect':
            # 日本株データ収集
            results = collector.collect_all_japanese_stocks()

            logger.info("✅ 収集完了:")
            logger.info(f"  - 追加銘柄: {results['summary']['symbols_added']}")
            logger.info(f"  - 価格データ銘柄: {results['summary']['symbols_with_prices']}")
            logger.info(f"  - 総価格レコード: {results['summary']['total_price_records']}")
            logger.info(f"  - エラー: {results['summary']['errors']}")

        elif mode == 'test':
            # テストモード（ソフトバンクのみ）
            symbol = '9434.JP'
            logger.info(f"📊 テスト: {symbol}")

            df = collector.fetch_stooq_data(symbol)
            if df is not None:
                logger.info(f"  - データ取得成功: {len(df)}日分")
                logger.info(f"  - 期間: {df.index[0]} ～ {df.index[-1]}")
                logger.info(f"  - 最新終値: {df['close'].iloc[-1]:.2f}")

                if 'sma10' in df.columns:
                    logger.info(f"  - 10日移動平均: {df['sma10'].iloc[-1]:.2f}")
                if 'sma75' in df.columns:
                    logger.info(f"  - 75日移動平均: {df['sma75'].iloc[-1]:.2f}")

        else:
            logger.warning(f"不明なモード: {mode}")

    except Exception as e:
        logger.error(f"❌ 処理エラー: {e}")
        sys.exit(1)

    finally:
        collector.disconnect()
        logger.info("✅ Stooq Japanese Stock Data Collector完了")


if __name__ == "__main__":
    main()