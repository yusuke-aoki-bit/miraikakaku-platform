#!/usr/bin/env python3
"""
クイック補填率チェッカー
データ生成進行中の補填率をリアルタイム監視
"""

import pymysql
import time
from datetime import datetime, timedelta

def check_current_fill_rates():
    """現在の補填率を確認"""
    db_config = {
        "host": "34.58.103.36",
        "user": "miraikakaku-user", 
        "password": "miraikakaku-secure-pass-2024",
        "database": "miraikakaku",
        "charset": "utf8mb4"
    }
    
    connection = pymysql.connect(**db_config)
    
    try:
        with connection.cursor() as cursor:
            print(f"⏰ 補填率チェック - {datetime.now().strftime('%H:%M:%S')}")
            print("=" * 50)
            
            # 銘柄数
            cursor.execute("SELECT COUNT(*) FROM stock_master WHERE is_active = 1")
            total_stocks = cursor.fetchone()[0]
            
            # 価格データ
            cursor.execute("SELECT COUNT(*) FROM stock_price_history")
            total_prices = cursor.fetchone()[0]
            
            cursor.execute("""
                SELECT COUNT(DISTINCT symbol) 
                FROM stock_price_history 
                WHERE date >= %s
            """, (datetime.now() - timedelta(days=30),))
            recent_price_stocks = cursor.fetchone()[0]
            
            # 予測データ
            cursor.execute("SELECT COUNT(*) FROM stock_predictions")
            total_predictions = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(DISTINCT symbol) FROM stock_predictions")
            prediction_stocks = cursor.fetchone()[0]
            
            cursor.execute("""
                SELECT COUNT(DISTINCT symbol) 
                FROM stock_predictions 
                WHERE created_at >= %s
            """, (datetime.now() - timedelta(days=1),))
            recent_prediction_stocks = cursor.fetchone()[0]
            
            # AI推論ログ
            cursor.execute("SELECT COUNT(*) FROM ai_inference_log")
            inference_logs = cursor.fetchone()[0]
            
            # 結果表示
            price_fill_rate = (recent_price_stocks / total_stocks * 100) if total_stocks > 0 else 0
            prediction_fill_rate = (prediction_stocks / total_stocks * 100) if total_stocks > 0 else 0
            
            print(f"📊 総アクティブ銘柄数: {total_stocks:,}")
            print(f"📈 価格データ総件数: {total_prices:,}")
            print(f"📈 過去30日価格補填: {recent_price_stocks:,}銘柄 ({price_fill_rate:.1f}%)")
            print(f"🔮 予測データ総件数: {total_predictions:,}")
            print(f"🔮 予測対象銘柄数: {prediction_stocks:,}銘柄 ({prediction_fill_rate:.1f}%)")
            print(f"🔮 過去24時間予測: {recent_prediction_stocks:,}銘柄")
            print(f"🤖 AI推論ログ件数: {inference_logs:,}")
            
            # 改善度計算
            if prediction_fill_rate >= 50:
                status = "🟢 優秀"
            elif prediction_fill_rate >= 20:
                status = "🟡 良好" 
            elif prediction_fill_rate >= 5:
                status = "🟠 改善中"
            else:
                status = "🔴 要改善"
                
            print(f"📊 予測補填ステータス: {status}")
            print("=" * 50)
            
            return {
                'prediction_fill_rate': prediction_fill_rate,
                'price_fill_rate': price_fill_rate,
                'total_predictions': total_predictions,
                'prediction_stocks': prediction_stocks
            }
            
    except Exception as e:
        print(f"❌ エラー: {e}")
        return None
    finally:
        connection.close()

def main():
    """継続的な補填率モニタリング"""
    print("🚀 補填率リアルタイム監視開始")
    
    start_time = datetime.now()
    check_interval = 60  # 60秒間隔
    max_duration = 1800  # 30分間
    
    initial_stats = check_current_fill_rates()
    
    while (datetime.now() - start_time).seconds < max_duration:
        time.sleep(check_interval)
        
        current_stats = check_current_fill_rates()
        
        if initial_stats and current_stats:
            # 改善度を表示
            pred_improvement = current_stats['prediction_fill_rate'] - initial_stats['prediction_fill_rate']
            pred_count_increase = current_stats['total_predictions'] - initial_stats['total_predictions']
            
            if pred_improvement > 0 or pred_count_increase > 0:
                print(f"📈 改善検出:")
                print(f"   予測補填率: +{pred_improvement:.1f}%")
                print(f"   予測データ: +{pred_count_increase:,}件")
                print()

if __name__ == "__main__":
    main()