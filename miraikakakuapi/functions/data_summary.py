#!/usr/bin/env python3
"""
データ最大化レポート - 機械学習用データ充足状況の最終確認
"""

import sys
import os
from datetime import datetime, timedelta
from sqlalchemy import text

# パスを追加
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database.database import get_db

def generate_data_report():
    """包括的データレポート生成"""
    db = next(get_db())
    
    try:
        print("="*80)
        print("🎯 機械学習用データ最大化レポート")
        print("="*80)
        
        # 基本統計
        result = db.execute(text("""
            SELECT 
                (SELECT COUNT(*) FROM stock_master WHERE is_active = 1) as total_symbols,
                (SELECT COUNT(DISTINCT symbol) FROM stock_prices) as price_symbols,
                (SELECT COUNT(*) FROM stock_prices) as price_records,
                (SELECT COUNT(DISTINCT symbol) FROM stock_predictions) as pred_symbols,
                (SELECT COUNT(*) FROM stock_predictions) as pred_records,
                (SELECT MIN(date) FROM stock_prices) as oldest_price,
                (SELECT MAX(date) FROM stock_prices) as newest_price,
                (SELECT MIN(prediction_date) FROM stock_predictions) as oldest_pred,
                (SELECT MAX(prediction_date) FROM stock_predictions) as newest_pred
        """))
        stats = result.fetchone()
        
        print(f"📊 データベース概要")
        print(f"  利用可能銘柄数: {stats[0]:,}")
        print(f"  価格データ銘柄: {stats[1]:,} ({stats[1]/stats[0]*100:.1f}%)")
        print(f"  価格データ件数: {stats[2]:,}")
        print(f"  予測データ銘柄: {stats[3]:,}")
        print(f"  予測データ件数: {stats[4]:,}")
        print(f"  価格データ期間: {stats[5]} ～ {stats[6]}")
        print(f"  予測データ期間: {stats[7]} ～ {stats[8]}")
        
        # データ充実度分析
        result = db.execute(text("""
            SELECT 
                symbol,
                COUNT(*) as records,
                MIN(date) as from_date,
                MAX(date) as to_date,
                DATEDIFF(MAX(date), MIN(date)) as days_span
            FROM stock_prices 
            GROUP BY symbol 
            ORDER BY records DESC 
            LIMIT 10
        """))
        top_symbols = result.fetchall()
        
        print(f"\n📈 データ充実度 TOP 10")
        print("Symbol     Records   Period                 Days")
        print("-" * 50)
        for symbol, records, from_date, to_date, days in top_symbols:
            print(f"{symbol:10} {records:7,} {from_date} - {to_date} {days:4d}")
        
        # 機械学習適合性評価
        result = db.execute(text("""
            SELECT 
                symbol,
                COUNT(*) as records
            FROM stock_prices 
            GROUP BY symbol 
            HAVING COUNT(*) >= 100
            ORDER BY records DESC
        """))
        ml_ready_symbols = result.fetchall()
        
        print(f"\n🤖 機械学習対応銘柄 (100日以上のデータ)")
        print(f"  対象銘柄数: {len(ml_ready_symbols)}")
        if ml_ready_symbols:
            print("  上位5銘柄:")
            for symbol, records in ml_ready_symbols[:5]:
                print(f"    {symbol}: {records:,}件")
        
        # 予測データ品質分析
        result = db.execute(text("""
            SELECT 
                model_version,
                COUNT(*) as predictions,
                AVG(confidence_score) as avg_confidence,
                COUNT(DISTINCT symbol) as symbols
            FROM stock_predictions 
            GROUP BY model_version
            ORDER BY predictions DESC
        """))
        prediction_models = result.fetchall()
        
        print(f"\n🔮 予測モデル別統計")
        print("Model                  Predictions  Symbols  Avg Confidence")
        print("-" * 60)
        for model, preds, symbols, confidence in prediction_models:
            conf_str = f"{confidence:.3f}" if confidence else "N/A"
            print(f"{model:20} {preds:10,} {symbols:7,} {conf_str:13}")
        
        # 今日のデータ追加状況
        result = db.execute(text("""
            SELECT 
                (SELECT COUNT(*) FROM stock_prices WHERE DATE(created_at) = CURDATE()) as today_prices,
                (SELECT COUNT(*) FROM stock_predictions WHERE DATE(created_at) = CURDATE()) as today_preds,
                (SELECT COUNT(*) FROM stock_prices WHERE created_at >= NOW() - INTERVAL 1 HOUR) as hour_prices,
                (SELECT COUNT(*) FROM stock_predictions WHERE created_at >= NOW() - INTERVAL 1 HOUR) as hour_preds
        """))
        today_stats = result.fetchone()
        
        print(f"\n⚡ 最近のデータ追加")
        print(f"  今日追加: 価格{today_stats[0]:,}件, 予測{today_stats[1]:,}件")
        print(f"  直近1時間: 価格{today_stats[2]:,}件, 予測{today_stats[3]:,}件")
        
        # データ品質評価
        result = db.execute(text("""
            SELECT 
                AVG(CASE WHEN close_price IS NOT NULL THEN 1 ELSE 0 END) as price_completeness,
                AVG(CASE WHEN volume > 0 THEN 1 ELSE 0 END) as volume_completeness,
                COUNT(*) as total_records
            FROM stock_prices
        """))
        quality_stats = result.fetchone()
        
        print(f"\n✅ データ品質")
        print(f"  価格データ完全性: {quality_stats[0]*100:.1f}%")
        print(f"  出来高データ完全性: {quality_stats[1]*100:.1f}%")
        print(f"  総レコード数: {quality_stats[2]:,}")
        
        # パフォーマンス統計
        result = db.execute(text("""
            SELECT 
                ROUND(AVG(close_price), 2) as avg_price,
                ROUND(STD(close_price), 2) as price_volatility,
                COUNT(DISTINCT symbol) as unique_symbols
            FROM stock_prices 
            WHERE close_price IS NOT NULL
        """))
        perf_stats = result.fetchone()
        
        print(f"\n📊 マーケット統計")
        print(f"  平均株価: ${perf_stats[0]}")
        print(f"  価格ボラティリティ: ${perf_stats[1]}")
        print(f"  データ対象銘柄: {perf_stats[2]}")
        
        # ML訓練データ充足度評価
        ml_readiness_score = 0
        
        # 1. データ量スコア (0-30点)
        data_score = min(30, stats[2] / 10000 * 30)
        
        # 2. 銘柄多様性スコア (0-25点)
        diversity_score = min(25, stats[1] / 100 * 25)
        
        # 3. 時系列長さスコア (0-25点)
        if top_symbols:
            avg_days = sum(row[4] for row in top_symbols[:5]) / 5
            time_score = min(25, avg_days / 365 * 25)
        else:
            time_score = 0
        
        # 4. 予測データ充実度スコア (0-20点)
        pred_score = min(20, stats[4] / 5000 * 20)
        
        ml_readiness_score = data_score + diversity_score + time_score + pred_score
        
        print(f"\n🎯 機械学習適合度スコア: {ml_readiness_score:.1f}/100")
        print(f"  データ量: {data_score:.1f}/30")
        print(f"  銘柄多様性: {diversity_score:.1f}/25") 
        print(f"  時系列長さ: {time_score:.1f}/25")
        print(f"  予測データ: {pred_score:.1f}/20")
        
        # 推奨事項
        print(f"\n💡 推奨事項")
        if ml_readiness_score < 50:
            print("  ⚠️  データ不足 - さらなるデータ収集が必要")
        elif ml_readiness_score < 75:
            print("  🟡 基本レベル - MLモデルの基礎訓練が可能")
        else:
            print("  🟢 高品質 - 高度なMLモデル訓練に適している")
        
        if stats[1] < 50:
            print("  • より多くの銘柄でデータ収集を実施")
        if stats[4] < 1000:
            print("  • 予測データの生成量を増加")
        if len(ml_ready_symbols) < 20:
            print("  • 長期履歴データの充実が必要")
            
        print("="*80)
        
        return {
            'total_symbols': stats[0],
            'price_symbols': stats[1],
            'price_records': stats[2],
            'prediction_records': stats[4],
            'ml_readiness_score': ml_readiness_score,
            'ml_ready_symbols': len(ml_ready_symbols)
        }
        
    finally:
        db.close()

if __name__ == "__main__":
    report = generate_data_report()
    print(f"\n📝 レポート完了: ML適合度 {report['ml_readiness_score']:.1f}点")