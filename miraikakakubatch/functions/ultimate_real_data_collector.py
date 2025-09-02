#!/usr/bin/env python3
"""
Ultimate Multi-Source Real Data Collector for Miraikakaku
Uses yfinance + Alpha Vantage + pandas-datareader for comprehensive real market data
NO MOCK DATA - Real data only from multiple sources
"""

import os
import sys
import requests
import psycopg2
import yfinance as yf
import pandas_datareader.data as web
import pandas as pd
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

class UltimateRealDataCollector:
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
        
        print(f"🚀 Ultimate Multi-Source Real Data Collector initialized")
        print(f"   yfinance (Yahoo Finance): ✅ Direct API access")
        print(f"   Alpha Vantage API: {'✅' if self.alpha_vantage_api_key else '❌ Missing API key'}")
        print(f"   pandas-datareader: ✅ Multiple source access")
        print(f"   Database: PostgreSQL")

    def create_economic_data_table(self, connection):
        """Create table for economic indicators"""
        with connection.cursor() as cursor:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS economic_indicators (
                    id SERIAL PRIMARY KEY,
                    indicator_code VARCHAR(20) NOT NULL,
                    indicator_name VARCHAR(200),
                    date DATE NOT NULL,
                    value DECIMAL(15,4),
                    data_source VARCHAR(50),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(indicator_code, date)
                )
            """)
            connection.commit()
            print("✅ Economic indicators table ready")

    def get_yfinance_data(self, symbol: str, period: str = "60d") -> Optional[pd.DataFrame]:
        """Get real stock data from Yahoo Finance via yfinance"""
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period=period)
            
            if hist.empty:
                print(f"❌ yfinance: No data for {symbol}")
                return None
                
            print(f"✅ yfinance: {symbol} - {len(hist)} days of real data")
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
            'outputsize': 'full',  # Get more historical data
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

    def get_fred_economic_data(self, indicator: str, name: str, days_back: int = 365) -> Optional[pd.DataFrame]:
        """Get real economic data from FRED via pandas-datareader"""
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days_back)
            
            data = web.DataReader(indicator, 'fred', start_date, end_date)
            
            if data.empty:
                print(f"❌ FRED: No data for {indicator}")
                return None
                
            print(f"✅ FRED: {indicator} ({name}) - {len(data)} data points")
            return data
            
        except Exception as e:
            print(f"❌ FRED error for {indicator}: {str(e)}")
            return None

    def get_stooq_data(self, symbol: str, days_back: int = 60) -> Optional[pd.DataFrame]:
        """Get data from Stooq via pandas-datareader (alternative source)"""
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days_back)
            
            data = web.DataReader(symbol, 'stooq', start_date, end_date)
            
            if data.empty:
                print(f"❌ Stooq: No data for {symbol}")
                return None
                
            print(f"✅ Stooq: {symbol} - {len(data)} days")
            return data
            
        except Exception as e:
            print(f"❌ Stooq error for {symbol}: {str(e)}")
            return None

    def save_yfinance_data_to_postgresql(self, symbol: str, hist_data: pd.DataFrame, connection, source_suffix: str = ""):
        """Save yfinance data to PostgreSQL"""
        saved_count = 0
        source_name = f"yfinance{('_' + source_suffix) if source_suffix else ''}"
        
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
                        source_name
                    ))
                    saved_count += 1
                except Exception as e:
                    print(f"⚠️ {source_name} save error for {symbol} on {date.strftime('%Y-%m-%d')}: {e}")
                    continue
                    
        connection.commit()
        return saved_count

    def save_economic_data_to_postgresql(self, indicator_code: str, indicator_name: str, data: pd.DataFrame, connection):
        """Save economic data to PostgreSQL"""
        saved_count = 0
        
        with connection.cursor() as cursor:
            for date, row in data.iterrows():
                try:
                    value = float(row.iloc[0]) if pd.notna(row.iloc[0]) else None
                    if value is not None:
                        cursor.execute("""
                            INSERT INTO economic_indicators 
                            (indicator_code, indicator_name, date, value, data_source)
                            VALUES (%s, %s, %s, %s, %s)
                            ON CONFLICT (indicator_code, date) DO UPDATE SET
                                value = EXCLUDED.value,
                                data_source = EXCLUDED.data_source
                        """, (
                            indicator_code,
                            indicator_name,
                            date.strftime('%Y-%m-%d'),
                            value,
                            'fred_real'
                        ))
                        saved_count += 1
                except Exception as e:
                    print(f"⚠️ Economic data save error for {indicator_code}: {e}")
                    continue
                    
        connection.commit()
        return saved_count

    def collect_ultimate_real_data(self, max_stocks: int = 25):
        """Collect comprehensive real data from all available sources"""
        print(f"🌍 Starting ultimate real data collection from all sources")
        print(f"🚫 Mock data generation: DISABLED")
        
        try:
            connection = psycopg2.connect(**self.db_config)
            print('✅ PostgreSQL connection established')
            
            # Create economic data table
            self.create_economic_data_table(connection)
            
            total_records = 0
            
            # === ECONOMIC INDICATORS (FRED) ===
            print("\\n📊 Economic Indicators Collection (FRED)")
            
            economic_indicators = [
                ('GDP', 'Gross Domestic Product'),
                ('UNRATE', 'Unemployment Rate'),
                ('CPIAUCSL', 'Consumer Price Index'),
                ('FEDFUNDS', 'Federal Funds Rate'),
                ('DGS10', '10-Year Treasury Rate'),
                ('DEXUSEU', 'USD/EUR Exchange Rate'),
                ('DEXJPUS', 'JPY/USD Exchange Rate')
            ]
            
            for indicator_code, indicator_name in economic_indicators:
                econ_data = self.get_fred_economic_data(indicator_code, indicator_name, days_back=730)  # 2 years
                if econ_data is not None:
                    saved = self.save_economic_data_to_postgresql(indicator_code, indicator_name, econ_data, connection)
                    total_records += saved
                    print(f"✅ {indicator_code}: {saved} records saved")
                
                time.sleep(0.5)  # Be respectful to FRED
            
            # === COMPREHENSIVE STOCK DATA ===
            print("\\n📈 Comprehensive Stock Data Collection")
            
            # Expanded stock universe
            us_mega_caps = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'NVDA', 'META', 'BRK-B', 'V', 'JNJ', 
                           'WMT', 'XOM', 'UNH', 'MA', 'PG', 'HD', 'CVX', 'LLY', 'ABBV', 'KO']
            
            tech_stocks = ['CRM', 'ORCL', 'NFLX', 'ADBE', 'PYPL', 'INTC', 'AMD', 'QCOM', 'TXN', 'AVGO']
            
            jp_major_stocks = ['7203.T', '6758.T', '9984.T', '8306.T', '6861.T', '4519.T', '6098.T', 
                              '8058.T', '9432.T', '7974.T']
            
            european_stocks = ['ASML.AS', 'SAP.DE', 'MC.PA', 'RMS.PA', 'OR.PA']  # ASML, SAP, LVMH, Hermes, L'Oreal
            
            all_stocks = (us_mega_caps + tech_stocks + jp_major_stocks + european_stocks)[:max_stocks]
            
            print(f"📊 Collecting data for {len(all_stocks)} global stocks...")
            
            # yfinance collection with extended period
            yfinance_count = 0
            for i, symbol in enumerate(all_stocks):
                print(f"📈 [{i+1}/{len(all_stocks)}] yfinance: {symbol}")
                
                hist_data = self.get_yfinance_data(symbol, period="90d")  # 3 months
                if hist_data is not None:
                    saved = self.save_yfinance_data_to_postgresql(symbol, hist_data, connection, "ultimate")
                    yfinance_count += saved
                    total_records += saved
                
                time.sleep(0.1)  # Rate limiting
            
            print(f"✅ yfinance collection complete: {yfinance_count} records")
            
            # === ALPHA VANTAGE SUPPLEMENTAL DATA ===
            if self.alpha_vantage_api_key:
                print("\\n📊 Alpha Vantage Supplemental Data Collection")
                
                # Focus on key stocks for Alpha Vantage (due to rate limits)
                av_priority_symbols = ['NVDA', 'TSLA', 'META', 'AMZN', 'GOOGL'][:3]
                av_count = 0
                
                for i, symbol in enumerate(av_priority_symbols):
                    print(f"📊 [{i+1}/{len(av_priority_symbols)}] Alpha Vantage: {symbol}")
                    
                    av_data = self.get_alpha_vantage_data(symbol)
                    if av_data and 'Time Series (Daily)' in av_data:
                        # Save Alpha Vantage data (more historical depth)
                        time_series = av_data['Time Series (Daily)']
                        av_saved = 0
                        
                        with connection.cursor() as cursor:
                            for date_str, daily_data in list(time_series.items())[:100]:  # Limit to 100 days
                                try:
                                    cursor.execute("""
                                        INSERT INTO stock_prices 
                                        (symbol, date, open_price, high_price, low_price, close_price, volume, data_source)
                                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                                        ON CONFLICT (symbol, date) DO UPDATE SET
                                            data_source = 'alpha_vantage_ultimate'
                                    """, (
                                        symbol,
                                        date_str,
                                        float(daily_data['1. open']),
                                        float(daily_data['2. high']),
                                        float(daily_data['3. low']),
                                        float(daily_data['4. close']),
                                        int(daily_data['5. volume']),
                                        'alpha_vantage_ultimate'
                                    ))
                                    av_saved += 1
                                except Exception as e:
                                    continue
                        
                        connection.commit()
                        av_count += av_saved
                        total_records += av_saved
                        print(f"✅ Alpha Vantage {symbol}: {av_saved} records")
                    
                    # Rate limiting for Alpha Vantage
                    if i < len(av_priority_symbols) - 1:
                        print("⏳ Alpha Vantage rate limiting...")
                        time.sleep(12)
                
                print(f"✅ Alpha Vantage collection complete: {av_count} records")
            
            # === ALTERNATIVE DATA SOURCES ===
            print("\\n🌍 Alternative Data Sources (Stooq)")
            
            # Try some European/Asian stocks via Stooq
            stooq_symbols = ['SPY.US', 'QQQ.US', 'EURUSD.FOREX']  # ETFs and Forex
            stooq_count = 0
            
            for symbol in stooq_symbols:
                try:
                    stooq_data = self.get_stooq_data(symbol, days_back=30)
                    if stooq_data is not None:
                        saved = self.save_yfinance_data_to_postgresql(symbol.replace('.', '_'), stooq_data, connection, "stooq")
                        stooq_count += saved
                        total_records += saved
                except Exception as e:
                    print(f"⚠️ Stooq {symbol} error: {e}")
                
                time.sleep(0.5)
            
            if stooq_count > 0:
                print(f"✅ Stooq collection complete: {stooq_count} records")
            
            # === FINAL SUMMARY ===
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT data_source, COUNT(*) 
                    FROM stock_prices 
                    GROUP BY data_source 
                    ORDER BY COUNT(*) DESC
                """)
                
                print(f"\\n📊 Stock Data Collection Summary:")
                for source, count in cursor.fetchall():
                    print(f"   {source}: {count:,} records")
                
                cursor.execute("SELECT COUNT(*) FROM economic_indicators")
                econ_total = cursor.fetchone()[0]
                if econ_total > 0:
                    print(f"   economic_indicators: {econ_total:,} records")
                
                cursor.execute("SELECT COUNT(*) FROM stock_prices")
                stock_total = cursor.fetchone()[0]
                
                cursor.execute("SELECT COUNT(DISTINCT symbol) FROM stock_prices")
                unique_symbols = cursor.fetchone()[0]
            
            print(f"\\n🎉 Ultimate multi-source real data collection completed!")
            print(f"📊 Total records collected: {total_records:,}")
            print(f"📈 Stock records: {stock_total:,}")
            print(f"📊 Economic indicators: {econ_total:,}")
            print(f"🌍 Unique symbols: {unique_symbols}")
            print(f"✅ Sources: yfinance + Alpha Vantage + pandas-datareader (FRED + Stooq)")
            print(f"🚫 Zero mock data generated")
            print(f"✅ PostgreSQL database updated with real data only")
            
        except Exception as e:
            print(f"❌ Ultimate collection error: {str(e)}")
            import traceback
            traceback.print_exc()
        finally:
            if 'connection' in locals():
                connection.close()
                print('🔐 PostgreSQL connection closed')


def main():
    """Main execution function"""
    print("🚀 Ultimate Multi-Source Real Data Collection System")
    print("=" * 60)
    
    collector = UltimateRealDataCollector()
    
    # Ultimate real data collection
    collector.collect_ultimate_real_data(max_stocks=20)
    
    print("🎯 Miraikakaku Ultimate Real Data Collection Complete")


if __name__ == "__main__":
    main()