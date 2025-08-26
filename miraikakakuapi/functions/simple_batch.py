#!/usr/bin/env python3
"""
シンプルなバッチ処理テスト - 少数の銘柄で動作確認
"""

import yfinance as yf
from datetime import datetime, timedelta
from sqlalchemy import text
from database.database import get_db
import numpy as np


def load_data_for_symbol(symbol):
    """1銘柄のデータをロード"""
    db = next(get_db())

    print(f"\n処理中: {symbol}")

    try:
        # Yahoo Financeから取得
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period="1mo")

        if hist.empty:
            print(f"  ❌ データ取得失敗")
            return False

        db_symbol = symbol.replace(".T", "").replace("^", "")
        saved_prices = 0

        # 価格データ保存
        for date, row in hist.iterrows():
            try:
                # 既存チェック
                result = db.execute(
                    text(
                        "SELECT COUNT(*) FROM stock_prices WHERE symbol = :sym AND date = :dt"
                    ),
                    {"sym": db_symbol, "dt": date.date()},
                )

                if result.scalar() == 0:
                    db.execute(
                        text(
                            """
                        INSERT INTO stock_prices
                        (symbol, date, open_price, high_price, low_price, close_price, volume, created_at)
                        VALUES (:sym, :dt, :op, :hi, :lo, :cl, :vol, NOW())
                    """
                        ),
                        {
                            "sym": db_symbol,
                            "dt": date.date(),
                            "op": float(row["Open"]),
                            "hi": float(row["High"]),
                            "lo": float(row["Low"]),
                            "cl": float(row["Close"]),
                            "vol": int(row["Volume"]),
                        },
                    )
                    saved_prices += 1
            except Exception as e:
                print(f"    Error: {e}")
                continue

        if saved_prices > 0:
            db.commit()
            print(f"  ✅ {saved_prices}件の価格データを保存")

        # 予測データ生成
        latest_price = float(hist["Close"].iloc[-1])
        saved_predictions = 0

        for days in range(1, 8):
            pred_date = datetime.now().date() + timedelta(days=days)

            # 既存チェック
            result = db.execute(
                text(
                    "SELECT COUNT(*) FROM stock_predictions WHERE symbol = :sym AND prediction_date = :dt"
                ),
                {"sym": db_symbol, "dt": pred_date},
            )

            if result.scalar() == 0:
                # 簡単な予測
                change = np.random.normal(0, 0.02)
                predicted = latest_price * (1 + change * days * 0.3)
                confidence = 0.9 - (days * 0.08)

                db.execute(
                    text(
                        """
                    INSERT INTO stock_predictions
                    (symbol, prediction_date, current_price, predicted_price,
                     confidence_score, prediction_days, model_version, created_at)
                    VALUES (:sym, :dt, :cur, :pred, :conf, :days, :model, NOW())
                """
                    ),
                    {
                        "sym": db_symbol,
                        "dt": pred_date,
                        "cur": latest_price,
                        "pred": round(predicted, 2),
                        "conf": round(confidence, 2),
                        "days": days,
                        "model": "SIMPLE_BATCH",
                    },
                )
                saved_predictions += 1

        if saved_predictions > 0:
            db.commit()
            print(f"  📊 {saved_predictions}件の予測データを生成")

        return True

    except Exception as e:
        print(f"  ❌ エラー: {e}")
        db.rollback()
        return False
    finally:
        db.close()


def main():
    """メイン処理"""
    print("=" * 50)
    print("シンプルバッチ処理開始")
    print("=" * 50)

    # テスト用銘柄（少数）
    test_symbols = [
        "^N225",  # 日経225
        "^DJI",  # ダウ
        "^GSPC",  # S&P500
        "AAPL",  # Apple
        "GOOGL",  # Google
        "MSFT",  # Microsoft
        "7203.T",  # トヨタ
        "9984.T",  # ソフトバンク
    ]

    success_count = 0

    for symbol in test_symbols:
        if load_data_for_symbol(symbol):
            success_count += 1

    print("\n" + "=" * 50)
    print(f"処理完了: {success_count}/{len(test_symbols)}銘柄成功")
    print("=" * 50)

    # データ確認
    db = next(get_db())

    # 価格データ件数
    result = db.execute(text("SELECT COUNT(*) FROM stock_prices"))
    price_count = result.scalar()

    # 予測データ件数
    result = db.execute(text("SELECT COUNT(*) FROM stock_predictions"))
    pred_count = result.scalar()

    print(f"\n現在のデータ件数:")
    print(f"  価格データ: {price_count}件")
    print(f"  予測データ: {pred_count}件")

    db.close()


if __name__ == "__main__":
    main()
