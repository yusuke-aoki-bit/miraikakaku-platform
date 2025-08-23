#!/usr/bin/env python3
"""
最適データジェネレーター - 確実で高速なデータ生成
"""

import sys, os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database.cloud_sql_only import db
from sqlalchemy import text
import numpy as np
from datetime import datetime, timedelta
import random
import logging
import time

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

def generate_ai_factors_optimized():
    """最適化されたAI決定要因生成"""
    logger.info("🧠 AI決定要因生成開始")
    
    # シンプルなテンプレート
    templates = [
        ("technical", "RSI分析", "RSI指標による買売判定"),
        ("technical", "移動平均分析", "短期・長期移動平均の位置関係"),
        ("technical", "ボリューム分析", "出来高トレンドによる強弱判定"),
        ("fundamental", "PER評価", "株価収益率による割安性評価"),
        ("fundamental", "成長率分析", "業績成長率の持続性評価"),
        ("sentiment", "市場心理", "投資家センチメント指標"),
        ("pattern", "チャートパターン", "テクニカルパターン認識"),
        ("news", "業績影響", "決算・業績発表による影響度")
    ]
    
    added = 0
    batch_size = 1000
    
    try:
        # 予測IDを分割取得
        with db.engine.connect() as conn:
            total_predictions = conn.execute(text("SELECT COUNT(*) FROM stock_predictions")).scalar()
            logger.info(f"対象予測数: {total_predictions:,}")
            
            # バッチ処理
            for offset in range(0, min(total_predictions, 20000), batch_size):
                prediction_ids = conn.execute(text('''
                    SELECT id FROM stock_predictions 
                    ORDER BY id LIMIT :limit OFFSET :offset
                '''), {'limit': batch_size, 'offset': offset}).fetchall()
                
                batch_data = []
                for (pred_id,) in prediction_ids:
                    # 各予測に3-5個の要因
                    num_factors = random.randint(3, 5)
                    selected = random.sample(templates, num_factors)
                    
                    for factor_type, name, desc in selected:
                        batch_data.append({
                            'prediction_id': pred_id,
                            'factor_type': factor_type,
                            'factor_name': name,
                            'influence_score': round(random.uniform(50, 90), 2),
                            'description': desc,
                            'confidence': round(random.uniform(70, 95), 2)
                        })
                
                # バッチ挿入
                if batch_data:
                    conn.execute(text('''
                        INSERT IGNORE INTO ai_decision_factors 
                        (prediction_id, factor_type, factor_name, influence_score, 
                         description, confidence, created_at)
                        VALUES (:prediction_id, :factor_type, :factor_name, :influence_score,
                                :description, :confidence, NOW())
                    '''), batch_data)
                    conn.commit()
                    added += len(batch_data)
                    
                    logger.info(f"バッチ完了: {added:,}件追加済み")
                    
                # 安全な間隔
                time.sleep(0.1)
                
    except Exception as e:
        logger.error(f"AI要因生成エラー: {e}")
    
    logger.info(f"✅ AI決定要因完了: {added:,}件追加")
    return added

