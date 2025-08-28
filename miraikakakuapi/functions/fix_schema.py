#!/usr/bin/env python3
"""
Database schema migration script to fix missing columns
"""

from database.cloud_sql_only import get_db, get_engine
from sqlalchemy import text
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def migrate_schema():
    """Add missing columns and create missing tables"""
    engine = get_engine()
    
    # First check if market column exists
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT COUNT(*) 
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_NAME = 'stock_master' 
            AND COLUMN_NAME = 'market'
            AND TABLE_SCHEMA = DATABASE()
        """))
        market_exists = result.scalar() > 0
    
    migrations = []
    
    # Only add market column if it doesn't exist
    if not market_exists:
        migrations.append("""
            ALTER TABLE stock_master 
            ADD COLUMN market VARCHAR(50) 
            AFTER exchange
        """)
    
    # Create stock_prices table if not exists (simpler structure)
    migrations.append("""
        CREATE TABLE IF NOT EXISTS stock_prices (
            id INT AUTO_INCREMENT PRIMARY KEY,
            symbol VARCHAR(20) NOT NULL,
            date DATE NOT NULL,
            open_price DECIMAL(10, 2),
            high_price DECIMAL(10, 2),
            low_price DECIMAL(10, 2),
            close_price DECIMAL(10, 2),
            volume BIGINT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE KEY unique_symbol_date (symbol, date),
            INDEX idx_symbol (symbol),
            INDEX idx_date (date)
        )
    """)
    
    # Update market column values based on exchange (only if column was added)
    if not market_exists:
        migrations.append("""
            UPDATE stock_master 
            SET market = CASE 
                WHEN exchange LIKE '%NYSE%' THEN 'US'
                WHEN exchange LIKE '%NASDAQ%' THEN 'US'
                WHEN exchange LIKE '%TSE%' THEN 'JP'
                WHEN exchange LIKE '%JPX%' THEN 'JP'
                WHEN exchange LIKE '%Tokyo%' THEN 'JP'
                ELSE 'OTHER'
            END
            WHERE market IS NULL
        """)
    
    # Modify country column
    migrations.append("""
        ALTER TABLE stock_master
        MODIFY COLUMN country VARCHAR(50) DEFAULT 'US'
    """)
    
    with engine.connect() as conn:
        for i, migration in enumerate(migrations, 1):
            try:
                logger.info(f"Running migration {i}/{len(migrations)}...")
                # Clean up the SQL
                clean_sql = ' '.join(migration.strip().split())
                conn.execute(text(clean_sql))
                conn.commit()
                logger.info(f"✅ Migration {i} completed successfully")
            except Exception as e:
                if "Duplicate column" in str(e) or "already exists" in str(e):
                    logger.info(f"ℹ️ Migration {i} skipped (already applied)")
                else:
                    logger.error(f"❌ Migration {i} failed: {e}")
    
    # Verify the changes
    with engine.connect() as conn:
        # Check stock_master columns
        result = conn.execute(text("""
            SELECT COLUMN_NAME 
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_NAME = 'stock_master' 
            AND TABLE_SCHEMA = DATABASE()
            ORDER BY ORDINAL_POSITION
        """))
        columns = [row[0] for row in result]
        logger.info(f"\nstock_master columns: {columns}")
        
        # Check if stock_prices table exists
        result = conn.execute(text("""
            SELECT COUNT(*) 
            FROM INFORMATION_SCHEMA.TABLES 
            WHERE TABLE_NAME = 'stock_prices' 
            AND TABLE_SCHEMA = DATABASE()
        """))
        exists = result.scalar() > 0
        logger.info(f"stock_prices table exists: {exists}")
        
        # Check if market column exists now
        result = conn.execute(text("""
            SELECT COUNT(*) 
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_NAME = 'stock_master' 
            AND COLUMN_NAME = 'market'
            AND TABLE_SCHEMA = DATABASE()
        """))
        has_market = result.scalar() > 0
        
        # Sample data check
        if has_market:
            query = "SELECT symbol, name, exchange, market, country FROM stock_master LIMIT 5"
        else:
            query = "SELECT symbol, name, exchange, country FROM stock_master LIMIT 5"
        
        result = conn.execute(text(query))
        logger.info("\nSample stock_master data:")
        for row in result:
            logger.info(f"  {row}")


def add_sample_data():
    """Add sample stock data if empty"""
    engine = get_engine()
    
    with engine.connect() as conn:
        # Check if we have any stocks
        result = conn.execute(text("SELECT COUNT(*) FROM stock_master"))
        count = result.scalar()
        
        # Check if market column exists
        result = conn.execute(text("""
            SELECT COUNT(*) 
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_NAME = 'stock_master' 
            AND COLUMN_NAME = 'market'
            AND TABLE_SCHEMA = DATABASE()
        """))
        has_market = result.scalar() > 0
        
        if count == 0:
            logger.info("Adding sample stock data...")
            
            sample_stocks = [
                ("AAPL", "Apple Inc.", "NASDAQ", "US", "US"),
                ("GOOGL", "Alphabet Inc.", "NASDAQ", "US", "US"),
                ("MSFT", "Microsoft Corporation", "NASDAQ", "US", "US"),
                ("7203.T", "Toyota Motor Corporation", "TSE", "JP", "JP"),
                ("9984.T", "SoftBank Group Corp.", "TSE", "JP", "JP"),
                ("^N225", "Nikkei 225", "INDEX", "JP", "JP"),
                ("^DJI", "Dow Jones Industrial Average", "INDEX", "US", "US"),
                ("^GSPC", "S&P 500", "INDEX", "US", "US"),
            ]
            
            for symbol, name, exchange, market, country in sample_stocks:
                try:
                    if has_market:
                        conn.execute(text("""
                            INSERT INTO stock_master (symbol, name, exchange, market, country)
                            VALUES (:symbol, :name, :exchange, :market, :country)
                        """), {
                            "symbol": symbol,
                            "name": name,
                            "exchange": exchange,
                            "market": market,
                            "country": country
                        })
                    else:
                        conn.execute(text("""
                            INSERT INTO stock_master (symbol, name, exchange, country)
                            VALUES (:symbol, :name, :exchange, :country)
                        """), {
                            "symbol": symbol,
                            "name": name,
                            "exchange": exchange,
                            "country": country
                        })
                    conn.commit()
                    logger.info(f"  Added {symbol}")
                except Exception as e:
                    logger.warning(f"  Failed to add {symbol}: {e}")


if __name__ == "__main__":
    logger.info("Starting schema migration...")
    migrate_schema()
    add_sample_data()
    logger.info("\n✅ Schema migration completed!")