#!/usr/bin/env python3
"""
大規模バッチの動作テスト (50銘柄)
全12,112銘柄実行前の動作確認
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from massive_full_expansion import MassiveFullExpansion
from database.cloud_sql_only import db
from sqlalchemy import text
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_massive_batch():
    """50銘柄でのテスト実行"""
    
    logger.info("🧪 大規模バッチのテスト実行開始 (50銘柄)")
    
    # テスト用に銘柄数を制限
    expander = MassiveFullExpansion()
    
    # 少数の銘柄のみ取得
    with db.engine.connect() as conn:
        result = conn.execute(text("""
            SELECT symbol, name, country, currency 
            FROM stock_master 
            WHERE is_active = 1 
            ORDER BY symbol
            LIMIT 50
        """)).fetchall()
        
        test_symbols = [(row[0], row[1], row[2], row[3]) for row in result]
    
    logger.info(f"📊 テスト対象: {len(test_symbols)}銘柄")
    
    # テスト前の統計
    with db.engine.connect() as conn:
        before_prices = conn.execute(text("SELECT COUNT(*) FROM stock_prices")).scalar()
        before_predictions = conn.execute(text("SELECT COUNT(*) FROM stock_predictions")).scalar()
    
    logger.info(f"📈 実行前: 価格{before_prices:,}件, 予測{before_predictions:,}件")
    
    # テスト実行
    start_time = time.time()
    successful = 0
    failed = 0
    
    for symbol_data in test_symbols:
        result = expander.bulk_data_generation(symbol_data)
        
        if result['status'] == 'success':
            successful += 1
            logger.info(f"✅ {result['symbol']}: 価格+{result['prices']}, 予測+{result['predictions']}")
        else:
            failed += 1
            logger.warning(f"❌ {result['symbol']}: {result['error']}")
    
    # テスト後の統計
    with db.engine.connect() as conn:
        after_prices = conn.execute(text("SELECT COUNT(*) FROM stock_prices")).scalar()
        after_predictions = conn.execute(text("SELECT COUNT(*) FROM stock_predictions")).scalar()
    
    duration = time.time() - start_time
    
    logger.info("="*60)
    logger.info("🧪 テスト完了")
    logger.info(f"⏱️  実行時間: {duration:.1f}秒")
    logger.info(f"✅ 成功: {successful}/{len(test_symbols)}")
    logger.info(f"❌ 失敗: {failed}/{len(test_symbols)}")
    logger.info(f"📈 価格データ: {before_prices:,} → {after_prices:,} (+{after_prices-before_prices:,})")
    logger.info(f"🔮 予測データ: {before_predictions:,} → {after_predictions:,} (+{after_predictions-before_predictions:,})")
    logger.info(f"🎯 処理速度: {len(test_symbols)/duration:.1f}銘柄/秒")
    logger.info("="*60)
    
    if successful > len(test_symbols) * 0.7:  # 70%以上成功
        logger.info("🎉 テスト成功！全銘柄実行の準備完了")
        return True
    else:
        logger.error("❌ テスト失敗。修正が必要です")
        return False

if __name__ == "__main__":
    import time
    test_massive_batch()