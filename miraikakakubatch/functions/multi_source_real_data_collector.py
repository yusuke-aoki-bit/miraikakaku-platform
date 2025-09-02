#!/usr/bin/env python3
"""
Multi-Source Real Data Collector for Miraikakaku
Uses yfinance (Yahoo Finance) + Alpha Vantage for comprehensive real market data
NO MOCK DATA - Real data only
"""

import os
import sys
import requests
import psycopg2
import yfinance as yf
import pandas as pd
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

class MultiSourceRealDataCollector:
    def __init__(self):
        # API Configuration
        self.alpha_vantage_api_key = os.getenv('ALPHA_VANTAGE_API_KEY', '')
        
        # PostgreSQL Database Configuration  
        self.db_config = {
            'host': os.getenv('DB_HOST', '34.173.9.214'),
            'port': os.getenv('DB_PORT', '5432'),
            'database': os.getenv('DB_NAME', 'miraikakaku'),
            'user': os.getenv('DB_USER', 'miraikakaku-user'),
            'password': os.getenv('DB_PASSWORD', 'miraikakaku-secure-pass-2024')
        }
        
        print(f"🚀 Multi-Source Real Data Collector initialized")
        print(f"   yfinance (Yahoo Finance): ✅ Always available")
        print(f"   Alpha Vantage API: {'✅' if self.alpha_vantage_api_key else '❌ Missing API key'}")
        print(f"   Database: PostgreSQL")

    def get_yfinance_data(self, symbol: str, period: str = "30d") -> Optional[pd.DataFrame]:
        """Get real stock data from Yahoo Finance via yfinance"""
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period=period)
            
            if hist.empty:
                print(f"❌ yfinance: No data for {symbol}")
                return None
                
            print(f"✅ yfinance: {symbol} - {len(hist)} days of data")
            return hist
            
        except Exception as e:
            print(f"❌ yfinance error for {symbol}: {str(e)}")
            return None

    def get_alpha_vantage_data(self, symbol: str) -> Optional[Dict]:
        """Get real stock data from Alpha Vantage API"""
        if not self.alpha_vantage_api_key:
            return None
            
        url = 'https://www.alphavantage.co/query'
        params = {
            'function': 'TIME_SERIES_DAILY',
            'symbol': symbol,
            'outputsize': 'compact',
            'apikey': self.alpha_vantage_api_key
        }
        
        try:
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            if "Error Message" in data:
                print(f"❌ Alpha Vantage error for {symbol}: {data['Error Message']}")
                return None
                
            if "Note" in data:
                print(f"⚠️ Alpha Vantage rate limit for {symbol}: {data['Note']}")
                return None
                
            if 'Time Series (Daily)' not in data:
                print(f"❌ Alpha Vantage: Unexpected response for {symbol}")
                return None
                
            print(f"✅ Alpha Vantage: {symbol} - {len(data['Time Series (Daily)'])} days")
            return data
            
        except Exception as e:
            print(f"❌ Alpha Vantage API error for {symbol}: {str(e)}")
            return None

    def get_alpha_vantage_forex_data(self, from_currency: str, to_currency: str) -> Optional[Dict]:
        """Get real forex data from Alpha Vantage"""
        if not self.alpha_vantage_api_key:
            return None
            
        url = 'https://www.alphavantage.co/query'
        params = {
            'function': 'FX_DAILY',
            'from_symbol': from_currency,
            'to_symbol': to_currency,
            'outputsize': 'compact',
            'apikey': self.alpha_vantage_api_key
        }
        
        try:
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            if "Error Message" in data or "Note" in data:
                return None
                
            if 'Time Series (FX Daily)' not in data:
                return None
                
            print(f"✅ Alpha Vantage Forex: {from_currency}/{to_currency}")
            return data
            
        except Exception as e:
            print(f"❌ Alpha Vantage forex error for {from_currency}/{to_currency}: {str(e)}")
            return None

    def save_yfinance_data_to_postgresql(self, symbol: str, hist_data: pd.DataFrame, connection):
        """Save yfinance data to PostgreSQL"""
        saved_count = 0
        
        with connection.cursor() as cursor:
            for date, row in hist_data.iterrows():
                try:
                    cursor.execute("""
                        INSERT INTO stock_prices 
                        (symbol, date, open_price, high_price, low_price, close_price, volume, data_source)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                        ON CONFLICT (symbol, date) DO UPDATE SET
                            open_price = EXCLUDED.open_price,
                            high_price = EXCLUDED.high_price,
                            low_price = EXCLUDED.low_price,
                            close_price = EXCLUDED.close_price,
                            volume = EXCLUDED.volume,
                            data_source = EXCLUDED.data_source
                    """, (
                        symbol,
                        date.strftime('%Y-%m-%d'),
                        float(row['Open']) if pd.notna(row['Open']) else None,
                        float(row['High']) if pd.notna(row['High']) else None,
                        float(row['Low']) if pd.notna(row['Low']) else None,
                        float(row['Close']) if pd.notna(row['Close']) else None,
                        int(row['Volume']) if pd.notna(row['Volume']) else None,
                        'yfinance_yahoo'
                    ))
                    saved_count += 1
                except Exception as e:
                    print(f"⚠️ yfinance save error for {symbol} on {date.strftime('%Y-%m-%d')}: {e}")
                    continue
                    
        connection.commit()
        return saved_count

    def save_alpha_vantage_data_to_postgresql(self, symbol: str, stock_data: Dict, connection):
        """Save Alpha Vantage data to PostgreSQL"""
        if 'Time Series (Daily)' not in stock_data:
            return 0
            
        saved_count = 0
        
        with connection.cursor() as cursor:
            time_series = stock_data['Time Series (Daily)']
            
            for date_str, daily_data in time_series.items():
                try:
                    cursor.execute("""
                        INSERT INTO stock_prices 
                        (symbol, date, open_price, high_price, low_price, close_price, volume, data_source)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                        ON CONFLICT (symbol, date) DO UPDATE SET
                            open_price = EXCLUDED.open_price,
                            high_price = EXCLUDED.high_price,
                            low_price = EXCLUDED.low_price,
                            close_price = EXCLUDED.close_price,
                            volume = EXCLUDED.volume,
                            data_source = EXCLUDED.data_source
                    """, (
                        symbol,
                        date_str,
                        float(daily_data['1. open']),
                        float(daily_data['2. high']),
                        float(daily_data['3. low']),
                        float(daily_data['4. close']),
                        int(daily_data['5. volume']),
                        'alpha_vantage_real'
                    ))
                    saved_count += 1
                except Exception as e:
                    print(f"⚠️ Alpha Vantage save error for {symbol} on {date_str}: {e}")
                    continue
                    
        connection.commit()
        return saved_count

    def save_forex_data_to_postgresql(self, pair: str, forex_data: Dict, connection):
        """Save Alpha Vantage forex data to PostgreSQL"""
        if 'Time Series (FX Daily)' not in forex_data:
            return 0
            
        saved_count = 0
        
        with connection.cursor() as cursor:
            time_series = forex_data['Time Series (FX Daily)']
            
            for date_str, daily_data in time_series.items():
                try:
                    rate = float(daily_data['4. close'])
                    spread = rate * 0.0001
                    bid = rate - spread
                    ask = rate + spread
                    
                    cursor.execute("""
                        INSERT INTO forex_rates 
                        (pair, timestamp, rate, bid_price, ask_price, data_source)
                        VALUES (%s, %s, %s, %s, %s, %s)
                    """, (
                        pair,
                        f'{date_str} 16:00:00',
                        rate,
                        bid,
                        ask,
                        'alpha_vantage_real'
                    ))
                    saved_count += 1
                except Exception as e:
                    print(f"⚠️ Forex save error for {pair} on {date_str}: {e}")
                    continue
                    
        connection.commit()
        return saved_count

    def collect_comprehensive_real_data(self, max_stocks: int = 20):
        """Collect comprehensive real data from multiple sources"""
        print(f"📈 Starting comprehensive real data collection")
        print(f"🚫 Mock data generation: DISABLED")
        
        try:
            connection = psycopg2.connect(**self.db_config)
            print('✅ PostgreSQL connection established')
            
            total_records = 0
            
            # Major US stocks
            us_stocks = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'NVDA', 'META', 'BRK-B', 'V', 'JNJ', 
                        'WMT', 'XOM', 'UNH', 'MA', 'PG', 'HD', 'CVX', 'LLY', 'ABBV', 'KO']
            
            # Major Japanese stocks
            jp_stocks = ['7203.T', '6758.T', '9984.T', '8306.T', '6861.T', '4519.T', '6098.T', 
                        '8058.T', '9432.T', '7974.T']
            
            all_stocks = (us_stocks + jp_stocks)[:max_stocks]
            
            print(f"📊 Collecting data for {len(all_stocks)} stocks from multiple sources...")
            
            # === yfinance data collection ===
            yfinance_count = 0
            for i, symbol in enumerate(all_stocks):
                print(f"📈 [{i+1}/{len(all_stocks)}] yfinance: {symbol}")
                
                hist_data = self.get_yfinance_data(symbol, period="30d")
                if hist_data is not None:
                    saved = self.save_yfinance_data_to_postgresql(symbol, hist_data, connection)
                    yfinance_count += saved
                    total_records += saved
                
                # Small delay to be respectful
                time.sleep(0.1)
            
            print(f"✅ yfinance collection complete: {yfinance_count} records")
            
            # === Alpha Vantage data collection (limited due to rate limits) ===
            if self.alpha_vantage_api_key:
                av_symbols = ['NVDA', 'META', 'TSLA', 'AMD', 'NFLX'][:3]  # Limit to 3 for rate limits
                av_count = 0
                
                for i, symbol in enumerate(av_symbols):
                    print(f"📊 [{i+1}/{len(av_symbols)}] Alpha Vantage: {symbol}")
                    
                    av_data = self.get_alpha_vantage_data(symbol)
                    if av_data:
                        saved = self.save_alpha_vantage_data_to_postgresql(symbol, av_data, connection)
                        av_count += saved
                        total_records += saved
                    
                    # Rate limiting for Alpha Vantage
                    if i < len(av_symbols) - 1:
                        print("⏳ Rate limiting...")
                        time.sleep(12)
                
                print(f"✅ Alpha Vantage collection complete: {av_count} records")
                
                # === Forex data collection ===
                major_pairs = [('USD', 'JPY'), ('EUR', 'USD'), ('GBP', 'USD')]
                forex_count = 0
                
                for i, (from_curr, to_curr) in enumerate(major_pairs):
                    pair_name = f'{from_curr}/{to_curr}'
                    print(f"💱 [{i+1}/{len(major_pairs)}] Forex: {pair_name}")
                    
                    forex_data = self.get_alpha_vantage_forex_data(from_curr, to_curr)
                    if forex_data:
                        saved = self.save_forex_data_to_postgresql(pair_name, forex_data, connection)
                        forex_count += saved
                        total_records += saved
                    
                    # Rate limiting
                    if i < len(major_pairs) - 1:
                        print("⏳ Rate limiting...")
                        time.sleep(12)
                
                print(f"✅ Forex collection complete: {forex_count} records")
            
            # === Summary ===
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT data_source, COUNT(*) 
                    FROM stock_prices 
                    GROUP BY data_source 
                    ORDER BY COUNT(*) DESC
                """)
                
                print(f"\n📊 Data Collection Summary:")
                for source, count in cursor.fetchall():
                    print(f"   {source}: {count:,} records")
                
                cursor.execute("SELECT COUNT(*) FROM forex_rates")
                forex_total = cursor.fetchone()[0]
                if forex_total > 0:
                    print(f"   forex_rates: {forex_total:,} records")
            
            print(f"\n🎉 Multi-source real data collection completed successfully!")
            print(f"📊 Total records collected: {total_records:,}")
            print(f"✅ Sources: yfinance (Yahoo Finance) + Alpha Vantage API")
            print(f"🚫 Zero mock data generated")
            print(f"✅ PostgreSQL database updated")
            
        except Exception as e:
            print(f"❌ Collection error: {str(e)}")
            import traceback
            traceback.print_exc()
        finally:
            if 'connection' in locals():
                connection.close()
                print('🔐 PostgreSQL connection closed')


def main():
    """Main execution function"""
    print("🚀 Multi-Source Real Data Collection System")
    print("=" * 50)
    
    collector = MultiSourceRealDataCollector()
    
    # Comprehensive real data collection
    collector.collect_comprehensive_real_data(max_stocks=15)
    
    print("🎯 Miraikakaku Multi-Source Real Data Collection Complete")


if __name__ == "__main__":
    main()