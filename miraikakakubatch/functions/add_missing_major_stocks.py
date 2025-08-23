#!/usr/bin/env python3
"""
不足している主要米国株を緊急追加
バッチ処理でエラーが出ている銘柄を事前登録
"""

import yfinance as yf
import logging
from database.cloud_sql_only import db
from sqlalchemy import text
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def add_missing_major_stocks():
    """エラーが出ている主要銘柄を緊急追加"""
    
    # バッチでエラーが出ている銘柄
    missing_symbols = [
        # 金融
        'WFC', 'MS', 'C', 'GS', 'AXP', 'V', 'MA', 'JPM', 'BAC',
        
        # 消費・小売
        'WMT', 'HD', 'PG', 'JNJ', 'KO', 'PEP', 'MCD', 'NKE', 'DIS',
        
        # エネルギー・工業
        'XOM', 'CVX', 'COP', 'SLB', 'BA', 'CAT', 'GE', 'MMM',
        'HON', 'UPS', 'LMT', 'RTX', 'DE', 'F', 'GM',
        
        # ETF
        'SPY', 'QQQ', 'IWM', 'VTI', 'VEA', 'VWO', 'BND', 'TLT',
        'GLD', 'SLV', 'USO', 'XLK', 'XLF', 'XLE', 'XLV', 'XLI',
        
        # 指数
        '^GSPC', '^DJI', '^IXIC', '^RUT', '^VIX', '^TNX'
    ]
    
    logger.info(f"🔧 不足銘柄の緊急追加開始: {len(missing_symbols)}銘柄")
    
    with db.engine.connect() as conn:
        added_count = 0
        skipped_count = 0
        error_count = 0
        
        for symbol in missing_symbols:
            try:
                # 存在チェック
                exists = conn.execute(text('SELECT COUNT(*) FROM stock_master WHERE symbol = :sym'), 
                                    {'sym': symbol}).scalar()
                
                if exists > 0:
                    logger.info(f"⏭️  {symbol}: 既に存在")
                    skipped_count += 1
                    continue
                
                # Yahoo Financeから情報取得
                ticker = yf.Ticker(symbol)
                
                try:
                    info = ticker.info
                    company_name = info.get('longName', info.get('shortName', symbol))
                    sector = info.get('sector', 'Financial Services' if symbol in ['WFC', 'MS', 'C', 'GS', 'AXP', 'JPM', 'BAC'] else 'Unknown')
                    
                    # 指数の場合
                    if symbol.startswith('^'):
                        company_name = {
                            '^GSPC': 'S&P 500 Index',
                            '^DJI': 'Dow Jones Industrial Average',
                            '^IXIC': 'NASDAQ Composite',
                            '^RUT': 'Russell 2000 Index',
                            '^VIX': 'CBOE Volatility Index',
                            '^TNX': '10-Year Treasury Yield'
                        }.get(symbol, f'{symbol} Index')
                        sector = 'Index'
                        country = 'US'
                        currency = 'USD'
                    else:
                        country = info.get('country', 'US')
                        currency = info.get('currency', 'USD')
                    
                except:
                    # フォールバック情報
                    company_name = symbol
                    sector = 'Unknown'
                    country = 'US'
                    currency = 'USD'
                
                # 市場判定
                market = 'NYSE'  # デフォルト
                if symbol in ['AAPL', 'MSFT', 'GOOGL', 'TSLA', 'META', 'AMZN', 'QQQ']:
                    market = 'NASDAQ'
                elif symbol.startswith('^'):
                    market = 'INDEX'
                elif symbol in ['SPY', 'IWM', 'VTI', 'BND', 'GLD', 'USO']:
                    market = 'ETF'
                
                # stock_masterに挿入
                conn.execute(text("""
                    INSERT INTO stock_master 
                    (symbol, name, sector, market, country, currency, is_active, created_at, updated_at)
                    VALUES (:sym, :name, :sector, :market, :country, :currency, 1, NOW(), NOW())
                """), {
                    "sym": symbol,
                    "name": company_name[:255],  # 長さ制限
                    "sector": sector[:100],
                    "market": market,
                    "country": country,
                    "currency": currency
                })
                
                conn.commit()
                logger.info(f"✅ {symbol}: 追加完了 - {company_name}")
                added_count += 1
                
                # API制限対策
                time.sleep(0.1)
                
            except Exception as e:
                logger.error(f"❌ {symbol}: エラー - {e}")
                error_count += 1
                continue
        
        logger.info("="*60)
        logger.info(f"🎯 銘柄追加完了")
        logger.info(f"✅ 追加: {added_count}銘柄")
        logger.info(f"⏭️  スキップ: {skipped_count}銘柄")
        logger.info(f"❌ エラー: {error_count}銘柄")
        logger.info("="*60)
        
        return {
            'added': added_count,
            'skipped': skipped_count,
            'errors': error_count
        }

if __name__ == "__main__":
    add_missing_major_stocks()