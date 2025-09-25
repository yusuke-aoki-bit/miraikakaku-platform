#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import psycopg2
import psycopg2.extras
import yfinance as yf
import pandas as pd
import logging
import time
import random
from datetime import datetime, timedelta

# ログ設定
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SimpleContinuousExpander:
    def __init__(self):
        self.db_config = {
            "host": "34.173.9.214",
            "user": "postgres",
            "password": "miraikakaku-postgres-secure-2024",
            "database": "miraikakaku",
            "port": 5432
        }
        
        # 追加確実銘柄（段階的拡張用）
        self.expansion_waves = [
            # Wave 1: 追加US大型株
            ['IBM', 'ORCL', 'CSCO', 'CMCSA', 'TMUS', 'CRM', 'INTU', 'TXN',
             'QCOM', 'AMGN', 'ISRG', 'MU', 'ADI', 'LRCX', 'KLAC', 'MCHP'],
            
            # Wave 2: 追加金融・保険
            ['BRK-B', 'JPM', 'BAC', 'WFC', 'GS', 'MS', 'AXP', 'USB',
             'PNC', 'TFC', 'SCHW', 'BLK', 'SPGI', 'ICE', 'CME', 'COF'],
            
            # Wave 3: 追加ヘルスケア
             ['ABBV', 'JNJ', 'PFE', 'MRK', 'UNH', 'LLY', 'TMO', 'ABT',
              'DHR', 'BMY', 'AMGN', 'GILD', 'REGN', 'VRTX', 'BIIB', 'ILMN'],
            
            # Wave 4: 追加消費財
            ['AMZN', 'TSLA', 'HD', 'NKE', 'SBUX', 'MCD', 'DIS', 'NFLX',
             'BKNG', 'LOW', 'TJX', 'TGT', 'COST', 'WMT', 'KR', 'WBA'],
            
            # Wave 5: 追加工業・エネルギー
            ['CAT', 'BA', 'GE', 'MMM', 'HON', 'RTX', 'LMT', 'NOC',
             'XOM', 'CVX', 'COP', 'EOG', 'SLB', 'PSX', 'VLO', 'MPC'],
            
            # Wave 6: 日本大型株追加
            ['7203.T', '6758.T', '9984.T', '8306.T', '9432.T', '6861.T',
             '7267.T', '8316.T', '4063.T', '9020.T', '6098.T', '4519.T',
             '6367.T', '6594.T', '6954.T', '4901.T', '8058.T', '2914.T']
        ]

    def get_yfinance_coverage_simple(self):
        """シンプルなカバー率取得"""
        try:
            connection = psycopg2.connect(**self.db_config)
            with connection.cursor() as cursor:
                cursor.execute("SELECT COUNT(*) FROM stock_master WHERE is_active = 1")
                total = cursor.fetchone()[0]
                
                cursor.execute("SELECT COUNT(DISTINCT symbol) FROM stock_price_history WHERE data_source = 'yfinance'")
                covered = cursor.fetchone()[0]
                
                return total, covered, (covered / total * 100) if total > 0 else 0
        except Exception as e:
            logger.error(f"カバー率取得エラー: {e}")
            return 0, 0, 0
        finally:
            if 'connection' in locals():
                connection.close()

    def check_symbol_exists(self, symbol):
        """シンボルの既存確認"""
        try:
            connection = psycopg2.connect(**self.db_config)
            with connection.cursor() as cursor:
                cursor.execute("SELECT COUNT(*) FROM stock_price_history WHERE symbol = %s AND data_source = 'yfinance'", (symbol,))
                return cursor.fetchone()[0] > 0
        except Exception as e:
            return True  # エラー時はスキップ
        finally:
            if 'connection' in locals():
                connection.close()

    def add_symbol_simple(self, symbol):
        """シンプル銘柄追加"""
        try:
            connection = psycopg2.connect(**self.db_config)
            with connection.cursor() as cursor:
                if symbol.endswith('.T'):
                    country, exchange = 'Japan', 'TSE'
                else:
                    country, exchange = 'US', 'NYSE'
                
                cursor.execute("""
                    INSERT IGNORE INTO stock_master 
                    (symbol, name, country, exchange, is_active)
                    VALUES (%s, %s, %s, %s, 1)
                """, (symbol, f"Stock-{symbol}", country, exchange))
                
                connection.commit()
                return True
        except Exception as e:
            return False
        finally:
            if 'connection' in locals():
                connection.close()

    def fetch_and_save_simple(self, symbol):
        """シンプル取得・保存"""
        try:
            # 既存確認
            if self.check_symbol_exists(symbol):
                return {'status': 'exists', 'count': 0}
            
            # master追加
            self.add_symbol_simple(symbol)
            
            # yfinance取得
            ticker = yf.Ticker(symbol)
            
            end_date = datetime.now()
            start_date = end_date - timedelta(days=90)
            
            hist_data = ticker.history(
                start=start_date.strftime('%Y-%m-%d'),
                end=end_date.strftime('%Y-%m-%d'),
                interval='1d'
            )
            
            if hist_data.empty:
                return {'status': 'no_data', 'count': 0}
            
            # データ変換
            price_data = []
            for date, row in hist_data.iterrows():
                try:
                    if pd.isna([row['Open'], row['Close']]).any() or row['Open'] <= 0 or row['Close'] <= 0:
                        continue
                    
                    price_data.append((
                        symbol, date.strftime('%Y-%m-%d'),
                        float(row['Open']), 
                        float(row['High']) if not pd.isna(row['High']) else float(row['Open']),
                        float(row['Low']) if not pd.isna(row['Low']) else float(row['Open']),
                        float(row['Close']),
                        int(max(row['Volume'], 0)) if not pd.isna(row['Volume']) else 0,
                        float(row['Close']),
                        'yfinance', 1, 0.96
                    ))
                except (ValueError, OverflowError):
                    continue
            
            if not price_data:
                return {'status': 'no_valid_data', 'count': 0}
            
            # 保存
            connection = psycopg2.connect(**self.db_config)
            try:
                with connection.cursor() as cursor:
                    cursor.executemany("""
                        INSERT IGNORE INTO stock_price_history 
                        (symbol, date, open_price, high_price, low_price, close_price,
                         volume, adjusted_close, data_source, is_valid, data_quality_score, created_at)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())
                    """, price_data)
                    
                    connection.commit()
                    return {'status': 'success', 'count': cursor.rowcount}
            except Exception as e:
                logger.error(f"保存エラー {symbol}: {e}")
                return {'status': 'save_error', 'count': 0}
            finally:
                connection.close()
                
        except Exception as e:
            logger.error(f"処理エラー {symbol}: {e}")
            return {'status': 'error', 'count': 0}

    def wave_expansion(self):
        """ウェーブ式拡張"""
        logger.info("🌊 ウェーブ式拡張開始")
        
        total_success = 0
        total_records = 0
        
        for wave_num, symbols in enumerate(self.expansion_waves, 1):
            logger.info(f"🌊 Wave {wave_num}: {len(symbols)}銘柄処理開始")
            
            wave_success = 0
            wave_records = 0
            
            for i, symbol in enumerate(symbols):
                logger.info(f"📊 Wave {wave_num} - {i+1}/{len(symbols)}: {symbol}")
                
                result = self.fetch_and_save_simple(symbol)
                
                if result['status'] == 'success':
                    wave_success += 1
                    wave_records += result['count']
                    logger.info(f"✅ {symbol}: {result['count']}件保存")
                elif result['status'] == 'exists':
                    logger.info(f"⏭️ {symbol}: 既存")
                else:
                    logger.warning(f"⚠️ {symbol}: {result['status']}")
                
                time.sleep(0.5)  # レート制限
            
            total_success += wave_success
            total_records += wave_records
            
            # Wave結果
            logger.info(f"🌊 Wave {wave_num} 完了: {wave_success}/{len(symbols)}成功, {wave_records:,}件")
            
            # カバー率確認
            total, covered, coverage = self.get_yfinance_coverage_simple()
            logger.info(f"📊 現在のカバー率: {coverage:.1f}% ({covered:,}/{total:,})")
            
            if coverage >= 70.0:
                logger.info("🎯 70%目標達成！")
                break
            
            time.sleep(2.0)  # Wave間待機
        
        logger.info(f"🎯 ウェーブ式拡張完了: {total_success}銘柄成功, {total_records:,}件追加")
        
        # 最終評価
        import subprocess
        subprocess.run(["python3", "collation_safe_data_assessment.py"])

def main():
    expander = SimpleContinuousExpander()
    expander.wave_expansion()

if __name__ == "__main__":
    main()