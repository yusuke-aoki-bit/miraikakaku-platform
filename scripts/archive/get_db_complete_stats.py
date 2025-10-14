#!/usr/bin/env python3
"""データベースの完全な統計情報を取得"""
import requests
import json

API_BASE = "https://miraikakaku-api-zbaru5v7za-uc.a.run.app"

print("=" * 80)
print("MIRAIKAKAKU DATABASE COMPLETE STATISTICS")
print("=" * 80)

# 1. シンボル統計
print("\n1. SYMBOLS (シンボル統計)")
print("-" * 80)
try:
    resp = requests.get(f"{API_BASE}/admin/stock-statistics", timeout=10)
    data = resp.json()
    stats = data['statistics']
    print(f"   総銘柄数:        {stats['total_stocks']:,}")
    print(f"   米国株:          {stats['us_stocks']:,}")
    print(f"   日本株:          {stats['jp_stocks']:,}")
    print(f"   韓国株:          {stats['kr_stocks']:,}")
    print(f"   アクティブ:      {stats['active_stocks']:,}")
    print(f"   非アクティブ:    {stats['inactive_stocks']:,}")
except Exception as e:
    print(f"   ERROR: {e}")

# 2. 予測データ統計
print("\n2. PREDICTIONS (予測データ統計)")
print("-" * 80)
try:
    resp = requests.get(f"{API_BASE}/api/predictions/summary", timeout=10)
    data = resp.json()
    print(f"   総予測レコード数:    {data['totalPredictions']:,}")
    print(f"   未来予測あり銘柄数:  {data['activePredictions']:,}")
    print(f"   平均信頼度:          {data['avgConfidence']:.1%}")
    print(f"   平均精度:            {data['avgAccuracy']:.1f}%")
    print(f"   予測カバレッジ:      {data['predictionCoverage']:.1f}%")
    print(f"   LSTMカバレッジ:      {data['lstmCoverage']:.2f}%")
    print(f"   ARIMAカバレッジ:     {data['arimaCoverage']:.2f}%")
    print(f"   MAカバレッジ:        {data['maCoverage']:.2f}%")
except Exception as e:
    print(f"   ERROR: {e}")

# 3. ニュースデータ統計
print("\n3. NEWS (ニュースデータ統計)")
print("-" * 80)
try:
    resp = requests.get(f"{API_BASE}/admin/stock-statistics", timeout=10)
    data = resp.json()
    news_stocks = data['stocks_with_news']
    total_news = sum(stock['news_count'] for stock in news_stocks)
    symbols_with_news = len(news_stocks)
    avg_sentiment = sum(stock['avg_sentiment'] for stock in news_stocks) / len(news_stocks) if news_stocks else 0

    print(f"   総ニュース数:        {total_news:,}")
    print(f"   ニュースあり銘柄数:  {symbols_with_news:,}")
    print(f"   平均センチメント:    {avg_sentiment:+.2%}")

    print(f"\n   Top 10 ニュース保有銘柄:")
    for i, stock in enumerate(news_stocks[:10], 1):
        print(f"      {i:2d}. {stock['symbol']:12s} {stock['news_count']:4d}記事  {stock['avg_sentiment']:+.2%}")
except Exception as e:
    print(f"   ERROR: {e}")

# 4. カバレッジ分析
print("\n4. COVERAGE ANALYSIS (カバレッジ分析)")
print("-" * 80)
try:
    resp1 = requests.get(f"{API_BASE}/admin/stock-statistics", timeout=10)
    total_symbols = resp1.json()['statistics']['total_stocks']

    resp2 = requests.get(f"{API_BASE}/api/predictions/summary", timeout=10)
    active_predictions = resp2.json()['activePredictions']

    resp3 = requests.get(f"{API_BASE}/admin/stock-statistics", timeout=10)
    symbols_with_news = len(resp3.json()['stocks_with_news'])

    pred_coverage = (active_predictions / total_symbols * 100) if total_symbols > 0 else 0
    news_coverage = (symbols_with_news / total_symbols * 100) if total_symbols > 0 else 0

    print(f"   予測データカバレッジ: {pred_coverage:.2f}% ({active_predictions:,}/{total_symbols:,})")
    print(f"   ニュースカバレッジ:   {news_coverage:.2f}% ({symbols_with_news:,}/{total_symbols:,})")

    # 未カバー銘柄数
    no_prediction = total_symbols - active_predictions
    no_news = total_symbols - symbols_with_news
    print(f"\n   未カバー銘柄:")
    print(f"      予測データなし:  {no_prediction:,} 銘柄")
    print(f"      ニュースなし:    {no_news:,} 銘柄")

except Exception as e:
    print(f"   ERROR: {e}")

print("\n" + "=" * 80)
print("REPORT COMPLETE")
print("=" * 80)
