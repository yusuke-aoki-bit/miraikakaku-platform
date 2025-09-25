#!/usr/bin/env python3
"""
Frontend確認用データ充足状況チェック
"""

import psycopg2
from datetime import datetime, timedelta

def check_data_status():
    """データ充足状況を確認"""
    db_config = {
        'host': '34.173.9.214',
        'user': 'postgres',
        'password': 'os.getenv('DB_PASSWORD', '')',
        'database': 'miraikakaku'
    }

    try:
        conn = psycopg2.connect(**db_config)
        cursor = conn.cursor()

        print("🔍 Frontend確認用データ充足銘柄一覧")
        print("=" * 80)

        # データ充足状況を確認
        cursor.execute("""
            SELECT
                s.symbol,
                COUNT(DISTINCT s.date) as price_days,
                COUNT(DISTINCT sp.prediction_date) as prediction_count,
                MAX(sp.created_at) as latest_prediction,
                MIN(s.date) as earliest_price,
                MAX(s.date) as latest_price,
                AVG(s.close_price) as avg_price
            FROM stock_prices s
            LEFT JOIN stock_predictions sp ON s.symbol = sp.symbol
            WHERE s.date >= CURRENT_DATE - INTERVAL '30 days'
            AND s.close_price > 0
            GROUP BY s.symbol
            HAVING COUNT(DISTINCT s.date) >= 15
            ORDER BY COUNT(DISTINCT sp.prediction_date) DESC, COUNT(DISTINCT s.date) DESC
            LIMIT 15;
        """)

        results = cursor.fetchall()

        print(f"{'Symbol':<15} {'Price Days':<12} {'Predictions':<12} {'Avg Price':<12} {'Latest Data':<12}")
        print("-" * 80)

        frontend_symbols = []

        for row in results:
            symbol, price_days, pred_count, latest_pred, earliest, latest, avg_price = row
            latest_str = latest.strftime('%m-%d') if latest else 'N/A'

            print(f"{symbol:<15} {price_days:<12} {pred_count or 0:<12} ${avg_price or 0:<11.2f} {latest_str:<12}")

            # Frontend確認に適した銘柄の条件
            if price_days >= 20 and (pred_count or 0) >= 5:
                frontend_symbols.append(symbol)

        print("\n🎯 Frontend確認推奨銘柄:")
        print("-" * 40)

        for i, symbol in enumerate(frontend_symbols[:5], 1):
            print(f"{i}. {symbol}")
            print(f"   URL: http://localhost:3001/details/{symbol}")

        # 最新の予測データ状況
        print("\n📊 最新予測データ状況:")
        print("-" * 40)

        cursor.execute("""
            SELECT
                model_type,
                COUNT(*) as count,
                MAX(created_at) as latest
            FROM stock_predictions
            WHERE created_at >= CURRENT_DATE - INTERVAL '24 hours'
            GROUP BY model_type
            ORDER BY count DESC;
        """)

        pred_results = cursor.fetchall()

        for model, count, latest in pred_results:
            latest_str = latest.strftime('%m-%d %H:%M') if latest else 'N/A'
            print(f"{model:<40} {count:>6} predictions (最新: {latest_str})")

        cursor.close()
        conn.close()

        return frontend_symbols[:5]

    except Exception as e:
        print(f"❌ Error: {e}")
        return []

if __name__ == "__main__":
    symbols = check_data_status()