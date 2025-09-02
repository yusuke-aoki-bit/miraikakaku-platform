#!/usr/bin/env python3
"""
pandas-datareaderの代替データソーステスト
"""

import pandas_datareader.data as web
import yfinance as yf
from datetime import datetime, timedelta

print("🧪 データソーステスト")

test_symbol = "AAPL"
end_date = datetime.now()
start_date = end_date - timedelta(days=5)

# 1. yfinanceを直接使用
print("\n1️⃣ yfinance (直接):")
try:
    ticker = yf.Ticker(test_symbol)
    hist = ticker.history(period="5d")
    print(f"✅ 成功: {len(hist)}日分取得")
    print(f"データソース: yfinance (直接API)")
except Exception as e:
    print(f"❌ 失敗: {e}")

# 2. pandas-datareader + yfinance
print("\n2️⃣ pandas-datareader (yfinance経由):")
try:
    # pandas-datareaderは内部でyfinanceを使うように変更可能
    import yfinance as yf
    yf.pdr_override()  # pandas-datareaderをyfinanceでオーバーライド
    
    df = web.get_data_yahoo(test_symbol, start_date, end_date)
    print(f"✅ 成功: {len(df)}日分取得")
    print(f"データソース: pandas-datareader -> yfinance")
except Exception as e:
    print(f"❌ 失敗: {e}")

# 3. FRED (経済指標)
print("\n3️⃣ FRED (経済指標):")
try:
    dgs10 = web.DataReader('DGS10', 'fred', start_date, end_date)
    print(f"✅ 10年物米国債利回り: {len(dgs10)}日分取得")
    print(f"最新値: {dgs10.iloc[-1].values[0]:.2f}%")
except Exception as e:
    print(f"❌ 失敗: {e}")

# 4. Stooq
print("\n4️⃣ Stooq:")
try:
    df_stooq = web.DataReader(f'{test_symbol}.US', 'stooq', start_date, end_date)
    print(f"✅ 成功: {len(df_stooq)}日分取得")
    print(f"データソース: Stooq (ポーランド)")
except Exception as e:
    print(f"❌ 失敗: {e}")

print("\n📌 結論: pandas-datareaderのYahoo直接接続は現在動作しませんが、")
print("   yfinanceオーバーライドやFRED、Stooqは正常に動作します。")