#!/usr/bin/env python3
"""
Database Analysis Script for Miraikakaku
Analyze current data coverage and identify expansion opportunities
"""

import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime, timedelta
import json

# Database configuration
DB_CONFIG = {
    'host': '34.173.9.214',
    'user': 'postgres',
    'password': 'os.getenv('DB_PASSWORD', '')',
    'database': 'miraikakaku'
}

def get_db_connection():
    """Get database connection"""
    return psycopg2.connect(**DB_CONFIG, cursor_factory=RealDictCursor)

def analyze_price_data_coverage():
    """Analyze price data coverage"""
    print("📊 Analyzing Price Data Coverage...")

    conn = get_db_connection()
    cur = conn.cursor()

    # Get overall statistics
    cur.execute("""
        SELECT
            COUNT(DISTINCT symbol) as total_symbols,
            COUNT(*) as total_records,
            MIN(date) as earliest_date,
            MAX(date) as latest_date,
            (MAX(date) - MIN(date)) as date_range_days
        FROM stock_prices;
    """)

    overall_stats = cur.fetchone()
    print(f"📈 Overall Statistics:")
    print(f"   Total Symbols: {overall_stats['total_symbols']}")
    print(f"   Total Records: {overall_stats['total_records']:,}")
    print(f"   Date Range: {overall_stats['earliest_date']} to {overall_stats['latest_date']}")
    print(f"   Coverage: {overall_stats['date_range_days']} days")
    print()

    # Get top symbols by data coverage
    cur.execute("""
        SELECT
            symbol,
            COUNT(*) as total_records,
            MIN(date) as earliest_date,
            MAX(date) as latest_date,
            (MAX(date) - MIN(date)) as date_range_days
        FROM stock_prices
        GROUP BY symbol
        ORDER BY total_records DESC
        LIMIT 10;
    """)

    top_symbols = cur.fetchall()
    print("🏆 Top 10 Symbols by Data Coverage:")
    for i, symbol in enumerate(top_symbols, 1):
        print(f"   {i:2d}. {symbol['symbol']:6s} - {symbol['total_records']:4d} records ({symbol['date_range_days']} days)")
    print()

    # Check data quality
    cur.execute("""
        SELECT
            COUNT(*) as records_with_nulls,
            COUNT(*) * 100.0 / (SELECT COUNT(*) FROM stock_prices) as null_percentage
        FROM stock_prices
        WHERE close_price IS NULL OR volume IS NULL;
    """)

    quality_stats = cur.fetchone()
    print(f"📉 Data Quality:")
    print(f"   Records with NULLs: {quality_stats['records_with_nulls']:,} ({quality_stats['null_percentage']:.2f}%)")
    print()

    conn.close()
    return overall_stats, top_symbols

def analyze_prediction_data():
    """Analyze prediction data"""
    print("🔮 Analyzing Prediction Data...")

    conn = get_db_connection()
    cur = conn.cursor()

    # Get prediction statistics
    cur.execute("""
        SELECT
            COUNT(DISTINCT symbol) as symbols_with_predictions,
            COUNT(*) as total_predictions,
            MIN(prediction_date) as earliest_prediction,
            MAX(prediction_date) as latest_prediction,
            COUNT(DISTINCT model_type) as model_count
        FROM stock_predictions;
    """)

    pred_stats = cur.fetchone()
    print(f"🤖 Prediction Statistics:")
    print(f"   Symbols with Predictions: {pred_stats['symbols_with_predictions']}")
    print(f"   Total Predictions: {pred_stats['total_predictions']:,}")
    print(f"   Date Range: {pred_stats['earliest_prediction']} to {pred_stats['latest_prediction']}")
    print(f"   Model Types: {pred_stats['model_count']}")
    print()

    # Get model breakdown
    cur.execute("""
        SELECT
            model_type,
            COUNT(*) as prediction_count,
            COUNT(DISTINCT symbol) as symbols_covered,
            AVG(confidence_score) as avg_confidence
        FROM stock_predictions
        GROUP BY model_type
        ORDER BY prediction_count DESC;
    """)

    models = cur.fetchall()
    print("🔧 Model Breakdown:")
    for model in models:
        print(f"   {model['model_type']:20s} - {model['prediction_count']:5d} predictions, {model['symbols_covered']:3d} symbols, {model['avg_confidence']:.3f} avg confidence")
    print()

    conn.close()
    return pred_stats, models