def generate_theme_insights_optimized():
    """最適化されたテーマ洞察生成"""
    logger.info("🎯 テーマ洞察生成開始")
    
    # 厳選テーマ
    themes = [
        ("AI Technology", "technology", "人工知能技術の急速な発展"),
        ("Green Energy", "energy", "再生可能エネルギーへの転換加速"),
        ("Digital Health", "healthcare", "デジタルヘルスケアの普及"),
        ("Fintech Growth", "finance", "金融テクノロジーの革新"),
        ("E-commerce Boom", "consumer", "オンライン商取引の拡大"),
        ("5G Revolution", "communication", "第5世代通信技術の展開"),
        ("EV Adoption", "transportation", "電気自動車の普及拡大"),
        ("Cybersecurity", "technology", "サイバーセキュリティ需要増"),
        ("Cloud Computing", "technology", "クラウドサービスの成長"),
        ("Sustainable Investing", "finance", "ESG投資の主流化")
    ]
    
    stocks = ["AAPL", "GOOGL", "MSFT", "AMZN", "TSLA", "NVDA", "META", "JPM", "JNJ", "V"]
    
    added = 0
    batch_data = []
    
    try:
        with db.engine.connect() as conn:
            for theme_name, category, driver in themes:
                # 各テーマ50個の洞察
                for i in range(50):
                    insight_date = datetime.now().date() - timedelta(days=random.randint(0, 60))
                    
                    batch_data.append({
                        'theme_name': f"{theme_name} #{i+1}",
                        'theme_category': category,
                        'insight_date': insight_date,
                        'key_drivers': f"{driver}, 市場成長率{random.randint(20,80)}%, 投資拡大",
                        'affected_stocks': ", ".join(random.sample(stocks, random.randint(3, 6))),
                        'impact_score': round(random.uniform(60, 95), 1),
                        'prediction_accuracy': round(random.uniform(0.70, 0.90), 3)
                    })
                    
                    # バッチサイズ100で挿入
                    if len(batch_data) >= 100:
                        conn.execute(text('''
                            INSERT INTO theme_insights 
                            (theme_name, theme_category, insight_date, key_drivers,
                             affected_stocks, impact_score, prediction_accuracy, created_at)
                            VALUES (:theme_name, :theme_category, :insight_date, :key_drivers,
                                    :affected_stocks, :impact_score, :prediction_accuracy, NOW())
                        '''), batch_data)
                        conn.commit()
                        added += len(batch_data)
                        batch_data = []
                        
                        logger.info(f"テーマ洞察: {added:,}件追加済み")
                        time.sleep(0.1)
                        
            # 残りを挿入
            if batch_data:
                conn.execute(text('''
                    INSERT INTO theme_insights 
                    (theme_name, theme_category, insight_date, key_drivers,
                     affected_stocks, impact_score, prediction_accuracy, created_at)
                    VALUES (:theme_name, :theme_category, :insight_date, :key_drivers,
                            :affected_stocks, :impact_score, :prediction_accuracy, NOW())
                '''), batch_data)
                conn.commit()
                added += len(batch_data)
                
    except Exception as e:
        logger.error(f"テーマ洞察生成エラー: {e}")
    
    logger.info(f"✅ テーマ洞察完了: {added:,}件追加")
    return added

def main():
    """メイン実行"""
    start_time = time.time()
    
    logger.info("="*60)
    logger.info("🚀 最適データ生成開始")
    logger.info("="*60)
    
    # 並行実行
    ai_added = generate_ai_factors_optimized()
    theme_added = generate_theme_insights_optimized()
    
    # 結果確認
    with db.engine.connect() as conn:
        ai_total = conn.execute(text("SELECT COUNT(*) FROM ai_decision_factors")).scalar()
        theme_total = conn.execute(text("SELECT COUNT(*) FROM theme_insights")).scalar()
        
        # 価格・予測データも確認
        price_total = conn.execute(text("SELECT COUNT(*) FROM stock_prices")).scalar()
        pred_total = conn.execute(text("SELECT COUNT(*) FROM stock_predictions")).scalar()
        
        # 充足率計算
        symbols = conn.execute(text("SELECT COUNT(*) FROM stock_master WHERE is_active = 1")).scalar()
        
        price_rate = (price_total / (symbols * 1000)) * 100 if symbols > 0 else 0
        pred_rate = (pred_total / (symbols * 100)) * 100 if symbols > 0 else 0
        
    elapsed = time.time() - start_time
    
    logger.info("="*60)
    logger.info("🎯 最適データ生成完了")
    logger.info(f"⏱️  実行時間: {elapsed:.2f}秒")
    logger.info(f"🧠 AI決定要因: {ai_total:,}件 (+{ai_added:,})")
    logger.info(f"🎯 テーマ洞察: {theme_total:,}件 (+{theme_added:,})")
    logger.info(f"💰 価格データ: {price_total:,}件 (充足率: {price_rate:.1f}%)")
    logger.info(f"🔮 予測データ: {pred_total:,}件 (充足率: {pred_rate:.1f}%)")
    logger.info("="*60)

if __name__ == "__main__":
    main()