#!/usr/bin/env python3
"""
データ問題の診断スクリプト
1. 最新の株価データの日付を確認
2. 予測データのボラティリティを確認
"""

import psycopg2
from datetime import datetime, timedelta
import numpy as np

# データベース接続 (Cloud SQL)
conn = psycopg2.connect(
    host="34.72.126.164",  # Cloud SQL IP
    port=5432,
    database="miraikakaku",
    user="postgres",
    password="Miraikakaku2024!"
)
cur = conn.cursor()

print("=" * 80)
print("📊 データ状況診断レポート")
print("=" * 80)

# 1. 株価データの最新日付を確認
print("\n【1. 株価データの最新状況】")
cur.execute("""
    SELECT
        MAX(date) as latest_date,
        MIN(date) as oldest_date,
        COUNT(DISTINCT symbol) as total_symbols,
        COUNT(*) as total_records,
        CURRENT_DATE - MAX(date) as days_behind
    FROM stock_prices
    WHERE date >= CURRENT_DATE - INTERVAL '30 days'
""")
result = cur.fetchone()
print(f"最新日付: {result[0]}")
print(f"最古日付: {result[1]}")
print(f"銘柄数: {result[2]}")
print(f"レコード数: {result[3]}")
print(f"現在からの遅延: {result[4]}日")

if result[4] and result[4] > 0:
    print(f"⚠️  警告: データが{result[4]}日古いです！")

# 2. サンプル銘柄のデータを確認
print("\n【2. 主要銘柄の最新データ】")
cur.execute("""
    SELECT
        symbol,
        MAX(date) as latest_date,
        COUNT(*) as record_count
    FROM stock_prices
    WHERE symbol IN ('AAPL', 'TSLA', '7203.T', '9984.T')
    GROUP BY symbol
    ORDER BY symbol
""")
for row in cur.fetchall():
    print(f"{row[0]}: 最新={row[1]}, レコード数={row[2]}")

# 3. 予測データのボラティリティ分析
print("\n【3. 予測のボラティリティ分析】")

# サンプル銘柄の過去のボラティリティ
cur.execute("""
    WITH daily_returns AS (
        SELECT
            symbol,
            date,
            close_price,
            LAG(close_price) OVER (PARTITION BY symbol ORDER BY date) as prev_close,
            (close_price - LAG(close_price) OVER (PARTITION BY symbol ORDER BY date)) /
            LAG(close_price) OVER (PARTITION BY symbol ORDER BY date) * 100 as daily_return
        FROM stock_prices
        WHERE symbol IN ('AAPL', 'TSLA', '7203.T', '9984.T')
        AND date >= CURRENT_DATE - INTERVAL '90 days'
    )
    SELECT
        symbol,
        STDDEV(daily_return) as volatility_pct,
        AVG(ABS(daily_return)) as avg_abs_return_pct,
        MIN(daily_return) as min_return,
        MAX(daily_return) as max_return
    FROM daily_returns
    WHERE daily_return IS NOT NULL
    GROUP BY symbol
    ORDER BY symbol
""")

historical_volatility = {}
print("\n過去90日の実績ボラティリティ:")
for row in cur.fetchall():
    symbol, vol, avg_abs, min_ret, max_ret = row
    historical_volatility[symbol] = float(vol) if vol else 0
    print(f"{symbol}:")
    print(f"  標準偏差: {vol:.2f}%")
    print(f"  平均変動: {avg_abs:.2f}%")
    print(f"  最大下落: {min_ret:.2f}%")
    print(f"  最大上昇: {max_ret:.2f}%")

# 4. 予測データのボラティリティを確認
print("\n【4. 予測データのボラティリティ】")
cur.execute("""
    WITH prediction_changes AS (
        SELECT
            symbol,
            prediction_date,
            ensemble_prediction as pred_price,
            LAG(ensemble_prediction) OVER (PARTITION BY symbol ORDER BY prediction_date) as prev_pred,
            (ensemble_prediction - LAG(ensemble_prediction) OVER (PARTITION BY symbol ORDER BY prediction_date)) /
            LAG(ensemble_prediction) OVER (PARTITION BY symbol ORDER BY prediction_date) * 100 as pred_change
        FROM ensemble_predictions
        WHERE symbol IN ('AAPL', 'TSLA', '7203.T', '9984.T')
        AND prediction_date >= CURRENT_DATE
        AND prediction_date <= CURRENT_DATE + INTERVAL '30 days'
    )
    SELECT
        symbol,
        COUNT(*) as num_predictions,
        STDDEV(pred_change) as pred_volatility_pct,
        AVG(ABS(pred_change)) as avg_abs_change_pct,
        MIN(pred_change) as min_change,
        MAX(pred_change) as max_change
    FROM prediction_changes
    WHERE pred_change IS NOT NULL
    GROUP BY symbol
    ORDER BY symbol
""")

print("\n予測の変動率:")
for row in cur.fetchall():
    symbol, num, vol, avg_abs, min_ch, max_ch = row
    hist_vol = historical_volatility.get(symbol, 0)

    print(f"{symbol}:")
    print(f"  予測数: {num}")
    print(f"  予測の標準偏差: {vol:.2f}% (実績: {hist_vol:.2f}%)")

    ratio = (vol / hist_vol * 100) if hist_vol > 0 else 0
    print(f"  ボラティリティ比率: {ratio:.1f}%")

    if ratio < 30:
        print(f"  ⚠️  警告: 予測が実績に比べて{100-ratio:.0f}%も平坦です！")

    print(f"  平均変動: {avg_abs:.2f}%")
    print(f"  最大下落予測: {min_ch:.2f}%")
    print(f"  最大上昇予測: {max_ch:.2f}%")

# 5. 予測モデルの設定を確認
print("\n【5. 現在の予測生成スクリプトの設定】")
try:
    with open('generate_ensemble_predictions.py', 'r', encoding='utf-8') as f:
        content = f.read()

        # 重要な設定を抽出
        if 'sequence_length' in content:
            print("✓ シーケンス長の設定を確認")
        if 'volatility' in content.lower():
            print("✓ ボラティリティ考慮の設定を確認")
        if 'trend_weight' in content:
            print("✓ トレンド重み付けの設定を確認")

        # 問題の可能性がある設定
        if 'noise' not in content.lower():
            print("⚠️  ノイズ追加の設定が見つかりません")
        if 'std' not in content.lower() and 'volatility' not in content.lower():
            print("⚠️  標準偏差/ボラティリティの使用が見つかりません")

except FileNotFoundError:
    print("⚠️  generate_ensemble_predictions.py が見つかりません")

# 6. 推奨事項
print("\n" + "=" * 80)
print("【推奨事項】")
print("=" * 80)

if result[4] and result[4] > 0:
    print(f"\n1. データ更新: {result[4]}日分の最新データを取得する必要があります")
    print("   実行: python update_stock_prices.py")

print("\n2. 予測モデルの改善:")
print("   - 履歴ボラティリティを予測に反映")
print("   - トレンドに加えてノイズ成分を追加")
print("   - 信頼区間を持った予測範囲を生成")

print("\n3. 即座の対応:")
print("   - generate_ensemble_predictions.pyを修正")
print("   - ボラティリティ適応型の予測を実装")
print("   - 予測を再生成")

cur.close()
conn.close()

print("\n診断完了")
