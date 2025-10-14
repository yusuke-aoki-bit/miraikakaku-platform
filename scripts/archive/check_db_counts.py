#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
データベースの実際のレコード数を確認するスクリプト
"""
import psycopg2
from psycopg2.extras import RealDictCursor
import os
from dotenv import load_dotenv

load_dotenv()

def get_db_connection():
    host = os.getenv('POSTGRES_HOST', 'localhost')
    config = {
        'database': os.getenv('POSTGRES_DB', 'miraikakaku'),
        'user': os.getenv('POSTGRES_USER', 'postgres'),
        'password': os.getenv('POSTGRES_PASSWORD', 'Miraikakaku2024!')
    }
    if host.startswith('/cloudsql/'):
        config['host'] = host
    else:
        config['host'] = host
        config['port'] = int(os.getenv('POSTGRES_PORT', 5433))
    return psycopg2.connect(**config)

def check_database_counts():
    """データベースの実際のレコード数をチェック"""
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)

        print("=" * 70)
        print("DATABASE RECORD COUNTS")
        print("=" * 70)

        # 1. stock_master (銘柄マスター)
        cur.execute("""
            SELECT
                COUNT(*) as total_symbols,
                COUNT(CASE WHEN is_active = TRUE THEN 1 END) as active_symbols,
                COUNT(CASE WHEN symbol NOT LIKE '%.T' AND symbol NOT LIKE '%.KS' AND symbol NOT LIKE '%.HK' THEN 1 END) as us_symbols,
                COUNT(CASE WHEN symbol LIKE '%.T' THEN 1 END) as jp_symbols
            FROM stock_master
        """)
        stock_master = cur.fetchone()

        print("\n1. stock_master (銘柄マスター)")
        print(f"   総銘柄数: {stock_master['total_symbols']:,}")
        print(f"   アクティブ: {stock_master['active_symbols']:,}")
        print(f"   米国株: {stock_master['us_symbols']:,}")
        print(f"   日本株: {stock_master['jp_symbols']:,}")

        # 2. stock_prices (価格データ)
        cur.execute("""
            SELECT
                COUNT(*) as total_records,
                COUNT(DISTINCT symbol) as symbols_with_prices,
                MIN(date) as earliest_date,
                MAX(date) as latest_date
            FROM stock_prices
        """)
        stock_prices = cur.fetchone()

        print("\n2. stock_prices (価格データ)")
        print(f"   総レコード数: {stock_prices['total_records']:,}")
        print(f"   価格データあり銘柄数: {stock_prices['symbols_with_prices']:,}")
        print(f"   最古データ: {stock_prices['earliest_date']}")
        print(f"   最新データ: {stock_prices['latest_date']}")

        # 3. ensemble_predictions (予測データ)
        cur.execute("""
            SELECT
                COUNT(*) as total_predictions,
                COUNT(DISTINCT symbol) as symbols_with_predictions,
                COUNT(CASE WHEN prediction_date >= CURRENT_DATE THEN 1 END) as future_predictions,
                COUNT(DISTINCT CASE WHEN prediction_date >= CURRENT_DATE THEN symbol END) as symbols_with_future_predictions,
                MIN(prediction_date) as earliest_prediction,
                MAX(prediction_date) as latest_prediction
            FROM ensemble_predictions
        """)
        ensemble_predictions = cur.fetchone()

        print("\n3. ensemble_predictions (予測データ)")
        print(f"   総予測レコード数: {ensemble_predictions['total_predictions']:,}")
        print(f"   予測データあり銘柄数: {ensemble_predictions['symbols_with_predictions']:,}")
        print(f"   未来予測レコード数: {ensemble_predictions['future_predictions']:,}")
        print(f"   未来予測あり銘柄数: {ensemble_predictions['symbols_with_future_predictions']:,}")
        print(f"   最古予測日: {ensemble_predictions['earliest_prediction']}")
        print(f"   最新予測日: {ensemble_predictions['latest_prediction']}")

        # 4. stock_news (ニュースデータ)
        cur.execute("""
            SELECT
                COUNT(*) as total_news,
                COUNT(DISTINCT symbol) as symbols_with_news,
                MIN(published_at) as earliest_news,
                MAX(published_at) as latest_news
            FROM stock_news
        """)
        stock_news = cur.fetchone()

        print("\n4. stock_news (ニュースデータ)")
        print(f"   総ニュース数: {stock_news['total_news']:,}")
        print(f"   ニュースあり銘柄数: {stock_news['symbols_with_news']:,}")
        print(f"   最古ニュース: {stock_news['earliest_news']}")
        print(f"   最新ニュース: {stock_news['latest_news']}")

        # 5. カバレッジ分析
        print("\n5. カバレッジ分析")

        # 価格データカバレッジ
        price_coverage = (stock_prices['symbols_with_prices'] / stock_master['total_symbols'] * 100) if stock_master['total_symbols'] > 0 else 0
        print(f"   価格データカバレッジ: {price_coverage:.1f}% ({stock_prices['symbols_with_prices']}/{stock_master['total_symbols']})")

        # 予測データカバレッジ
        prediction_coverage = (ensemble_predictions['symbols_with_predictions'] / stock_master['total_symbols'] * 100) if stock_master['total_symbols'] > 0 else 0
        print(f"   予測データカバレッジ: {prediction_coverage:.1f}% ({ensemble_predictions['symbols_with_predictions']}/{stock_master['total_symbols']})")

        # 未来予測カバレッジ
        future_coverage = (ensemble_predictions['symbols_with_future_predictions'] / stock_master['total_symbols'] * 100) if stock_master['total_symbols'] > 0 else 0
        print(f"   未来予測カバレッジ: {future_coverage:.1f}% ({ensemble_predictions['symbols_with_future_predictions']}/{stock_master['total_symbols']})")

        # ニュースカバレッジ
        news_coverage = (stock_news['symbols_with_news'] / stock_master['total_symbols'] * 100) if stock_master['total_symbols'] > 0 else 0
        print(f"   ニュースカバレッジ: {news_coverage:.1f}% ({stock_news['symbols_with_news']}/{stock_master['total_symbols']})")

        print("\n" + "=" * 70)

        # 6. データ品質チェック
        print("\n6. データ品質チェック")

        # 価格データなし銘柄
        cur.execute("""
            SELECT COUNT(*) as count
            FROM stock_master sm
            LEFT JOIN stock_prices sp ON sm.symbol = sp.symbol
            WHERE sm.is_active = TRUE
              AND sp.symbol IS NULL
        """)
        no_price_data = cur.fetchone()['count']
        print(f"   価格データなしアクティブ銘柄: {no_price_data:,}")

        # 予測データなし銘柄
        cur.execute("""
            SELECT COUNT(*) as count
            FROM stock_master sm
            LEFT JOIN ensemble_predictions ep ON sm.symbol = ep.symbol AND ep.prediction_date >= CURRENT_DATE
            WHERE sm.is_active = TRUE
              AND ep.symbol IS NULL
        """)
        no_prediction_data = cur.fetchone()['count']
        print(f"   未来予測なしアクティブ銘柄: {no_prediction_data:,}")

        print("\n" + "=" * 70)

        cur.close()
        conn.close()

        return {
            "stock_master": dict(stock_master),
            "stock_prices": dict(stock_prices),
            "ensemble_predictions": dict(ensemble_predictions),
            "stock_news": dict(stock_news),
            "coverage": {
                "price_coverage": round(price_coverage, 2),
                "prediction_coverage": round(prediction_coverage, 2),
                "future_coverage": round(future_coverage, 2),
                "news_coverage": round(news_coverage, 2)
            },
            "quality": {
                "no_price_data": no_price_data,
                "no_prediction_data": no_prediction_data
            }
        }

    except Exception as e:
        print(f"エラー: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    check_database_counts()