def identify_expansion_opportunities():
    """Identify opportunities for data expansion"""
    print("🎯 Identifying Expansion Opportunities...")

    conn = get_db_connection()
    cur = conn.cursor()

    # Find symbols with limited historical data
    cur.execute("""
        SELECT
            symbol,
            COUNT(*) as record_count,
            MIN(date) as earliest_date,
            MAX(date) as latest_date,
            (CURRENT_DATE - MIN(date)) as total_days_available,
            (MAX(date) - MIN(date)) as coverage_days
        FROM stock_prices
        GROUP BY symbol
        HAVING COUNT(*) < 100 OR (MAX(date) - MIN(date)) < 365
        ORDER BY record_count ASC
        LIMIT 20;
    """)

    limited_symbols = cur.fetchall()
    print("⚠️  Symbols with Limited Historical Data (< 100 records or < 1 year):")
    for symbol in limited_symbols:
        print(f"   {symbol['symbol']:6s} - {symbol['record_count']:3d} records, {symbol['coverage_days']:3d} days coverage")
    print()

    # Find symbols missing recent data
    cur.execute("""
        SELECT
            symbol,
            MAX(date) as latest_date,
            (CURRENT_DATE - MAX(date)) as days_since_last_update
        FROM stock_prices
        GROUP BY symbol
        HAVING MAX(date) < CURRENT_DATE - INTERVAL '7 days'
        ORDER BY MAX(date) DESC
        LIMIT 10;
    """)

    stale_symbols = cur.fetchall()
    print("📅 Symbols with Stale Data (> 7 days old):")
    for symbol in stale_symbols:
        print(f"   {symbol['symbol']:6s} - Last update: {symbol['latest_date']} ({symbol['days_since_last_update']} days ago)")
    print()

    conn.close()
    return limited_symbols, stale_symbols

def check_batch_system_health():
    """Check GCP batch job status and recent activity"""
    print("🚀 Checking Batch System Health...")

    # This would normally use GCP APIs, but we'll simulate based on database updates
    conn = get_db_connection()
    cur = conn.cursor()

    # Check recent data ingestion activity
    cur.execute("""
        SELECT
            DATE(created_at) as date,
            COUNT(*) as records_added
        FROM stock_prices
        WHERE created_at >= CURRENT_DATE - INTERVAL '7 days'
        GROUP BY DATE(created_at)
        ORDER BY date DESC;
    """)

    recent_activity = cur.fetchall()
    print("📈 Recent Data Ingestion Activity (Last 7 days):")
    if recent_activity:
        for activity in recent_activity:
            print(f"   {activity['date']}: {activity['records_added']:,} records added")
    else:
        print("   ⚠️  No recent data ingestion activity detected")
    print()

    # Check prediction generation activity
    cur.execute("""
        SELECT
            DATE(created_at) as date,
            COUNT(*) as predictions_generated
        FROM stock_predictions
        WHERE created_at >= CURRENT_DATE - INTERVAL '7 days'
        GROUP BY DATE(created_at)
        ORDER BY date DESC;
    """)

    pred_activity = cur.fetchall()
    print("🔮 Recent Prediction Generation (Last 7 days):")
    if pred_activity:
        for activity in pred_activity:
            print(f"   {activity['date']}: {activity['predictions_generated']:,} predictions generated")
    else:
        print("   ⚠️  No recent prediction generation activity detected")
    print()

    conn.close()
    return recent_activity, pred_activity

def main():
    """Main analysis function"""
    print("🔍 Miraikakaku Data Analysis Report")
    print("=" * 50)
    print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    try:
        # Analyze price data coverage
        overall_stats, top_symbols = analyze_price_data_coverage()

        # Analyze prediction data
        pred_stats, models = analyze_prediction_data()

        # Identify expansion opportunities
        limited_symbols, stale_symbols = identify_expansion_opportunities()

        # Check batch system health
        recent_activity, pred_activity = check_batch_system_health()

        print("💡 Recommendations:")
        print("   1. Expand historical data for symbols with < 1 year coverage")
        print("   2. Implement daily batch jobs for recent data updates")
        print("   3. Add more model types for prediction diversity")
        print("   4. Focus on top 20 symbols for comprehensive coverage")
        print("   5. Monitor and alert on stale data (> 3 days)")
        print()

        # Summary
        print("📋 Summary:")
        print(f"   • {overall_stats['total_symbols']} symbols tracked")
        print(f"   • {overall_stats['total_records']:,} price records")
        print(f"   • {pred_stats['total_predictions']:,} predictions generated")
        print(f"   • {len(limited_symbols)} symbols need historical expansion")
        print(f"   • {len(stale_symbols)} symbols have stale data")

    except Exception as e:
        print(f"❌ Error during analysis: {e}")

if __name__ == "__main__":
    main()