#!/usr/bin/env python3
"""
実データのみで100%カバレッジを目指すコレクター
合成データは一切使用しない
"""

import psycopg2
import psycopg2.extras
import yfinance as yf
import pandas_datareader.data as web
from datetime import datetime, timedelta
import logging
import time
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RealDataOnlyCollector:
    def __init__(self):
        self.db_config = {
            "host": os.getenv("DB_HOST", "34.58.103.36"),
            "user": os.getenv("DB_USER", "miraikakaku-user"),
            "password": os.getenv("DB_PASSWORD", "miraikakaku-secure-pass-2024"),
            "database": os.getenv("DB_NAME", "miraikakaku"),
            "port": 5432
        }
        
        self.worker_id = int(os.getenv("BATCH_TASK_INDEX", "0"))
        
    def generate_alternative_symbols(self, symbol, market, country):
        """代替シンボルを生成"""
        alternatives = [symbol]  # 元のシンボルを最初に
        
        # 国別シンボル変換
        if country == 'Japan' or market == 'JP':
            alternatives.extend([
                f"{symbol}.T",      # Tokyo Stock Exchange
                f"{symbol}.JP"      # Japan suffix
            ])
        elif country == 'United States' or market in ['US', 'NYSE', 'NASDAQ']:
            alternatives.extend([
                f"{symbol}.US",     # US suffix for Stooq
                symbol.replace('-', '.')  # ハイフン→ドット変換
            ])
        elif country == 'Canada':
            alternatives.extend([
                f"{symbol}.TO",     # Toronto
                f"{symbol}.V"       # Vancouver
            ])
        elif country == 'UK':
            alternatives.extend([
                f"{symbol}.L",      # London
                f"{symbol}.LN"      # London alternative
            ])
        elif country == 'Germany':
            alternatives.extend([
                f"{symbol}.DE",     # Germany
                f"{symbol}.F"       # Frankfurt
            ])
        
        return alternatives
    
    def fetch_with_yfinance(self, symbol):
        """yfinanceでデータ取得"""
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period="5d")
            
            if not hist.empty:
                logger.debug(f"✅ yfinance: {symbol} - {len(hist)}日分")
                return hist, 'yfinance'
        except Exception as e:
            logger.debug(f"yfinance failed {symbol}: {e}")
        
        return None, None
    
    def fetch_with_stooq(self, symbol):
        """Stooq (pandas-datareader)でデータ取得"""
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=30)
            
            df = web.DataReader(symbol, 'stooq', start_date, end_date)
            
            if not df.empty:
                logger.debug(f"✅ stooq: {symbol} - {len(df)}日分")
                return df, 'stooq'
        except Exception as e:
            logger.debug(f"stooq failed {symbol}: {e}")
        
        return None, None
    
    def fetch_with_fred(self, symbol):
        """FRED (経済指標)でデータ取得"""
        try:
            # FRED経済指標のシンボル判定
            fred_symbols = {
                'DGS10', 'DGS2', 'DGS30',  # 国債利回り
                'DEXJPUS', 'DEXUSEU', 'DEXCAUS',  # 為替
                'DCOILWTICO', 'GOLDAMGBD228NLBM'  # コモディティ
            }
            
            if symbol.upper() in fred_symbols or 'DGS' in symbol or 'DEX' in symbol:
                df = web.DataReader(symbol, 'fred', datetime.now() - timedelta(days=30))
                
                if not df.empty:
                    logger.debug(f"✅ FRED: {symbol} - {len(df)}日分")
                    return df, 'fred'
        except Exception as e:
            logger.debug(f"FRED failed {symbol}: {e}")
        
        return None, None
    
    def try_all_sources(self, symbol, market, country):
        """全てのデータソースとシンボル変換を試行"""
        alternatives = self.generate_alternative_symbols(symbol, market, country)
        
        for alt_symbol in alternatives:
            # 1. yfinanceを試行
            data, source = self.fetch_with_yfinance(alt_symbol)
            if data is not None:
                return data, source, alt_symbol
            
            # 2. Stooqを試行
            data, source = self.fetch_with_stooq(alt_symbol)
            if data is not None:
                return data, source, alt_symbol
            
            # 短い待機（API制限対策）
            time.sleep(0.05)
        
        # 3. FRED（経済指標の場合）
        data, source = self.fetch_with_fred(symbol)
        if data is not None:
            return data, source, symbol
        
        return None, None, None
    
    def mark_as_unfetchable(self, symbol, reason="no_real_data_available"):
        """実データが取得できない銘柄をマーク"""
        connection = psycopg2.connect(**self.db_config)
        
        try:
            with connection.cursor() as cursor:
                # unfetchable_stocks テーブルに記録
                cursor.execute("""
                    INSERT INTO unfetchable_stocks 
                    (symbol, reason, attempted_at, notes)
                    VALUES (%s, %s, NOW(), %s)
                    ON DUPLICATE KEY UPDATE
                    reason = VALUES(reason),
                    attempted_at = VALUES(attempted_at),
                    attempt_count = attempt_count + 1
                """, (symbol, reason, f"Worker_{self.worker_id}_attempted"))
                
                connection.commit()
                logger.debug(f"🚫 {symbol} marked as unfetchable: {reason}")
        except Exception as e:
            logger.error(f"Failed to mark {symbol}: {e}")
        finally:
            connection.close()
    
    def collect_real_data_only(self, batch_size=100):
        """実データのみでコレクション実行"""
        connection = psycopg2.connect(**self.db_config)
        
        try:
            with connection.cursor() as cursor:
                # 未収集銘柄を取得（unfetchableマーク済みは除外）
                offset = self.worker_id * batch_size
                
                cursor.execute("""
                    SELECT sm.symbol, sm.name, sm.market, sm.country
                    FROM stock_master sm
                    LEFT JOIN stock_price_history sph ON sm.symbol = sph.symbol
                    LEFT JOIN unfetchable_stocks uf ON sm.symbol = uf.symbol
                    WHERE sm.is_active = 1 
                        AND sph.symbol IS NULL
                        AND uf.symbol IS NULL
                    ORDER BY 
                        CASE 
                            WHEN sm.market IN ('US', 'NYSE', 'NASDAQ') THEN 1
                            WHEN sm.country = 'Japan' THEN 2
                            ELSE 3
                        END,
                        sm.symbol
                    LIMIT %s OFFSET %s
                """, (batch_size, offset))
                
                uncovered = cursor.fetchall()
                logger.info(f"🔍 Worker {self.worker_id}: {len(uncovered)}銘柄を処理")
                
                successful = 0
                failed = 0
                
                for symbol, name, market, country in uncovered:
                    try:
                        # 実データ取得を試行
                        data, source, used_symbol = self.try_all_sources(symbol, market, country)
                        
                        if data is not None:
                            # データ保存
                            saved = self.save_real_data(symbol, data, source, used_symbol)
                            if saved > 0:
                                successful += 1
                                logger.info(f"✅ {symbol} ({source}): {saved}レコード保存")
                        else:
                            # 実データが取得できない場合はマーク
                            self.mark_as_unfetchable(symbol, "no_api_response")
                            failed += 1
                            logger.debug(f"🚫 {symbol}: 実データ取得不可")
                        
                        # API制限対策
                        time.sleep(0.1)
                        
                    except Exception as e:
                        logger.error(f"❌ {symbol}: {e}")
                        failed += 1
                
                logger.info(f"""
                🎯 Worker {self.worker_id} 完了:
                - 成功: {successful}銘柄
                - 失敗: {failed}銘柄
                - 実データのみ使用
                """)
                
                return successful
                
        finally:
            connection.close()
    
    def save_real_data(self, symbol, df, source, used_symbol):
        """実データをデータベースに保存"""
        connection = psycopg2.connect(**self.db_config)
        saved_count = 0
        
        try:
            with connection.cursor() as cursor:
                for date, row in df.iterrows():
                    try:
                        cursor.execute("""
                            INSERT INTO stock_price_history 
                            (symbol, date, open_price, high_price, low_price, 
                             close_price, volume, adjusted_close, data_source, 
                             is_valid, data_quality_score, created_at, updated_at)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, 1, 1.0, NOW(), NOW())
                            ON DUPLICATE KEY UPDATE
                            close_price = VALUES(close_price),
                            data_source = VALUES(data_source),
                            data_quality_score = 1.0,
                            updated_at = NOW()
                        """, (
                            symbol,
                            date.date() if hasattr(date, 'date') else date,
                            float(row.get('Open', 0)),
                            float(row.get('High', 0)),
                            float(row.get('Low', 0)),
                            float(row.get('Close', 0)),
                            int(row.get('Volume', 0)),
                            float(row.get('Close', 0)),
                            f"{source}_{used_symbol}" if used_symbol != symbol else source
                        ))
                        saved_count += 1
                    except Exception as save_error:
                        logger.debug(f"Save error for {symbol}: {save_error}")
                        continue
                
                connection.commit()
        finally:
            connection.close()
        
        return saved_count

def main():
    collector = RealDataOnlyCollector()
    result = collector.collect_real_data_only(batch_size=150)
    
    logger.info(f"✅ Real data collection completed: {result} stocks processed")

if __name__ == "__main__":
    main()