#!/usr/bin/env python3
"""
AI予測データの完全分析スクリプト（修正版）
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
            print("=== AI予測データ完全分析 ===\n")
            
            # 予測対象銘柄の詳細
            print("【予測対象銘柄】")
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
            
            # 予測精度評価
            print("【予測精度評価】")
            cursor.execute("""
                SELECT 
                    AVG(confidence_score) as avg_confidence,
                    MIN(confidence_score) as min_confidence,
                    MAX(confidence_score) as max_confidence,
                    COUNT(*) as total_predictions
                FROM stock_predictions
                WHERE confidence_score IS NOT NULL
            """)
            confidence_stats = cursor.fetchone()
            
            if confidence_stats and confidence_stats[0] is not None:
                avg_conf, min_conf, max_conf, total = confidence_stats
                print(f"総予測数: {total:,}")
                print(f"平均信頼度: {avg_conf:.3f}")
                print(f"最小信頼度: {min_conf:.3f}")
                print(f"最大信頼度: {max_conf:.3f}")
            else:
                print("信頼度データが不足しています")
            
            print()
            
            # モデル性能データ（修正版）
            print("【モデル性能データ】")
            cursor.execute("SELECT COUNT(*) FROM model_performance")
            model_count = cursor.fetchone()[0]
            print(f"モデル性能記録数: {model_count}")
            
            if model_count > 0:
                cursor.execute("""
                    SELECT 
                        model_type,
                        model_version,
                        accuracy,
                        mse,
                        mae,
                        created_at
                    FROM model_performance
                    ORDER BY created_at DESC
                    LIMIT 5
                """)
                models = cursor.fetchall()
                
                print("最新のモデル性能:")
                for model_type, model_version, accuracy, mse, mae, created_at in models:
                    print(f"- {model_type} v{model_version}: 精度={accuracy:.3f}, MSE={mse:.3f}, MAE={mae:.3f} ({created_at})")
            
            print()
            
            # AI推論ログの確認
            print("【AI推論ログ】")
            cursor.execute("SELECT COUNT(*) FROM ai_inference_log")
            inference_count = cursor.fetchone()[0]
            print(f"AI推論ログ数: {inference_count:,}")
            
            if inference_count > 0:
                cursor.execute("""
                    SELECT 
                        DATE(created_at) as log_date,
                        COUNT(*) as daily_inferences,
                        AVG(inference_time_ms) as avg_inference_time,
                        AVG(confidence_score) as avg_confidence
                    FROM ai_inference_log
                    WHERE created_at >= DATE_SUB(NOW(), INTERVAL 30 DAY)
                    GROUP BY DATE(created_at)
                    ORDER BY log_date DESC
                    LIMIT 10
                """)
                daily_inferences = cursor.fetchall()
                
                print("直近の推論実行状況:")
                for date, count, avg_time, avg_conf in daily_inferences:
                    avg_time = avg_time or 0
                    avg_conf = avg_conf or 0
                    print(f"- {date}: {count}回, 平均時間:{avg_time:.0f}ms, 平均信頼度:{avg_conf:.3f}")
            
            print()
            
            # 予測カバレッジの分析
            print("【予測カバレッジ分析】")
            
            cursor.execute("SELECT COUNT(*) FROM stock_master WHERE is_active = 1")
            total_active = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(DISTINCT symbol) FROM stock_predictions")
            predicted_symbols = cursor.fetchone()[0]
            
            coverage = (predicted_symbols / total_active * 100) if total_active > 0 else 0
            
            print(f"総アクティブ銘柄数: {total_active:,}")
            print(f"予測対象銘柄数: {predicted_symbols:,}")
            print(f"予測カバレッジ: {coverage:.1f}%")
            
            print()
            
            # 予測モデル別統計
            print("【モデル別予測統計】")
            cursor.execute("""
                SELECT 
                    model_type,
                    COUNT(*) as prediction_count,
                    AVG(confidence_score) as avg_confidence,
                    COUNT(DISTINCT symbol) as unique_symbols
                FROM stock_predictions
                WHERE model_type IS NOT NULL
                GROUP BY model_type
                ORDER BY prediction_count DESC
            """)
            model_stats = cursor.fetchall()
            
            if model_stats:
                for model_type, count, avg_conf, symbols in model_stats:
                    avg_conf = avg_conf or 0
                    print(f"- {model_type}: {count}予測, 平均信頼度:{avg_conf:.3f}, 対象銘柄:{symbols}")
            else:
                print("モデル種別データなし")
            
            print()
                
    except Exception as e:
        print(f"エラー: {e}")
        import traceback
        traceback.print_exc()
    finally:
        connection.close()

if __name__ == "__main__":
    main()