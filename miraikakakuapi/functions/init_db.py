#!/usr/bin/env python3
"""
データベース初期化スクリプト
"""
import asyncio
import sys
import os

# パスを追加してモジュールをインポート可能にする
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database.database import engine, SessionLocal, init_database
from database.models import Base, StockMaster, StockPriceHistory, StockPredictions
from datetime import datetime, timedelta
import random

def create_sample_data():
    """サンプルデータを作成"""
    db = SessionLocal()
    try:
        # 既存のデータをクリア（オプション）
        print("Creating sample data...")
        
        # サンプル株式マスターデータ
        sample_stocks = [
            {
                "symbol": "AAPL",
                "company_name": "Apple Inc.",
                "exchange": "NASDAQ",
                "sector": "Technology",
                "industry": "Consumer Electronics",
                "market_cap": 3000000000000,
                "currency": "USD",
                "country": "US",
                "pe_ratio": 28.5,
                "dividend_yield": 0.0052,
                "beta": 1.2
            },
            {
                "symbol": "MSFT",
                "company_name": "Microsoft Corporation",
                "exchange": "NASDAQ",
                "sector": "Technology", 
                "industry": "Software",
                "market_cap": 2800000000000,
                "currency": "USD",
                "country": "US",
                "pe_ratio": 30.1,
                "dividend_yield": 0.0072,
                "beta": 0.9
            },
            {
                "symbol": "GOOGL",
                "company_name": "Alphabet Inc.",
                "exchange": "NASDAQ",
                "sector": "Technology",
                "industry": "Internet Services",
                "market_cap": 2000000000000,
                "currency": "USD",
                "country": "US",
                "pe_ratio": 25.3,
                "dividend_yield": 0.0000,
                "beta": 1.1
            },
            {
                "symbol": "TSLA",
                "company_name": "Tesla, Inc.",
                "exchange": "NASDAQ",
                "sector": "Automotive",
                "industry": "Electric Vehicles",
                "market_cap": 800000000000,
                "currency": "USD",
                "country": "US",
                "pe_ratio": 45.6,
                "dividend_yield": 0.0000,
                "beta": 2.1
            },
            {
                "symbol": "NVDA",
                "company_name": "NVIDIA Corporation",
                "exchange": "NASDAQ",
                "sector": "Technology",
                "industry": "Semiconductors",
                "market_cap": 1800000000000,
                "currency": "USD",
                "country": "US",
                "pe_ratio": 65.2,
                "dividend_yield": 0.0015,
                "beta": 1.7
            }
        ]
        
        # 株式マスターデータを挿入
        for stock_data in sample_stocks:
            existing_stock = db.query(StockMaster).filter(StockMaster.symbol == stock_data["symbol"]).first()
            if not existing_stock:
                stock = StockMaster(**stock_data)
                db.add(stock)
                print(f"Added stock: {stock_data['symbol']} - {stock_data['company_name']}")
        
        db.commit()
        
        # 各株式に対して過去30日の価格履歴を生成
        for stock_data in sample_stocks:
            symbol = stock_data["symbol"]
            base_price = random.uniform(100, 300)  # ベース価格
            
            for i in range(30):
                date = datetime.now() - timedelta(days=29-i)
                # 価格変動をシミュレート
                daily_change = random.uniform(-0.05, 0.05)
                base_price *= (1 + daily_change)
                
                high_price = base_price * (1 + random.uniform(0, 0.03))
                low_price = base_price * (1 - random.uniform(0, 0.03))
                open_price = base_price * (1 + random.uniform(-0.02, 0.02))
                
                volume = random.randint(1000000, 10000000)
                
                price_data = StockPriceHistory(
                    symbol=symbol,
                    date=date,
                    open_price=round(open_price, 2),
                    high_price=round(high_price, 2),
                    low_price=round(low_price, 2),
                    close_price=round(base_price, 2),
                    adjusted_close=round(base_price, 2),
                    volume=volume,
                    data_source="sample"
                )
                db.add(price_data)
            
            print(f"Added 30 days of price history for {symbol}")
        
        db.commit()
        
        # 予測データを生成
        for stock_data in sample_stocks:
            symbol = stock_data["symbol"]
            
            # 過去の最新価格を取得
            latest_price = db.query(StockPriceHistory).filter(
                StockPriceHistory.symbol == symbol
            ).order_by(StockPriceHistory.date.desc()).first()
            
            if latest_price:
                base_price = float(latest_price.close_price)
                
                # 次の7日間の予測を生成
                for i in range(1, 8):
                    prediction_date = datetime.now() + timedelta(days=i)
                    
                    # 予測価格（トレンドベース）
                    trend = random.uniform(-0.02, 0.02)
                    predicted_price = base_price * (1 + trend * i)
                    
                    confidence = random.uniform(0.6, 0.9)
                    
                    prediction = StockPredictions(
                        symbol=symbol,
                        prediction_date=datetime.now(),
                        target_date=prediction_date,
                        predicted_price=round(predicted_price, 2),
                        confidence_score=round(confidence, 4),
                        prediction_type="daily",
                        model_name="sample_model_v1.0",
                        model_version="1.0.0"
                    )
                    db.add(prediction)
                
                print(f"Added 7 days of predictions for {symbol}")
        
        db.commit()
        print("Sample data created successfully!")
        
    except Exception as e:
        print(f"Error creating sample data: {e}")
        db.rollback()
    finally:
        db.close()

async def main():
    """メイン実行関数"""
    print("Initializing database...")
    
    try:
        # データベースを初期化
        await init_database()
        print("Database tables created successfully!")
        
        # サンプルデータを作成
        create_sample_data()
        
        print("Database initialization completed!")
        
    except Exception as e:
        print(f"Error initializing database: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)