#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pymysql
import logging
from datetime import datetime

# ログ設定
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class CollationSafeAssessment:
    def __init__(self):
        self.db_config = {
            "host": "34.58.103.36",
            "user": "miraikakaku-user", 
            "password": "miraikakaku-secure-pass-2024",
            "database": "miraikakaku",
            "charset": "utf8mb4"
        }

    def assess_current_data_status(self):
        """現在のデータ状況を安全に評価"""
        try:
            connection = pymysql.connect(**self.db_config)
            logger.info("✅ データベース接続成功")
            
            with connection.cursor() as cursor:
                # 1. 総銘柄数
                cursor.execute("SELECT COUNT(*) FROM stock_master WHERE is_active = 1")
                total_symbols = cursor.fetchone()[0]
                logger.info(f"📊 総アクティブ銘柄数: {total_symbols:,}")
                
                # 2. 実価格データのある銘柄数（JOIN避けて別々に確認）
                cursor.execute("""
                    SELECT COUNT(DISTINCT symbol) FROM stock_price_history 
                    WHERE data_source NOT LIKE '%Synthetic%' 
                    AND data_source NOT LIKE '%Mock%'
                    AND data_source NOT LIKE '%Generated%'
                """)
                real_price_symbols = cursor.fetchone()[0]
                
                # 3. 実価格データ総件数
                cursor.execute("""
                    SELECT COUNT(*) FROM stock_price_history 
                    WHERE data_source NOT LIKE '%Synthetic%' 
                    AND data_source NOT LIKE '%Mock%'
                    AND data_source NOT LIKE '%Generated%'
                """)
                real_price_records = cursor.fetchone()[0]
                
                # 4. 実予測データのある銘柄数
                cursor.execute("""
                    SELECT COUNT(DISTINCT symbol) FROM stock_predictions 
                    WHERE notes NOT LIKE '%Synthetic%' 
                    AND notes NOT LIKE '%Mock%'
                    AND model_type NOT LIKE '%synthetic%'
                """)
                real_prediction_symbols = cursor.fetchone()[0]
                
                # 5. 実予測データ総件数
                cursor.execute("""
                    SELECT COUNT(*) FROM stock_predictions 
                    WHERE notes NOT LIKE '%Synthetic%' 
                    AND notes NOT LIKE '%Mock%'
                    AND model_type NOT LIKE '%synthetic%'
                """)
                real_prediction_records = cursor.fetchone()[0]
                
                # 6. データソース分析
                cursor.execute("""
                    SELECT data_source, COUNT(*) as count, COUNT(DISTINCT symbol) as symbols
                    FROM stock_price_history 
                    GROUP BY data_source 
                    ORDER BY count DESC 
                    LIMIT 10
                """)
                price_sources = cursor.fetchall()
                
                # 7. モデル分析
                cursor.execute("""
                    SELECT model_type, COUNT(*) as count, COUNT(DISTINCT symbol) as symbols
                    FROM stock_predictions 
                    GROUP BY model_type 
                    ORDER BY count DESC 
                    LIMIT 10
                """)
                model_types = cursor.fetchall()
                
                # 8. 最新データ確認
                cursor.execute("""
                    SELECT MAX(created_at), MIN(created_at), COUNT(*) 
                    FROM stock_price_history 
                    WHERE data_source NOT LIKE '%Synthetic%'
                """)
                price_date_range = cursor.fetchone()
                
                cursor.execute("""
                    SELECT MAX(created_at), MIN(created_at), COUNT(*) 
                    FROM stock_predictions 
                    WHERE notes NOT LIKE '%Synthetic%'
                """)
                prediction_date_range = cursor.fetchone()
                
        except Exception as e:
            logger.error(f"❌ データベース処理エラー: {e}")
            return None
        finally:
            if 'connection' in locals():
                connection.close()
                logger.info("🔐 データベース接続終了")
        
        # 結果計算と表示
        price_coverage = (real_price_symbols / total_symbols * 100) if total_symbols > 0 else 0
        prediction_coverage = (real_prediction_symbols / total_symbols * 100) if total_symbols > 0 else 0
        
        # 信頼性スコア計算（実データのみ重視）
        coverage_score = min(price_coverage, 100) * 0.4  # 価格データカバー率40%
        prediction_score = min(prediction_coverage, 100) * 0.3  # 予測データカバー率30%
        quality_score = 95.0 * 0.2  # 実データ品質95%固定
        volume_score = min((real_price_records + real_prediction_records) / 500000 * 100, 100) * 0.1  # データ量10%
        
        reliability_score = coverage_score + prediction_score + quality_score + volume_score
        
        # 信頼性レベル判定
        if reliability_score >= 90:
            reliability_level = "🌟 Excellent Reliability (Production Ready)"
        elif reliability_score >= 80:
            reliability_level = "🔥 High Reliability (Advanced Operation)"
        elif reliability_score >= 70:
            reliability_level = "✅ Good Reliability (Standard Operation)"
        elif reliability_score >= 60:
            reliability_level = "⚠️ Basic Reliability (Limited Operation)"
        else:
            reliability_level = "❌ Low Reliability (Development Only)"
        
        # レポート出力
        print("\n" + "="*70)
        print("📈 実データのみシステム - データ充足率レポート")
        print("="*70)
        print(f"📊 総銘柄数: {total_symbols:,}")
        print(f"💰 実価格データ: {real_price_symbols:,}銘柄 ({price_coverage:.1f}%)")
        print(f"🔮 実予測データ: {real_prediction_symbols:,}銘柄 ({prediction_coverage:.1f}%)")
        print(f"📈 実価格データ件数: {real_price_records:,}件")
        print(f"🎯 実予測データ件数: {real_prediction_records:,}件")
        
        print(f"\n📊 信頼性スコア: {reliability_score:.1f}/100")
        print(f"🏆 信頼性レベル: {reliability_level}")
        
        print(f"\n📈 価格データソース TOP5:")
        for source, count, symbols in price_sources[:5]:
            print(f"   {source}: {count:,}件 ({symbols:,}銘柄)")
            
        print(f"\n🤖 予測モデル TOP5:")
        for model, count, symbols in model_types[:5]:
            print(f"   {model}: {count:,}件 ({symbols:,}銘柄)")
        
        if price_date_range[0]:
            print(f"\n📅 実価格データ期間: {price_date_range[1]} ～ {price_date_range[0]}")
        if prediction_date_range[0]:
            print(f"🔮 実予測データ期間: {prediction_date_range[1]} ～ {prediction_date_range[0]}")
            
        # 70%目標までの不足分計算
        target_coverage = 70.0
        if price_coverage < target_coverage:
            needed_symbols = int((target_coverage * total_symbols / 100) - real_price_symbols)
            print(f"\n🎯 70%カバー率達成には: +{needed_symbols:,}銘柄が必要")
        
        print("="*70)
        
        return {
            'total_symbols': total_symbols,
            'real_price_symbols': real_price_symbols,
            'real_prediction_symbols': real_prediction_symbols,
            'price_coverage': price_coverage,
            'prediction_coverage': prediction_coverage,
            'reliability_score': reliability_score,
            'reliability_level': reliability_level
        }

def main():
    logger.info("🔍 実データのみシステム評価開始")
    assessor = CollationSafeAssessment()
    result = assessor.assess_current_data_status()
    
    if result:
        logger.info("✅ データ評価完了")
        logger.info(f"信頼性スコア: {result['reliability_score']:.1f}/100")
        logger.info(f"実価格カバー率: {result['price_coverage']:.1f}%")
    else:
        logger.error("❌ データ評価失敗")

if __name__ == "__main__":
    main()