#!/usr/bin/env python3
"""
モック・バルク・サンプルデータ一括削除スクリプト
"""

import pymysql
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    db_config = {
        "host": "34.58.103.36",
        "user": "miraikakaku-user", 
        "password": "miraikakaku-secure-pass-2024",
        "database": "miraikakaku",
    }
    
    connection = pymysql.connect(**db_config)
    
    try:
        with connection.cursor() as cursor:
            # 削除対象データソースの特定と削除
            mock_sources = [
                'bulk_100pct',  # バルクデータ
                'us_massive_batch_001',  # 過去の大量生成データ
                'us_massive_batch_002',
                'us_massive_batch_003',
                'us_massive_batch_004',
                'us_massive_batch_005',
                'us_massive_batch_006',
                'us_massive_batch_007',
                'us_massive_batch_008',
                'us_massive_batch_009',
                'us_massive_batch_010'
            ]
            
            total_deleted = 0
            
            for source in mock_sources:
                logger.info(f"🧹 削除対象: {source}")
                
                # 削除前の件数確認
                cursor.execute("SELECT COUNT(*) FROM stock_price_history WHERE data_source = %s", (source,))
                before_count = cursor.fetchone()[0]
                
                if before_count > 0:
                    # データ削除実行
                    cursor.execute("DELETE FROM stock_price_history WHERE data_source = %s", (source,))
                    deleted_count = cursor.rowcount
                    total_deleted += deleted_count
                    
                    logger.info(f"✅ {source}: {deleted_count}件削除")
                else:
                    logger.info(f"⭕ {source}: データなし")
            
            # 孤立した株式マスターデータ削除はスキップ（文字エンコード問題回避）
            orphaned_masters = 0
            logger.info("⭕ 孤立master削除はスキップ（文字エンコード問題）")
            
            connection.commit()
            logger.info("=" * 50)
            logger.info("🧹 モック・バルクデータ削除完了")
            logger.info(f"📊 price_history削除: {total_deleted}件")
            logger.info(f"📊 孤立master削除: {orphaned_masters}件")
            logger.info("=" * 50)
            
    except Exception as e:
        logger.error(f"❌ エラー: {e}")
        connection.rollback()
    finally:
        connection.close()

if __name__ == "__main__":
    main()