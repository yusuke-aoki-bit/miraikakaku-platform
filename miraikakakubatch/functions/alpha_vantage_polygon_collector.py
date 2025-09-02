#!/usr/bin/env python3
"""
Real Data Collector for Miraikakaku
Uses Alpha Vantage and Polygon APIs for actual market data
"""

import os
import sys
import requests
import pymysql
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import json

class RealDataCollector:
    def __init__(self):
        # API Configuration
        self.alpha_vantage_api_key = os.getenv('ALPHA_VANTAGE_API_KEY', '')
        self.polygon_api_key = os.getenv('POLYGON_API_KEY', '')
        
        # Database Configuration
        self.db_config = {
            'host': os.getenv('DB_HOST', '34.58.103.36'),
            'user': os.getenv('DB_USER', 'miraikakaku-user'),
            'password': os.getenv('DB_PASSWORD', 'miraikakaku-secure-pass-2024'),
            'database': os.getenv('DB_NAME', 'miraikakaku'),
            'charset': 'utf8mb4'
        }
        
        # API Rate Limits
        self.alpha_vantage_calls_per_minute = 5  # Free tier limit
        self.polygon_calls_per_minute = 200      # Paid tier limit
        
        print(f"🚀 Real Data Collector initialized")
        print(f"   Alpha Vantage API: {'✅' if self.alpha_vantage_api_key else '❌ Missing API key'}")
        print(f"   Polygon API: {'✅' if self.polygon_api_key else '❌ Missing API key'}")

    def get_alpha_vantage_stock_data(self, symbol: str) -> Optional[Dict]:
        """Get real stock data from Alpha Vantage API"""
        if not self.alpha_vantage_api_key:
            print(f"❌ Alpha Vantage API key missing for {symbol}")
            return None
            
        url = f"https://www.alphavantage.co/query"
        params = {
            'function': 'TIME_SERIES_DAILY_ADJUSTED',
            'symbol': symbol,
            'outputsize': 'compact',  # Last 100 data points
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
                
            return data
            
        except Exception as e:
            print(f"❌ Alpha Vantage API error for {symbol}: {str(e)}")
            return None

    def get_polygon_stock_data(self, symbol: str, days_back: int = 30) -> Optional[Dict]:
        """Get real stock data from Polygon API"""
        if not self.polygon_api_key:
            print(f"❌ Polygon API key missing for {symbol}")
            return None
            
        # Calculate date range
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=days_back)).strftime('%Y-%m-%d')
        
        url = f"https://api.polygon.io/v2/aggs/ticker/{symbol}/range/1/day/{start_date}/{end_date}"
        params = {
            'adjusted': 'true',
            'sort': 'desc',
            'apikey': self.polygon_api_key
        }
        
        try:
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            if data.get('status') != 'OK':
                print(f"❌ Polygon error for {symbol}: {data.get('error', 'Unknown error')}")
                return None
                
            return data
            
        except Exception as e:
            print(f"❌ Polygon API error for {symbol}: {str(e)}")
            return None

    def get_alpha_vantage_forex_data(self, from_currency: str, to_currency: str) -> Optional[Dict]:
        """Get real forex data from Alpha Vantage"""
        if not self.alpha_vantage_api_key:
            return None
            
        url = f"https://www.alphavantage.co/query"
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
                
            return data
            
        except Exception as e:
            print(f"❌ Alpha Vantage forex error for {from_currency}/{to_currency}: {str(e)}")
            return None

    def save_stock_data_to_db(self, symbol: str, stock_data: Dict, source: str):
        """Save real stock data to database"""
        try:
            connection = pymysql.connect(**self.db_config)
            with connection.cursor() as cursor:
                
                # Process Alpha Vantage data
                if source == 'alpha_vantage' and 'Time Series (Daily)' in stock_data:
                    time_series = stock_data['Time Series (Daily)']
                    
                    for date_str, daily_data in time_series.items():
                        try:
                            # Insert into stock_prices table
                            cursor.execute("""
                                INSERT IGNORE INTO stock_prices 
                                (symbol, date, open_price, high_price, low_price, close_price, volume, data_source)
                                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                            """, (
                                symbol,
                                date_str,
                                float(daily_data['1. open']),
                                float(daily_data['2. high']),
                                float(daily_data['3. low']),
                                float(daily_data['4. close']),
                                int(daily_data['6. volume']),
                                'alpha_vantage'
                            ))
                        except (ValueError, KeyError) as e:
                            print(f"⚠️ Data parsing error for {symbol} on {date_str}: {e}")
                            continue
                
                # Process Polygon data
                elif source == 'polygon' and 'results' in stock_data:
                    results = stock_data['results']
                    
                    for daily_data in results:
                        try:
                            # Convert timestamp to date
                            date_obj = datetime.fromtimestamp(daily_data['t'] / 1000)
                            date_str = date_obj.strftime('%Y-%m-%d')
                            
                            cursor.execute("""
                                INSERT IGNORE INTO stock_prices 
                                (symbol, date, open_price, high_price, low_price, close_price, volume, data_source)
                                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                            """, (
                                symbol,
                                date_str,
                                float(daily_data['o']),  # open
                                float(daily_data['h']),  # high
                                float(daily_data['l']),  # low
                                float(daily_data['c']),  # close
                                int(daily_data['v']),    # volume
                                'polygon'
                            ))
                        except (ValueError, KeyError) as e:
                            print(f"⚠️ Polygon data parsing error for {symbol}: {e}")
                            continue
                
                connection.commit()
                rows_affected = cursor.rowcount
                print(f"✅ {symbol}: {rows_affected} real data points saved from {source}")
                
        except Exception as e:
            print(f"❌ Database error for {symbol}: {str(e)}")
        finally:
            if 'connection' in locals():
                connection.close()

    def save_forex_data_to_db(self, pair: str, forex_data: Dict):
        """Save real forex data to database"""
        try:
            connection = pymysql.connect(**self.db_config)
            with connection.cursor() as cursor:
                
                # Create forex_rates table if it doesn't exist
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS forex_rates (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        pair VARCHAR(10) NOT NULL,
                        timestamp DATETIME NOT NULL,
                        rate DECIMAL(10,5) NOT NULL,
                        bid_price DECIMAL(10,5),
                        ask_price DECIMAL(10,5),
                        data_source VARCHAR(50),
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        INDEX idx_pair_timestamp (pair, timestamp)
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
                """)
                
                if 'Time Series (FX Daily)' in forex_data:
                    time_series = forex_data['Time Series (FX Daily)']
                    
                    for date_str, daily_data in time_series.items():
                        try:
                            rate = float(daily_data['4. close'])
                            # Simulate bid/ask spread (typically 0.001-0.01% of rate)
                            spread = rate * 0.0001
                            bid = rate - spread
                            ask = rate + spread
                            
                            cursor.execute("""
                                INSERT IGNORE INTO forex_rates 
                                (pair, timestamp, rate, bid_price, ask_price, data_source)
                                VALUES (%s, %s, %s, %s, %s, %s)
                            """, (
                                pair,
                                f"{date_str} 16:00:00",  # Market close time
                                rate,
                                bid,
                                ask,
                                'alpha_vantage'
                            ))
                        except (ValueError, KeyError) as e:
                            print(f"⚠️ Forex data parsing error for {pair} on {date_str}: {e}")
                            continue
                
                connection.commit()
                rows_affected = cursor.rowcount
                print(f"✅ {pair}: {rows_affected} real forex data points saved")
                
        except Exception as e:
            print(f"❌ Database error for forex {pair}: {str(e)}")
        finally:
            if 'connection' in locals():
                connection.close()

    def collect_real_stock_data(self, symbols: List[str], max_symbols: int = 10):
        """Collect real stock data for given symbols"""
        print(f"📈 Starting real stock data collection for {min(len(symbols), max_symbols)} symbols")
        
        collected = 0
        for symbol in symbols[:max_symbols]:
            if collected >= max_symbols:
                break
                
            print(f"📊 Collecting data for {symbol}...")
            
            # Try Polygon first (higher rate limit)
            if self.polygon_api_key:
                data = self.get_polygon_stock_data(symbol)
                if data:
                    self.save_stock_data_to_db(symbol, data, 'polygon')
                    collected += 1
                    time.sleep(0.3)  # Rate limiting
                    continue
            
            # Fallback to Alpha Vantage
            if self.alpha_vantage_api_key:
                data = self.get_alpha_vantage_stock_data(symbol)
                if data:
                    self.save_stock_data_to_db(symbol, data, 'alpha_vantage')
                    collected += 1
                    time.sleep(12)  # Alpha Vantage rate limiting (5 calls/minute)
            
        print(f"✅ Real stock data collection completed: {collected}/{len(symbols)} symbols")

    def collect_real_forex_data(self, currency_pairs: List[Tuple[str, str]], max_pairs: int = 5):
        """Collect real forex data for given currency pairs"""
        if not self.alpha_vantage_api_key:
            print("❌ Alpha Vantage API key required for forex data")
            return
            
        print(f"💱 Starting real forex data collection for {min(len(currency_pairs), max_pairs)} pairs")
        
        collected = 0
        for from_curr, to_curr in currency_pairs[:max_pairs]:
            if collected >= max_pairs:
                break
                
            pair_name = f"{from_curr}/{to_curr}"
            print(f"💱 Collecting data for {pair_name}...")
            
            data = self.get_alpha_vantage_forex_data(from_curr, to_curr)
            if data:
                self.save_forex_data_to_db(pair_name, data)
                collected += 1
                
            time.sleep(12)  # Alpha Vantage rate limiting
            
        print(f"✅ Real forex data collection completed: {collected}/{len(currency_pairs)} pairs")

    def get_active_symbols_from_db(self) -> List[str]:
        """Get active stock symbols from database"""
        try:
            connection = pymysql.connect(**self.db_config)
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT DISTINCT symbol FROM stock_master 
                    WHERE is_active = 1 
                    ORDER BY symbol 
                    LIMIT 50
                """)
                symbols = [row[0] for row in cursor.fetchall()]
                return symbols
        except Exception as e:
            print(f"❌ Database error getting symbols: {str(e)}")
            return []
        finally:
            if 'connection' in locals():
                connection.close()


def main():
    """Main execution function"""
    print("🚀 Real Data Collection System Starting")
    print("=" * 50)
    
    collector = RealDataCollector()
    
    # Check API keys
    if not collector.alpha_vantage_api_key and not collector.polygon_api_key:
        print("❌ No API keys configured. Please set environment variables:")
        print("   - ALPHA_VANTAGE_API_KEY")
        print("   - POLYGON_API_KEY")
        sys.exit(1)
    
    # Get active symbols from database
    symbols = collector.get_active_symbols_from_db()
    if not symbols:
        print("❌ No active symbols found in database")
        sys.exit(1)
    
    print(f"📊 Found {len(symbols)} active symbols in database")
    
    # Collect real stock data (limited to avoid rate limits)
    collector.collect_real_stock_data(symbols, max_symbols=10)
    
    # Collect real forex data
    major_pairs = [
        ('USD', 'JPY'),
        ('EUR', 'USD'),
        ('GBP', 'USD'),
        ('EUR', 'JPY'),
        ('AUD', 'USD')
    ]
    
    collector.collect_real_forex_data(major_pairs, max_pairs=3)
    
    print("🎉 Real data collection completed successfully")


if __name__ == "__main__":
    main()