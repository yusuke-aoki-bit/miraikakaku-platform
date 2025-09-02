#!/usr/bin/env python3
"""
データベースの補填率確認スクリプト
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
            print("=== データベース補填率レポート ===\n")
            
            # 1. 銘柄マスタの補填率
            print("【1. 銘柄マスタ (stock_master)】")
            cursor.execute("SELECT COUNT(*) FROM stock_master WHERE is_active = 1")
            active_stocks = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM stock_master")
            total_stocks = cursor.fetchone()[0]
            
            print(f"総銘柄数: {total_stocks:,}")
            print(f"アクティブ銘柄数: {active_stocks:,}")
            print(f"アクティブ率: {(active_stocks/total_stocks*100):.1f}%")
            
            # 詳細項目の補填率
            detail_fields = [
                ('sector', 'セクター'),
                ('industry', '業界'),
                ('website', 'ウェブサイト'),
                ('description', '説明')
            ]
            
            for field, name in detail_fields:
                cursor.execute(f"SELECT COUNT(*) FROM stock_master WHERE {field} IS NOT NULL AND {field} != ''")
                filled = cursor.fetchone()[0]
                print(f"{name}補填率: {(filled/total_stocks*100):.1f}% ({filled:,}/{total_stocks:,})")
            
            print()
            
            # 2. 価格履歴の補填率
            print("【2. 価格履歴 (stock_price_history)】")
            cursor.execute("SELECT COUNT(*) FROM stock_price_history")
            total_prices = cursor.fetchone()[0]
            print(f"総価格データ数: {total_prices:,}")
            
            # 最新30日間のデータがある銘柄数
            thirty_days_ago = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
            cursor.execute(f"""
                SELECT COUNT(DISTINCT symbol) 
                FROM stock_price_history 
                WHERE date >= '{thirty_days_ago}'
            """)
            recent_symbols = cursor.fetchone()[0]
            print(f"過去30日にデータがある銘柄数: {recent_symbols:,}")
            print(f"最新データ補填率: {(recent_symbols/active_stocks*100):.1f}%")
            
            # データ品質の確認
            cursor.execute("SELECT COUNT(*) FROM stock_price_history WHERE is_valid = 1")
            valid_data = cursor.fetchone()[0]
            print(f"有効データ率: {(valid_data/total_prices*100):.1f}%")
            
            cursor.execute("SELECT AVG(data_quality_score) FROM stock_price_history WHERE data_quality_score IS NOT NULL")
            avg_quality = cursor.fetchone()[0] or 0
            print(f"平均データ品質スコア: {avg_quality:.2f}")
            
            print()
            
            # 3. AI予測データの補填率
            print("【3. AI予測データ (stock_predictions)】")
            cursor.execute("SELECT COUNT(*) FROM stock_predictions")
            total_predictions = cursor.fetchone()[0]
            print(f"総予測データ数: {total_predictions:,}")
            
            # 最新予測がある銘柄数
            cursor.execute(f"""
                SELECT COUNT(DISTINCT symbol) 
                FROM stock_predictions 
                WHERE created_at >= '{thirty_days_ago}'
            """)
            recent_predictions = cursor.fetchone()[0]
            print(f"過去30日に予測がある銘柄数: {recent_predictions:,}")
            print(f"予測データ補填率: {(recent_predictions/active_stocks*100):.1f}%")
            
            print()
            
            # 4. マーケット・取引所別の分布
            print("【4. マーケット分布】")
            cursor.execute("""
                SELECT market, COUNT(*) as count 
                FROM stock_master 
                WHERE is_active = 1 
                GROUP BY market 
                ORDER BY count DESC 
                LIMIT 10
            """)
            markets = cursor.fetchall()
            for market, count in markets:
                market_name = market or '未設定'
                percentage = (count/active_stocks*100)
                print(f"{market_name}: {count:,}銘柄 ({percentage:.1f}%)")
            
            print()
            
            # 5. セクター分布
            print("【5. セクター分布 (上位10位)】")
            cursor.execute("""
                SELECT sector, COUNT(*) as count 
                FROM stock_master 
                WHERE is_active = 1 AND sector IS NOT NULL AND sector != ''
                GROUP BY sector 
                ORDER BY count DESC 
                LIMIT 10
            """)
            sectors = cursor.fetchall()
            for sector, count in sectors:
                percentage = (count/active_stocks*100)
                print(f"{sector}: {count:,}銘柄 ({percentage:.1f}%)")
            
            print()
            
            # 6. データの最新性確認
            print("【6. データの最新性】")
            cursor.execute("""
                SELECT MAX(date) as latest_date 
                FROM stock_price_history
            """)
            latest_date = cursor.fetchone()[0]
            if latest_date:
                if isinstance(latest_date, datetime):
                    latest_date = latest_date.date()
                days_old = (datetime.now().date() - latest_date).days
                print(f"最新価格データ日付: {latest_date}")
                print(f"最新データの経過日数: {days_old}日")
                
                if days_old <= 1:
                    freshness = "🟢 最新"
                elif days_old <= 7:
                    freshness = "🟡 やや古い"
                else:
                    freshness = "🔴 古い"
                print(f"データの鮮度: {freshness}")
            
            print()
            
            # 7. 総合評価
            print("【7. 総合評価】")
            
            # 補填率の重み付き平均を計算
            master_score = (active_stocks/total_stocks) * 100
            price_score = (recent_symbols/active_stocks) * 100 if active_stocks > 0 else 0
            prediction_score = (recent_predictions/active_stocks) * 100 if active_stocks > 0 else 0
            quality_score = (valid_data/total_prices) * 100 if total_prices > 0 else 0
            
            overall_score = (master_score * 0.2 + price_score * 0.4 + prediction_score * 0.3 + quality_score * 0.1)
            
            print(f"マスタデータ品質: {master_score:.1f}%")
            print(f"価格データ補填: {price_score:.1f}%")
            print(f"予測データ補填: {prediction_score:.1f}%")
            print(f"データ品質: {quality_score:.1f}%")
            print(f"総合補填スコア: {overall_score:.1f}%")
            
            if overall_score >= 80:
                grade = "🟢 優秀"
            elif overall_score >= 60:
                grade = "🟡 良好"
            elif overall_score >= 40:
                grade = "🟠 改善要"
            else:
                grade = "🔴 要改善"
            
            print(f"総合評価: {grade}")
            
    except Exception as e:
        print(f"エラー: {e}")
    finally:
        connection.close()

if __name__ == "__main__":
    main()