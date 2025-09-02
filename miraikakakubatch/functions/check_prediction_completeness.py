#!/usr/bin/env python3
"""
AI予測データの詳細分析スクリプト
"""

import pymysql
from datetime import datetime, timedelta

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
            print("=== AI予測データ詳細分析 ===\n")
            
            # 1. 予測テーブルの構造確認
            print("【1. stock_predictions テーブル構造】")
            cursor.execute("DESCRIBE stock_predictions")
            columns = cursor.fetchall()
            for column in columns:
                print(f"- {column[0]}: {column[1]}")
            
            print()
            
            # 2. 予測データの時系列分布
            print("【2. 予測データの時系列分布】")
            cursor.execute("""
                SELECT 
                    DATE(created_at) as prediction_date,
                    COUNT(*) as count,
                    COUNT(DISTINCT symbol) as unique_symbols
                FROM stock_predictions 
                GROUP BY DATE(created_at) 
                ORDER BY prediction_date DESC
                LIMIT 30
            """)
            daily_predictions = cursor.fetchall()
            
            if daily_predictions:
                print("過去30日の予測データ:")
                for date, count, symbols in daily_predictions:
                    print(f"{date}: {count}件 (対象銘柄: {symbols})")
            else:
                print("予測データが見つかりません")
            
            print()
            
            # 3. 予測対象銘柄の詳細
            print("【3. 予測対象銘柄】")
            cursor.execute("""
                SELECT DISTINCT sp.symbol, sm.name, sm.market
                FROM stock_predictions sp
                LEFT JOIN stock_master sm ON sp.symbol = sm.symbol
                ORDER BY sp.symbol
            """)
            prediction_stocks = cursor.fetchall()
            
            if prediction_stocks:
                print(f"予測対象銘柄数: {len(prediction_stocks)}")
                for symbol, name, market in prediction_stocks:
                    company_name = name or '不明'
                    market_name = market or '不明'
                    print(f"- {symbol}: {company_name} ({market_name})")
            
            print()
            
            # 4. 予測精度の評価（可能な場合）
            print("【4. 予測精度評価】")
            cursor.execute("""
                SELECT 
                    AVG(confidence_score) as avg_confidence,
                    MIN(confidence_score) as min_confidence,
                    MAX(confidence_score) as max_confidence
                FROM stock_predictions
                WHERE confidence_score IS NOT NULL
            """)
            confidence_stats = cursor.fetchone()
            
            if confidence_stats and confidence_stats[0] is not None:
                avg_conf, min_conf, max_conf = confidence_stats
                print(f"平均信頼度: {avg_conf:.3f}")
                print(f"最小信頼度: {min_conf:.3f}")
                print(f"最大信頼度: {max_conf:.3f}")
            else:
                print("信頼度データが不足しています")
            
            print()
            
            # 5. モデル性能テーブルの確認
            print("【5. モデル性能データ】")
            cursor.execute("SELECT COUNT(*) FROM model_performance")
            model_count = cursor.fetchone()[0]
            print(f"モデル性能記録数: {model_count}")
            
            if model_count > 0:
                cursor.execute("""
                    SELECT 
                        model_name,
                        accuracy,
                        mse,
                        mae,
                        created_at
                    FROM model_performance
                    ORDER BY created_at DESC
                    LIMIT 10
                """)
                models = cursor.fetchall()
                
                print("最新のモデル性能:")
                for model_name, accuracy, mse, mae, created_at in models:
                    print(f"- {model_name}: 精度={accuracy:.3f}, MSE={mse:.3f}, MAE={mae:.3f} ({created_at})")
            
            print()
            
            # 6. AI推論ログの確認
            print("【6. AI推論ログ】")
            cursor.execute("SELECT COUNT(*) FROM ai_inference_log")
            inference_count = cursor.fetchone()[0]
            print(f"AI推論ログ数: {inference_count}")
            
            if inference_count > 0:
                cursor.execute("""
                    SELECT 
                        DATE(timestamp) as log_date,
                        COUNT(*) as daily_inferences
                    FROM ai_inference_log
                    GROUP BY DATE(timestamp)
                    ORDER BY log_date DESC
                    LIMIT 10
                """)
                daily_inferences = cursor.fetchall()
                
                print("直近の推論実行状況:")
                for date, count in daily_inferences:
                    print(f"- {date}: {count}回")
            
            print()
            
            # 7. 予測カバレッジの分析
            print("【7. 予測カバレッジ分析】")
            
            # アクティブ銘柄数取得
            cursor.execute("SELECT COUNT(*) FROM stock_master WHERE is_active = 1")
            total_active = cursor.fetchone()[0]
            
            # 予測がある銘柄数
            cursor.execute("SELECT COUNT(DISTINCT symbol) FROM stock_predictions")
            predicted_symbols = cursor.fetchone()[0]
            
            coverage = (predicted_symbols / total_active * 100) if total_active > 0 else 0
            
            print(f"総アクティブ銘柄数: {total_active:,}")
            print(f"予測対象銘柄数: {predicted_symbols:,}")
            print(f"予測カバレッジ: {coverage:.1f}%")
            
            # マーケット別カバレッジ
            cursor.execute("""
                SELECT 
                    sm.market,
                    COUNT(*) as total_stocks,
                    COUNT(DISTINCT sp.symbol) as predicted_stocks
                FROM stock_master sm
                LEFT JOIN stock_predictions sp ON sm.symbol = sp.symbol
                WHERE sm.is_active = 1
                GROUP BY sm.market
                ORDER BY total_stocks DESC
            """)
            market_coverage = cursor.fetchall()
            
            print("\nマーケット別予測カバレッジ:")
            for market, total, predicted in market_coverage:
                market_name = market or '未設定'
                predicted = predicted or 0
                market_coverage_pct = (predicted / total * 100) if total > 0 else 0
                print(f"- {market_name}: {predicted}/{total} ({market_coverage_pct:.1f}%)")
            
            print()
            
            # 8. 改善提案
            print("【8. 改善提案】")
            
            if coverage < 10:
                print("🔴 予測カバレッジが非常に低いです（<10%）")
                print("  → 予測モデルの実行頻度を上げる必要があります")
            elif coverage < 50:
                print("🟠 予測カバレッジが低いです（<50%）")
                print("  → より多くの銘柄に対する予測生成が必要です")
            else:
                print("🟢 予測カバレッジは良好です")
            
            if model_count == 0:
                print("🔴 モデル性能データがありません")
                print("  → モデルの精度評価システムが必要です")
            
            if inference_count < 100:
                print("🟠 AI推論の実行回数が少ないです")
                print("  → 予測実行の自動化を強化する必要があります")
                
    except Exception as e:
        print(f"エラー: {e}")
        import traceback
        traceback.print_exc()
    finally:
        connection.close()

if __name__ == "__main__":
    main()