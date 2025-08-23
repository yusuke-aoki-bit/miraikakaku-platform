#!/usr/bin/env python3
"""
外部キー制約問題の修正 - stock_masterに必要な銘柄を追加
"""

import logging
import sys
import os
from sqlalchemy import text

# パスを追加
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database.database import get_db

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def fix_foreign_key_constraints():
    """外部キー制約問題を修正"""
    
    logger.info("🔧 外部キー制約問題の修正開始")
    
    db = next(get_db())
    
    try:
        # 主要銘柄リスト（バッチ処理でよく使用される）
        major_symbols = [
            # 米国指数
            ('GSPC', 'S&P 500 Index', 'INDEX', 'NYSE', 'United States', True),
            ('DJI', 'Dow Jones Industrial Average', 'INDEX', 'NYSE', 'United States', True),
            ('IXIC', 'NASDAQ Composite Index', 'INDEX', 'NASDAQ', 'United States', True),
            ('RUT', 'Russell 2000 Index', 'INDEX', 'NYSE', 'United States', True),
            ('VIX', 'CBOE Volatility Index', 'INDEX', 'CBOE', 'United States', True),
            ('TNX', '10-Year Treasury Note Yield', 'INDEX', 'NYSE', 'United States', True),
            
            # 米国主要株
            ('AAPL', 'Apple Inc.', 'Technology', 'NASDAQ', 'United States', True),
            ('MSFT', 'Microsoft Corporation', 'Technology', 'NASDAQ', 'United States', True),
            ('GOOGL', 'Alphabet Inc. Class A', 'Technology', 'NASDAQ', 'United States', True),
            ('AMZN', 'Amazon.com Inc.', 'Consumer', 'NASDAQ', 'United States', True),
            ('TSLA', 'Tesla Inc.', 'Automotive', 'NASDAQ', 'United States', True),
            ('META', 'Meta Platforms Inc.', 'Technology', 'NASDAQ', 'United States', True),
            ('NVDA', 'NVIDIA Corporation', 'Technology', 'NASDAQ', 'United States', True),
            ('JPM', 'JPMorgan Chase & Co.', 'Finance', 'NYSE', 'United States', True),
            ('V', 'Visa Inc.', 'Finance', 'NYSE', 'United States', True),
            ('MA', 'Mastercard Inc.', 'Finance', 'NYSE', 'United States', True),
            
            # 主要ETF
            ('SPY', 'SPDR S&P 500 ETF Trust', 'ETF', 'NYSE', 'United States', True),
            ('QQQ', 'Invesco QQQ Trust', 'ETF', 'NASDAQ', 'United States', True),
            ('IWM', 'iShares Russell 2000 ETF', 'ETF', 'NYSE', 'United States', True),
            ('VTI', 'Vanguard Total Stock Market ETF', 'ETF', 'NYSE', 'United States', True),
            ('GLD', 'SPDR Gold Shares', 'ETF', 'NYSE', 'United States', True),
        ]
        
        logger.info(f"追加対象: {len(major_symbols)}銘柄")
        
        added_count = 0
        updated_count = 0
        
        for db_symbol, name, sector, market, country, is_active in major_symbols:
            try:
                # 既存チェック
                result = db.execute(text(
                    "SELECT COUNT(*) FROM stock_master WHERE symbol = :symbol"
                ), {"symbol": db_symbol})
                
                exists = result.scalar() > 0
                
                if exists:
                    # 既存レコードの更新
                    db.execute(text("""
                        UPDATE stock_master SET 
                            name = :name,
                            sector = :sector,
                            market = :market,
                            country = :country,
                            is_active = :is_active,
                            updated_at = NOW()
                        WHERE symbol = :symbol
                    """), {
                        "symbol": db_symbol,
                        "name": name,
                        "sector": sector,
                        "market": market,
                        "country": country,
                        "is_active": is_active
                    })
                    updated_count += 1
                    logger.info(f"  ✅ 更新: {db_symbol} ({name})")
                else:
                    # 新規追加
                    db.execute(text("""
                        INSERT INTO stock_master 
                        (symbol, name, sector, market, country, is_active, created_at, updated_at)
                        VALUES (:symbol, :name, :sector, :market, :country, :is_active, NOW(), NOW())
                    """), {
                        "symbol": db_symbol,
                        "name": name,
                        "sector": sector,
                        "market": market,
                        "country": country,
                        "is_active": is_active
                    })
                    added_count += 1
                    logger.info(f"  ➕ 追加: {db_symbol} ({name})")
                    
            except Exception as e:
                logger.error(f"  ❌ エラー {db_symbol}: {e}")
                continue
        
        db.commit()
        
        logger.info(f"✅ 外部キー制約修正完了")
        logger.info(f"  追加: {added_count}件")
        logger.info(f"  更新: {updated_count}件")
        
        # 修正後の確認
        result = db.execute(text("SELECT COUNT(*) FROM stock_master WHERE is_active = 1"))
        total_active = result.scalar()
        
        logger.info(f"📊 修正後統計:")
        logger.info(f"  アクティブ銘柄総数: {total_active:,}")
        
        return {
            'added': added_count,
            'updated': updated_count,
            'total_active': total_active
        }
        
    finally:
        db.close()

if __name__ == "__main__":
    result = fix_foreign_key_constraints()
    logger.info(f"🎉 修正完了: 追加{result['added']}件, 更新{result['updated']}件")