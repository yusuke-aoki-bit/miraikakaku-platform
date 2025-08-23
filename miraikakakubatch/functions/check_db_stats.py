#!/usr/bin/env python3
"""
データベース統計確認スクリプト
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from database.cloud_sql_only import db
from datetime import datetime

def check_database_stats():
    """データベースの統計情報を確認"""
    print("🔍 データベース統計情報確認中...")
    print("=" * 60)
    
    try:
        # 基本統計
        from sqlalchemy import text
        with db.engine.connect() as conn:
            # 銘柄数
            result = conn.execute(text("SELECT COUNT(*) as count FROM stock_master")).fetchone()
            stock_count = result[0] if result else 0
            print(f"📊 銘柄数: {stock_count:,}")
            
            # 価格データ数
            result = conn.execute(text("SELECT COUNT(*) as count FROM stock_prices")).fetchone()
            price_count = result[0] if result else 0
            print(f"💰 価格データ数: {price_count:,}")
            
            # 予測データ数
            result = conn.execute(text("SELECT COUNT(*) as count FROM stock_predictions")).fetchone()
            prediction_count = result[0] if result else 0
            print(f"🔮 予測データ数: {prediction_count:,}")
            
            # AI決定要因数
            result = conn.execute(text("SELECT COUNT(*) as count FROM ai_decision_factors")).fetchone()
            factors_count = result[0] if result else 0
            print(f"🧠 AI決定要因数: {factors_count:,}")
            
            # テーマ洞察数
            result = conn.execute(text("SELECT COUNT(*) as count FROM theme_insights")).fetchone()
            themes_count = result[0] if result else 0
            print(f"🎯 テーマ洞察数: {themes_count:,}")
            
            print("=" * 60)
            
            # 最新データ確認
            print("📅 最新データ日時:")
            
            # 最新価格データ
            result = conn.execute(text("SELECT MAX(date) FROM stock_prices")).fetchone()
            latest_price = result[0] if result else None
            print(f"   価格データ: {latest_price}")
            
            # 最新予測データ
            result = conn.execute(text("SELECT MAX(prediction_date) FROM stock_predictions")).fetchone()
            latest_prediction = result[0] if result else None
            print(f"   予測データ: {latest_prediction}")
            
            print("=" * 60)
            
            # 充足率計算
            if stock_count > 0:
                # 1銘柄あたりの平均価格データ数
                avg_prices = price_count / stock_count if stock_count > 0 else 0
                print(f"📈 1銘柄あたり平均価格データ数: {avg_prices:.1f}")
                
                # 1銘柄あたりの平均予測データ数
                avg_predictions = prediction_count / stock_count if stock_count > 0 else 0
                print(f"🔮 1銘柄あたり平均予測データ数: {avg_predictions:.1f}")
                
                # 推定データ充足率 (目標: 1銘柄あたり1000価格データ、100予測データ)
                price_fill_rate = min(100, (avg_prices / 1000) * 100) if avg_prices > 0 else 0
                prediction_fill_rate = min(100, (avg_predictions / 100) * 100) if avg_predictions > 0 else 0
                
                print(f"📊 価格データ充足率: {price_fill_rate:.1f}%")
                print(f"🔮 予測データ充足率: {prediction_fill_rate:.1f}%")
                print(f"🎯 総合充足率: {(price_fill_rate + prediction_fill_rate) / 2:.1f}%")
            
            print("=" * 60)
            
            # 上位銘柄のデータ数
            print("🏆 データ数上位銘柄:")
            result = conn.execute(text("""
                SELECT sm.symbol, sm.name, 
                       COUNT(sp.id) as price_count,
                       COUNT(spr.id) as prediction_count
                FROM stock_master sm 
                LEFT JOIN stock_prices sp ON sm.symbol = sp.symbol
                LEFT JOIN stock_predictions spr ON sm.symbol = spr.symbol
                GROUP BY sm.symbol, sm.name
                ORDER BY price_count DESC
                LIMIT 10
            """)).fetchall()
            
            for row in result:
                symbol, name, prices, predictions = row
                print(f"   {symbol}: {prices:,}価格, {predictions:,}予測 - {name}")
                
    except Exception as e:
        print(f"❌ エラー: {e}")
        return False
    
    return True

if __name__ == "__main__":
    check_database_stats()