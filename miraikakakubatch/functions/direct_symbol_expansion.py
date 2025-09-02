#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pymysql
import yfinance as yf
import pandas as pd
import logging
import time
from datetime import datetime, timedelta

# ログ設定
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DirectSymbolExpansion:
    def __init__(self):
        self.db_config = {
            "host": "34.58.103.36",
            "user": "miraikakaku-user",
            "password": "miraikakaku-secure-pass-2024",
            "database": "miraikakaku",
            "charset": "utf8mb4"
        }
        
        # 追加したい高確率成功銘柄リスト
        self.reliable_symbols = [
            # 追加US主要株
            'AMD', 'QCOM', 'NFLX', 'ADBE', 'CRM', 'PYPL', 'UBER', 'SHOP',
            'ZM', 'SQ', 'ROKU', 'TWLO', 'OKTA', 'SNOW', 'CRWD', 'ZS',
            'DDOG', 'NET', 'MDB', 'FSLY', 'ESTC', 'TEAM', 'WDAY', 'NOW',
            'SPLK', 'VEEV', 'ZI', 'DOCU', 'ZOOM', 'PLTR', 'RBLX',
            
            # 追加ETF
            'ARKK', 'ARKQ', 'ARKG', 'ARKF', 'ARKW', 'ICLN', 'JETS', 'MOON',
            'HACK', 'CLOU', 'FINX', 'EDOC', 'HERO', 'ESPO', 'GAMR', 'NERD',
            'FXI', 'EWJ', 'EWZ', 'EEM', 'VEA', 'VWO', 'IEMG', 'IXUS',
            
            # セクターETF
            'XBI', 'IBB', 'XRT', 'IYR', 'XME', 'XOP', 'KBE', 'SMH',
            'SOXX', 'IGV', 'SKYY', 'BOTZ', 'ROBO', 'QTUM', 'BLOK', 'BKCH',
            
            # 国際ETF
            'VGK', 'VPL', 'VGE', 'VSS', 'VBR', 'VBK', 'VUG', 'VTV',
            'VTEB', 'VGIT', 'VGSH', 'VGLT', 'VMOT', 'VCSH', 'VCIT', 'VCLT',
            
            # 債券・コモディティ
            'AGG', 'BND', 'VBTLX', 'SCHZ', 'IAU', 'PDBC', 'DJP', 'DBA',
            'UNG', 'UCO', 'BOIL', 'KOLD', 'UUP', 'FXE', 'FXY', 'FXA',
            
            # 仮想通貨関連
            'COIN', 'RIOT', 'MARA', 'HUT', 'BITF', 'HIVE', 'DMGI', 'ARBK',
            
            # 日本追加株
            '1301.T', '1332.T', '1333.T', '2269.T', '2282.T', '2432.T',
            '3382.T', '3659.T', '4324.T', '4689.T', '4704.T', '6178.T',
            '6723.T', '6724.T', '6857.T', '7182.T', '8304.T', '9613.T',
            '9984.T', '4385.T', '3092.T', '4477.T', '3793.T', '6185.T'
        ]

    def check_existing_data(self, symbol):
        """既存データの確認（直接クエリ）"""
        try:
            connection = pymysql.connect(**self.db_config)
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT COUNT(*) FROM stock_price_history 
                    WHERE symbol = %s AND data_source = 'yfinance'
                """, (symbol,))
                count = cursor.fetchone()[0]
                return count > 0
        except Exception as e:
            logger.error(f"既存データ確認エラー {symbol}: {e}")
            return True  # エラーの場合はスキップ
        finally:
            if 'connection' in locals():
                connection.close()

    def add_symbol_to_master(self, symbol):
        """銘柄をstock_masterに追加"""
        try:
            connection = pymysql.connect(**self.db_config)
            with connection.cursor() as cursor:
                # シンボル情報の推定
                if symbol.endswith('.T'):
                    country, exchange = 'Japan', 'TSE'
                    name = f"Japanese Stock {symbol.replace('.T', '')}"
                elif symbol in ['COIN', 'RIOT', 'MARA']:
                    country, exchange = 'US', 'NASDAQ'
                    name = f"Crypto-related {symbol}"
                elif any(x in symbol for x in ['ARK', 'XBI', 'IBB', 'XRT']):
                    country, exchange = 'US', 'NYSE/NASDAQ'
                    name = f"ETF {symbol}"
                else:
                    country, exchange = 'US', 'NYSE/NASDAQ'
                    name = f"US Stock {symbol}"
                
                cursor.execute("""
                    INSERT IGNORE INTO stock_master 
                    (symbol, name, country, exchange, sector, is_active)
                    VALUES (%s, %s, %s, %s, 'Technology', 1)
                """, (symbol, name, country, exchange))
                
                connection.commit()
                return cursor.rowcount > 0
        except Exception as e:
            logger.error(f"master追加エラー {symbol}: {e}")
            return False
        finally:
            if 'connection' in locals():
                connection.close()

    def fetch_reliable_yfinance(self, symbol):
        """信頼性の高いyfinanceデータ取得"""
        try:
            ticker = yf.Ticker(symbol)
            
            # 過去6ヶ月分取得（高速化）
            end_date = datetime.now()
            start_date = end_date - timedelta(days=180)
            
            hist_data = ticker.history(
                start=start_date.strftime('%Y-%m-%d'),
                end=end_date.strftime('%Y-%m-%d'),
                interval='1d',
                auto_adjust=True
            )
            
            if hist_data.empty:
                return None
                
            price_data = []
            for date, row in hist_data.iterrows():
                try:
                    # 基本検証
                    if pd.isna([row['Open'], row['High'], row['Low'], row['Close'], row['Volume']]).any():
                        continue
                    
                    if any(v <= 0 for v in [row['Open'], row['High'], row['Low'], row['Close']]):
                        continue
                        
                    if row['Volume'] < 0:
                        continue
                    
                    price_data.append({
                        'symbol': symbol,
                        'date': date.strftime('%Y-%m-%d'),
                        'open_price': float(row['Open']),
                        'high_price': float(row['High']),
                        'low_price': float(row['Low']),
                        'close_price': float(row['Close']),
                        'adjusted_close': float(row['Close']),
                        'volume': int(row['Volume']),
                        'data_source': 'yfinance',
                        'is_valid': 1,
                        'data_quality_score': 0.97
                    })
                except (ValueError, OverflowError):
                    continue
            
            return price_data if len(price_data) >= 30 else None
            
        except Exception as e:
            logger.warning(f"yfinance取得失敗 {symbol}: {e}")
            return None

    def save_direct_data(self, price_data_list):
        """直接データ保存"""
        if not price_data_list:
            return 0
            
        try:
            connection = pymysql.connect(**self.db_config)
            with connection.cursor() as cursor:
                insert_data = []
                for data in price_data_list:
                    insert_data.append((
                        data['symbol'], data['date'],
                        data['open_price'], data['high_price'],
                        data['low_price'], data['close_price'],
                        data['volume'], data['adjusted_close'],
                        data['data_source'], data['is_valid'],
                        data['data_quality_score']
                    ))
                
                cursor.executemany("""
                    INSERT IGNORE INTO stock_price_history 
                    (symbol, date, open_price, high_price, low_price, close_price,
                     volume, adjusted_close, data_source, is_valid, data_quality_score, created_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())
                """, insert_data)
                
                connection.commit()
                return cursor.rowcount
                
        except Exception as e:
            logger.error(f"直接保存エラー: {e}")
            return 0
        finally:
            if 'connection' in locals():
                connection.close()

    def expand_direct_symbols(self, max_symbols=150):
        """直接銘柄拡張"""
        logger.info(f"🎯 直接銘柄拡張開始 - 対象: {len(self.reliable_symbols)}銘柄")
        
        successful = 0
        failed = 0
        total_records = 0
        
        for i, symbol in enumerate(self.reliable_symbols[:max_symbols]):
            try:
                logger.info(f"📊 処理中 {i+1}/{min(max_symbols, len(self.reliable_symbols))}: {symbol}")
                
                # 既存データ確認
                if self.check_existing_data(symbol):
                    logger.info(f"⏭️ {symbol}: 既存データあり、スキップ")
                    continue
                
                # stock_masterに追加
                self.add_symbol_to_master(symbol)
                
                # yfinanceデータ取得
                price_data = self.fetch_reliable_yfinance(symbol)
                
                if price_data:
                    saved_count = self.save_direct_data(price_data)
                    if saved_count > 0:
                        successful += 1
                        total_records += saved_count
                        logger.info(f"✅ {symbol}: {saved_count}件保存成功")
                    else:
                        failed += 1
                        logger.warning(f"⚠️ {symbol}: 保存失敗")
                else:
                    failed += 1
                    logger.warning(f"❌ {symbol}: データ取得失敗")
                
                # レート制限対応
                time.sleep(0.3)
                
                # 進捗報告
                if (successful + failed) % 20 == 0 and (successful + failed) > 0:
                    progress = ((i + 1) / min(max_symbols, len(self.reliable_symbols))) * 100
                    success_rate = (successful / (successful + failed)) * 100
                    logger.info(f"📈 進捗: {progress:.1f}% | 成功: {successful}, 失敗: {failed} | 成功率: {success_rate:.1f}%")
                
            except Exception as e:
                failed += 1
                logger.error(f"❌ {symbol}: 処理エラー - {e}")
        
        # 最終結果
        total_processed = successful + failed
        final_success_rate = (successful / total_processed * 100) if total_processed > 0 else 0
        
        logger.info(f"🎯 直接銘柄拡張完了:")
        logger.info(f"   - 処理銘柄: {total_processed}")
        logger.info(f"   - 成功銘柄: {successful} ({final_success_rate:.1f}%)")
        logger.info(f"   - 失敗銘柄: {failed}")
        logger.info(f"   - 収集データ: {total_records:,}件")
        
        return {
            'total': total_processed,
            'successful': successful,
            'failed': failed,
            'total_records': total_records,
            'success_rate': final_success_rate
        }

def main():
    logger.info("🎯 直接銘柄拡張システム開始")
    
    expander = DirectSymbolExpansion()
    result = expander.expand_direct_symbols(max_symbols=100)
    
    if result['successful'] > 0:
        logger.info("✅ 直接銘柄拡張成功 - 評価実行中...")
        
        # 拡張後の評価
        import subprocess
        subprocess.run(["python3", "collation_safe_data_assessment.py"])
    else:
        logger.error("❌ 直接銘柄拡張失敗")

if __name__ == "__main__":
    main()