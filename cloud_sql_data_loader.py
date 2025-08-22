#!/usr/bin/env python3
"""
Cloud SQLデータローダー
4,168社の日本株データをCloud SQLに投入
"""

import os
import sys
import logging
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from google.cloud.sql.connector import Connector
import pandas as pd
from datetime import datetime
import json

# ロギング設定
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 日本株データのインポート
sys.path.append('/mnt/c/Users/yuuku/cursor/miraikakaku/miraikakakudatafeed/data')
from comprehensive_japanese_stocks_enhanced import COMPREHENSIVE_JAPANESE_STOCKS

class CloudSQLDataLoader:
    def __init__(self):
        self.project_id = "pricewise-huqkr"
        self.region = "us-central1"
        self.instance_name = "miraikakaku"
        self.database_name = "miraikakaku_prod"
        self.username = "root"
        self.password = "miraikakaku2025"
        self.connector = Connector()
        self.engine = None
        self.session = None
        
    def connect_to_cloud_sql(self):
        """Cloud SQLに接続"""
        try:
            def getconn():
                conn = self.connector.connect(
                    f"{self.project_id}:{self.region}:{self.instance_name}",
                    "pymysql",
                    user=self.username,
                    password=self.password,
                    db=self.database_name
                )
                return conn
            
            self.engine = create_engine("mysql+pymysql://", creator=getconn)
            Session = sessionmaker(bind=self.engine)
            self.session = Session()
            logger.info("Cloud SQL接続成功")
            return True
            
        except Exception as e:
            logger.error(f"Cloud SQL接続エラー: {e}")
            return False
    
    def initialize_schema(self):
        """データベーススキーマを初期化"""
        try:
            # スキーマファイルを読み込み
            with open('/mnt/c/Users/yuuku/cursor/miraikakaku/miraikakakuapi/functions/database/schema.sql', 'r', encoding='utf-8') as f:
                schema_sql = f.read()
            
            # SQLステートメントを分割して実行
            statements = [stmt.strip() for stmt in schema_sql.split(';') if stmt.strip()]
            
            for statement in statements:
                if statement:
                    try:
                        self.session.execute(text(statement))
                        self.session.commit()
                    except Exception as e:
                        if "already exists" in str(e).lower():
                            logger.info(f"テーブル既存: {statement[:50]}...")
                        else:
                            logger.warning(f"SQL実行警告: {e}")
            
            logger.info("スキーマ初期化完了")
            return True
            
        except Exception as e:
            logger.error(f"スキーマ初期化エラー: {e}")
            return False
    
    def insert_stock_master_data(self):
        """株式マスターデータを投入"""
        try:
            logger.info(f"株式データ投入開始: {len(COMPREHENSIVE_JAPANESE_STOCKS)}社")
            
            # 既存データを確認
            result = self.session.execute(text("SELECT COUNT(*) as count FROM stock_master"))
            existing_count = result.fetchone()[0]
            logger.info(f"既存データ: {existing_count}社")
            
            if existing_count > 0:
                # データをクリア
                self.session.execute(text("DELETE FROM stock_master WHERE market IN ('プライム', 'スタンダード', 'グロース')"))
                self.session.commit()
                logger.info("既存日本株データクリア完了")
            
            # バッチ投入用データ準備
            batch_data = []
            for symbol, info in COMPREHENSIVE_JAPANESE_STOCKS.items():
                batch_data.append({
                    'symbol': symbol,
                    'name': info['name'],
                    'sector': info['sector'],
                    'market': info['market'],
                    'country': 'Japan',
                    'currency': 'JPY',
                    'is_active': True,
                    'created_at': datetime.now(),
                    'updated_at': datetime.now()
                })
            
            # バッチ投入 (1000件ずつ)
            batch_size = 1000
            total_inserted = 0
            
            for i in range(0, len(batch_data), batch_size):
                batch = batch_data[i:i + batch_size]
                
                # SQL作成
                values_sql = []
                for data in batch:
                    values_sql.append(f"""(
                        '{data['symbol']}',
                        '{data['name'].replace("'", "''")}',
                        '{data['sector']}',
                        '{data['market']}',
                        '{data['country']}',
                        '{data['currency']}',
                        {data['is_active']},
                        NOW(),
                        NOW()
                    )""")
                
                insert_sql = f"""
                INSERT INTO stock_master 
                (symbol, name, sector, market, country, currency, is_active, created_at, updated_at)
                VALUES {','.join(values_sql)}
                """
                
                self.session.execute(text(insert_sql))
                self.session.commit()
                total_inserted += len(batch)
                
                logger.info(f"投入進捗: {total_inserted}/{len(batch_data)}社")
            
            logger.info(f"株式マスターデータ投入完了: {total_inserted}社")
            return True
            
        except Exception as e:
            logger.error(f"データ投入エラー: {e}")
            self.session.rollback()
            return False
    
    def verify_data(self):
        """データ投入を検証"""
        try:
            # 市場別カウント
            result = self.session.execute(text("""
                SELECT market, COUNT(*) as count 
                FROM stock_master 
                WHERE country = 'Japan'
                GROUP BY market
            """))
            
            logger.info("=== データ投入検証結果 ===")
            total = 0
            for row in result:
                logger.info(f"{row.market}: {row.count}社")
                total += row.count
            
            logger.info(f"合計: {total}社")
            
            # セクター別上位10
            result = self.session.execute(text("""
                SELECT sector, COUNT(*) as count 
                FROM stock_master 
                WHERE country = 'Japan'
                GROUP BY sector 
                ORDER BY count DESC 
                LIMIT 10
            """))
            
            logger.info("=== セクター別上位10 ===")
            for row in result:
                logger.info(f"{row.sector}: {row.count}社")
            
            return True
            
        except Exception as e:
            logger.error(f"検証エラー: {e}")
            return False
    
    def close_connection(self):
        """接続をクローズ"""
        if self.session:
            self.session.close()
        if self.connector:
            self.connector.close()

def main():
    """メイン処理"""
    loader = CloudSQLDataLoader()
    
    try:
        # 1. Cloud SQL接続
        if not loader.connect_to_cloud_sql():
            logger.error("Cloud SQL接続失敗")
            return False
        
        # 2. スキーマ初期化
        if not loader.initialize_schema():
            logger.error("スキーマ初期化失敗")
            return False
        
        # 3. データ投入
        if not loader.insert_stock_master_data():
            logger.error("データ投入失敗")
            return False
        
        # 4. 検証
        if not loader.verify_data():
            logger.error("データ検証失敗")
            return False
        
        logger.info("🎉 全データのCloud SQL投入が完了しました！")
        return True
        
    except Exception as e:
        logger.error(f"処理中にエラーが発生: {e}")
        return False
    
    finally:
        loader.close_connection()

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)