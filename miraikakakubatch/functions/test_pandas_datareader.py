#!/usr/bin/env python3
"""
pandas-datareaderが実際に動作するかテスト
"""

import pandas_datareader.data as web
from datetime import datetime, timedelta

print("🧪 pandas-datareader テスト開始")

# テスト銘柄
test_symbol = "AAPL"
end_date = datetime.now()
start_date = end_date - timedelta(days=5)

try:
    # pandas-datareaderでYahoo Financeから取得
    print(f"\n📊 pandas-datareader.data.DataReader('{test_symbol}', 'yahoo')を実行中...")
    df = web.DataReader(test_symbol, 'yahoo', start_date, end_date)
    
    print(f"✅ データ取得成功: {len(df)}日分")
    print(f"カラム: {df.columns.tolist()}")
    print(f"\n最新データ:")
    print(df.tail(2))
    
    # Stooqからも試す
    print(f"\n📊 Stooq から取得を試行...")
    df_stooq = web.DataReader(f"{test_symbol}.US", 'stooq', start_date, end_date)
    print(f"✅ Stooq取得成功: {len(df_stooq)}日分")
    
except Exception as e:
    print(f"❌ エラー: {e}")
    print(f"エラータイプ: {type(e).__name__}")

print("\n📌 注: pandas-datareaderは内部でyfinanceを使用することがあります")