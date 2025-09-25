#!/usr/bin/env python3
"""
拡張シンボルコレクター - より多くの銘柄を収集するためのシステム
"""

import psycopg2
import yfinance as yf
import logging
from datetime import datetime, timedelta
import time
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ExpandedSymbolCollector:
    def __init__(self):
        self.db_config = {
            "host": "34.173.9.214",
            "user": "postgres",
            "password": "os.getenv('DB_PASSWORD', '')",
            "database": "miraikakaku",
            "port": 5432
        }

    def get_expanded_symbol_list(self):
        """大幅に拡張された銘柄リストを取得"""
        return [
            # US メガキャップ テクノロジー (100+)
            'AAPL', 'MSFT', 'GOOGL', 'GOOG', 'AMZN', 'NVDA', 'TSLA', 'META',
            'NFLX', 'ADBE', 'CRM', 'ORCL', 'CSCO', 'INTC', 'QCOM', 'TXN',
            'AVGO', 'IBM', 'NOW', 'AMD', 'MU', 'AMAT', 'ADI', 'LRCX', 'MRVL',
            'KLAC', 'CDNS', 'SNPS', 'FTNT', 'PANW', 'CRWD', 'ZS', 'OKTA',
            'DDOG', 'NET', 'SNOW', 'MDB', 'PLTR', 'PALANTIR', 'RBLX',

            # US 金融 (50+)
            'JPM', 'BAC', 'WFC', 'GS', 'MS', 'C', 'USB', 'PNC', 'TFC', 'COF',
            'AXP', 'BLK', 'SPGI', 'CME', 'ICE', 'CB', 'PGR', 'AIG', 'MET', 'PRU',
            'AFL', 'ALL', 'TRV', 'HIG', 'CMA', 'FITB', 'KEY', 'RF', 'CFG', 'HBAN',

            # US ヘルスケア (50+)
            'JNJ', 'PFE', 'UNH', 'CVS', 'MRK', 'ABBV', 'TMO', 'DHR', 'ABT',
            'LLY', 'BMY', 'AMGN', 'GILD', 'ISRG', 'SYK', 'BSX', 'MDT', 'ZTS',
            'VRTX', 'REGN', 'BIIB', 'ILMN', 'MRNA', 'NVAX', 'BNT', 'PFE',
            'BNTX', 'JNJ', 'RGEN', 'ALNY', 'BMRN', 'BLUE', 'CRSP',

            # US エネルギー (30+)
            'XOM', 'CVX', 'COP', 'EOG', 'SLB', 'PSX', 'VLO', 'MPC', 'OXY', 'BKR',
            'HAL', 'APA', 'DVN', 'FANG', 'EQT', 'CNX', 'AR', 'SM', 'MRO', 'CHK',

            # US 消費財 (50+)
            'PG', 'KO', 'PEP', 'WMT', 'HD', 'MCD', 'NKE', 'SBUX', 'TGT', 'LOW',
            'COST', 'KMB', 'CL', 'CLX', 'CHD', 'GIS', 'K', 'CPB', 'CAG', 'TSN',
            'HRL', 'SJM', 'MKC', 'LW', 'PM', 'MO', 'BTI', 'IMBBY',

            # 日本主要銘柄 (200+)
            # 自動車
            '7203.T', '7267.T', '7269.T', '7270.T', '7201.T', '7202.T', '7211.T',
            '7261.T', '7272.T', '7259.T', '7244.T', '7205.T', '7240.T',

            # 金融
            '8306.T', '8316.T', '8354.T', '8355.T', '8411.T', '8473.T', '8604.T',
            '8750.T', '8766.T', '8795.T', '8801.T', '8802.T', '8830.T',

            # テクノロジー
            '6758.T', '6861.T', '6503.T', '6504.T', '6506.T', '6594.T', '6674.T',
            '6701.T', '6702.T', '6703.T', '6723.T', '6724.T', '6752.T', '6753.T',
            '6762.T', '6770.T', '6806.T', '6841.T', '6856.T', '6857.T',

            # 通信・メディア
            '9432.T', '9433.T', '9434.T', '9613.T', '9984.T', '9983.T', '4755.T',
            '4689.T', '4751.T', '4324.T', '4385.T', '4776.T',

            # 製薬・化学
            '4519.T', '4568.T', '4523.T', '4578.T', '4508.T', '4506.T', '4507.T',
            '4041.T', '4042.T', '4043.T', '4061.T', '4063.T', '4080.T',

            # 小売・消費
            '7974.T', '7832.T', '7751.T', '8233.T', '8267.T', '8252.T', '9843.T',

            # 欧州主要銘柄 (100+)
            'ASML', 'SAP', 'NESN.SW', 'NOVO-B.CO', 'RMS.PA', 'SAN.PA',
            'INGA.AS', 'ADYEN.AS', 'MC.PA', 'OR.PA', 'AI.PA', 'SU.PA',
            'BAS.DE', 'SAP.DE', 'ALV.DE', 'SIE.DE', 'DTE.DE', 'VOW3.DE',
            'BMW.DE', 'MBG.DE', 'FRE.DE', 'HEN3.DE', 'LIN.DE', 'MRK.DE',

            # 中国・アジア主要 (50+)
            'BABA', 'JD', 'BIDU', 'TCEHY', 'NTES', 'PDD', 'NIO', 'XPEV', 'LI',
            'DIDI', 'TME', 'BILI', 'IQ', 'VIPS', 'FUTU', 'TIGR',
            '005930.KS', '000660.KS', '035420.KS', '207940.KS', '068270.KS',

            # 韓国主要
            '005930.KS', '000660.KS', '035420.KS', '207940.KS', '005380.KS',
            '017670.KS', '090430.KS', '066570.KS', '003550.KS', '015760.KS',

            # インド主要
            'INFY', 'TCS.NS', 'WIPRO.NS', 'HCLTECH.NS', 'TECHM.NS',
            'RELIANCE.NS', 'HINDUNILVR.NS', 'ITC.NS', 'SBIN.NS', 'HDFCBANK.NS',

            # カナダ主要
            'SHOP.TO', 'WEED.TO', 'ACB.TO', 'BB.TO', 'SU.TO', 'CNQ.TO',
            'CP.TO', 'CNR.TO', 'RY.TO', 'TD.TO', 'BNS.TO', 'BMO.TO',

            # オーストラリア主要
            'CBA.AX', 'ANZ.AX', 'WBC.AX', 'NAB.AX', 'BHP.AX', 'RIO.AX',
            'CSL.AX', 'WOW.AX', 'WES.AX', 'TLS.AX', 'TCL.AX',

            # ETF・インデックス
            'SPY', 'QQQ', 'IWM', 'EFA', 'EEM', 'VTI', 'VXUS', 'BND', 'AGG',
            'GLD', 'SLV', 'USO', 'UNG', 'TLT', 'HYG', 'LQD', 'VNQ',

            # 暗号通貨関連
            'COIN', 'MSTR', 'RIOT', 'MARA', 'HUT', 'BITF', 'SOS', 'EBON',

            # REIT
            'AMT', 'PLD', 'CCI', 'EQIX', 'PSA', 'O', 'WELL', 'DLR', 'SPG', 'AVB',

            # 商品・原材料
            'FCX', 'NEM', 'GOLD', 'AA', 'X', 'CLF', 'MT', 'VALE', 'RIO', 'BHP',

            # 公益事業
            'NEE', 'DUK', 'SO', 'AEP', 'EXC', 'XEL', 'D', 'PCG', 'ED', 'ES'
        ]

    def collect_expanded_data(self, max_symbols=500, batch_size=50):
        """拡張シンボルリストからデータ収集"""
        connection = psycopg2.connect(**self.db_config)

        try:
            with connection.cursor() as cursor:
                logger.info("🚀 拡張シンボル収集開始")

                all_symbols = self.get_expanded_symbol_list()
                symbols_to_process = all_symbols[:max_symbols] if max_symbols else all_symbols

                logger.info(f"📊 処理対象: {len(symbols_to_process)}銘柄")

                total_successful = 0
                total_errors = 0

                for batch_start in range(0, len(symbols_to_process), batch_size):
                    batch_symbols = symbols_to_process[batch_start:batch_start + batch_size]

                    batch_successful, batch_errors = self.process_symbol_batch(cursor, batch_symbols)
                    total_successful += batch_successful
                    total_errors += batch_errors

                    connection.commit()

                    progress = ((batch_start + len(batch_symbols)) / len(symbols_to_process)) * 100
                    logger.info(f"📈 進捗: {progress:.1f}% (成功{total_successful}件, エラー{total_errors}件)")

                    # レート制限対策
                    time.sleep(2)

                logger.info(f"✅ 拡張収集完了: 成功{total_successful}件, エラー{total_errors}件")
                return total_successful

        except Exception as e:
            logger.error(f"❌ 拡張収集エラー: {e}")
            return 0
        finally:
            connection.close()

    def process_symbol_batch(self, cursor, symbols):
        """シンボルバッチの並列処理"""
        successful_count = 0
        error_count = 0

        with ThreadPoolExecutor(max_workers=10) as executor:
            future_to_symbol = {
                executor.submit(self.fetch_symbol_data, symbol): symbol
                for symbol in symbols
            }

            price_updates = []

            for future in as_completed(future_to_symbol):
                symbol = future_to_symbol[future]
                try:
                    price_data = future.result()
                    if price_data:
                        price_updates.append(price_data)
                        successful_count += 1
                    else:
                        error_count += 1
                except Exception as e:
                    logger.debug(f"⚠️ {symbol}: {e}")
                    error_count += 1

            # バッチ挿入
            if price_updates:
                self.batch_insert_prices(cursor, price_updates)

        return successful_count, error_count

    def fetch_symbol_data(self, symbol):
        """個別シンボルのデータ取得"""
        try:
            ticker = yf.Ticker(symbol)

            # 過去5日のデータ取得
            hist = ticker.history(period="5d", interval="1d")

            if hist.empty:
                return None

            # 最新データを取得
            latest_data = hist.iloc[-1]
            latest_date = hist.index[-1].date()

            return {
                'symbol': symbol,
                'date': latest_date,
                'open': round(float(latest_data['Open']), 2) if not pd.isna(latest_data['Open']) else 0.0,
                'high': round(float(latest_data['High']), 2) if not pd.isna(latest_data['High']) else 0.0,
                'low': round(float(latest_data['Low']), 2) if not pd.isna(latest_data['Low']) else 0.0,
                'close': round(float(latest_data['Close']), 2) if not pd.isna(latest_data['Close']) else 0.0,
                'volume': int(latest_data['Volume']) if not pd.isna(latest_data['Volume']) else 0
            }

        except Exception as e:
            logger.debug(f"🔍 {symbol}: データ取得失敗 - {e}")
            return None

    def batch_insert_prices(self, cursor, price_data_list):
        """価格データのバッチ挿入 (PostgreSQL対応)"""
        try:
            insert_data = []
            for data in price_data_list:
                insert_data.append((
                    data['symbol'], data['date'], data['open'], data['high'],
                    data['low'], data['close'], data['volume']
                ))

            cursor.executemany("""
                INSERT INTO stock_prices
                (symbol, date, open_price, high_price, low_price, close_price, volume, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, NOW())
                ON CONFLICT (symbol, date) DO UPDATE SET
                open_price = EXCLUDED.open_price,
                high_price = EXCLUDED.high_price,
                low_price = EXCLUDED.low_price,
                close_price = EXCLUDED.close_price,
                volume = EXCLUDED.volume,
                updated_at = NOW()
            """, insert_data)

        except Exception as e:
            logger.error(f"❌ バッチ挿入エラー: {e}")

def main():
    collector = ExpandedSymbolCollector()

    logger.info("🚀 拡張シンボルコレクター開始")

    # 拡張データ収集実行
    successful_count = collector.collect_expanded_data(max_symbols=1000, batch_size=100)

    logger.info(f"✅ 拡張収集完了: {successful_count}件成功")

if __name__ == "__main__":
    import pandas as pd
    main()