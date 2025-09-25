#!/usr/bin/env python3
"""
日次実データ更新システム
毎日定時実行して全実銘柄の最新データを取得・更新
"""

import yfinance as yf
import psycopg2
import psycopg2.extras
import pandas as pd
import logging
import time
from datetime import datetime, timedelta
import numpy as np
from typing import Dict, List, Any, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DailyRealDataUpdater:
    def __init__(self):
        self.db_config = {
            "host": "34.173.9.214",
            "user": "postgres", 
            "password": "miraikakaku-postgres-secure-2024",
            "database": "miraikakaku",
        }
        self.update_stats = {
            "symbols_updated": 0,
            "successful_updates": 0,
            "failed_updates": 0,
            "new_records_created": 0
        }

    def get_connection(self):
        return psycopg2.connect(**self.db_config)

    def get_active_symbols(self) -> List[str]:
        """アクティブな実銘柄リストを取得"""
        # 文字エンコード問題回避のため、直接銘柄リストを定義
        return [
            # 米国メガキャップ
            'AAPL', 'MSFT', 'GOOGL', 'GOOG', 'AMZN', 'NVDA', 'TSLA', 'META', 
            'NFLX', 'ADBE', 'CRM', 'ORCL', 'CSCO', 'INTC', 'QCOM', 'TXN',
            'AVGO', 'IBM', 'NOW', 'AMD', 'MU', 'AMAT', 'ADI', 'LRCX', 'MRVL',
            
            # 米国金融
            'JPM', 'BAC', 'WFC', 'GS', 'MS', 'C', 'USB', 'PNC', 'TFC', 'COF',
            'AXP', 'BLK', 'SPGI', 'CME', 'ICE', 'CB', 'PGR', 'AIG', 'MET', 'PRU',
            
            # 米国ヘルスケア
            'JNJ', 'PFE', 'UNH', 'CVS', 'MRK', 'ABBV', 'TMO', 'DHR', 'ABT', 
            'LLY', 'BMY', 'AMGN', 'GILD', 'ISRG', 'SYK', 'BSX', 'MDT', 'ZTS',
            
            # 日本主要
            '7203.T', '6758.T', '9984.T', '4519.T', '6861.T', '9432.T',
            '8306.T', '7267.T', '6367.T', '8031.T', '9433.T', '4063.T',
            '6503.T', '7741.T', '4568.T', '8316.T', '9020.T', '7974.T',
            
            # 欧州主要
            'ASML', 'SAP', 'NESN.SW', 'NOVO-B.CO', 'RMS.PA', 'SAN.PA',
            'INGA.AS', 'ADYEN.AS', 'MC.PA', 'OR.PA', 'AI.PA', 'SU.PA',
            
            # その他主要銘柄
            'BABA', 'JD', 'BIDU', 'TCEHY', 'NTES', 'PDD', 'NIO',
            '005930.KS', '000660.KS', 'SHEL', 'AZN', 'BP'
        ]

    def update_symbol_data(self, symbol: str) -> bool:
        """単一銘柄のデータ更新"""
        try:
            ticker = yf.Ticker(symbol)
            
            # 過去5日間のデータを取得（最新を確実に取得）
            hist = ticker.history(period="5d")
            
            if hist.empty:
                logger.warning(f"⚠️ {symbol}: データなし")
                return False
            
            # 最新日のデータ
            latest_data = hist.iloc[-1]
            latest_date = hist.index[-1].strftime('%Y-%m-%d')
            
            # 前日比計算
            if len(hist) > 1:
                prev_close = hist.iloc[-2]['Close']
                change = latest_data['Close'] - prev_close
                change_percent = (change / prev_close) * 100
            else:
                change = 0
                change_percent = 0
            
            # データベース更新
            connection = self.get_connection()
            try:
                with connection.cursor() as cursor:
                    # 既存レコード確認
                    cursor.execute("""
                        SELECT COUNT(*) FROM stock_price_history 
                        WHERE symbol = %s AND DATE(date) = %s
                    """, (symbol.replace('.T', '').replace('.L', '').replace('.DE', '').replace('.PA', '').replace('.SW', '').replace('.AS', '').replace('.CO', '').replace('.KS', ''), latest_date))
                    
                    exists = cursor.fetchone()[0] > 0
                    
                    if not exists:
                        # 新規レコード作成
                        cursor.execute("""
                            INSERT INTO stock_price_history 
                            (symbol, date, open_price, high_price, low_price, close_price, volume, data_source, created_at, updated_at, is_valid, data_quality_score)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW(), 1, 0.95)
                        """, (
                            symbol.replace('.T', '').replace('.L', '').replace('.DE', '').replace('.PA', '').replace('.SW', '').replace('.AS', '').replace('.CO', '').replace('.KS', ''),
                            latest_date,
                            float(latest_data['Open']),
                            float(latest_data['High']),
                            float(latest_data['Low']),
                            float(latest_data['Close']),
                            int(latest_data['Volume']),
                            "Daily Real Update"
                        ))
                        
                        connection.commit()
                        self.update_stats["new_records_created"] += 1
                        logger.info(f"✅ {symbol}: ${latest_data['Close']:.2f} ({change_percent:+.2f}%) - NEW")
                        
                    else:
                        # 既存レコード更新
                        cursor.execute("""
                            UPDATE stock_price_history SET
                            close_price = %s,
                            volume = %s,
                            updated_at = NOW()
                            WHERE symbol = %s AND DATE(date) = %s
                        """, (
                            float(latest_data['Close']),
                            int(latest_data['Volume']),
                            symbol.replace('.T', '').replace('.L', '').replace('.DE', '').replace('.PA', '').replace('.SW', '').replace('.AS', '').replace('.CO', '').replace('.KS', ''),
                            latest_date
                        ))
                        
                        connection.commit()
                        logger.info(f"✅ {symbol}: ${latest_data['Close']:.2f} ({change_percent:+.2f}%) - UPDATED")
                        
            finally:
                connection.close()
                
            self.update_stats["successful_updates"] += 1
            return True
            
        except Exception as e:
            logger.error(f"❌ {symbol} 更新失敗: {e}")
            self.update_stats["failed_updates"] += 1
            return False

    def run_daily_update(self):
        """日次更新実行"""
        start_time = datetime.now()
        logger.info(f"🚀 日次実データ更新開始: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # アクティブ銘柄取得
        symbols = self.get_active_symbols()
        self.update_stats["symbols_updated"] = len(symbols)
        
        if not symbols:
            logger.warning("⚠️ 更新対象銘柄が見つかりませんでした")
            return
        
        logger.info(f"🎯 更新対象: {len(symbols)}銘柄")
        
        # 並列処理で更新実行
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = {executor.submit(self.update_symbol_data, symbol): symbol for symbol in symbols}
            
            for future in as_completed(futures):
                symbol = futures[future]
                try:
                    future.result()
                    time.sleep(0.1)  # レート制限対策
                except Exception as e:
                    logger.error(f"❌ {symbol} 並列処理エラー: {e}")
        
        # 完了報告
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        logger.info("=" * 70)
        logger.info("📊 日次実データ更新完了サマリー")
        logger.info(f"⏱️  実行時間: {duration:.1f}秒")
        logger.info(f"🎯 対象銘柄: {self.update_stats['symbols_updated']}銘柄")
        logger.info(f"✅ 成功更新: {self.update_stats['successful_updates']}銘柄")
        logger.info(f"❌ 失敗更新: {self.update_stats['failed_updates']}銘柄")
        logger.info(f"🆕 新規作成: {self.update_stats['new_records_created']}件")
        logger.info(f"📈 成功率: {(self.update_stats['successful_updates'] / max(1, self.update_stats['symbols_updated'])) * 100:.1f}%")
        logger.info(f"✅ ステータス: DAILY UPDATE {'SUCCESS' if self.update_stats['failed_updates'] == 0 else 'PARTIAL'}")
        logger.info("=" * 70)

if __name__ == "__main__":
    updater = DailyRealDataUpdater()
    
    try:
        logger.info("🚀 日次実データ更新システム開始")
        updater.run_daily_update()
        
    except KeyboardInterrupt:
        logger.info("🛑 手動停止されました")
    except Exception as e:
        logger.error(f"❌ システムエラー: {e}")
        import traceback
        traceback.print_exc()