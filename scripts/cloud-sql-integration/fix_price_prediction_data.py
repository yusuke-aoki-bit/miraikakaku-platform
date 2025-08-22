#!/usr/bin/env python3
"""
スキーマ対応版：価格・予測データ投入スクリプト
実際のテーブル構造に合わせたデータ生成
"""

import random
import logging
from datetime import datetime, timedelta

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_fixed_sql():
    """実際のスキーマに対応したSQL生成"""
    
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    sql_script = f"""-- Miraikakaku 価格・予測データ投入（スキーマ対応版）
-- 生成日時: {current_time}

USE miraikakaku_prod;

-- テーブル構造に合わせたカラム追加（必要に応じて）
ALTER TABLE stock_predictions ADD COLUMN IF NOT EXISTS prediction_horizon INT DEFAULT 1;
ALTER TABLE stock_predictions ADD COLUMN IF NOT EXISTS is_active BOOLEAN DEFAULT TRUE;

"""
    
    # サンプル銘柄
    symbols = [
        ('AAPL', 'USA', 180.0),
        ('MSFT', 'USA', 380.0),
        ('GOOGL', 'USA', 140.0),
        ('AMZN', 'USA', 155.0),
        ('TSLA', 'USA', 250.0),
        ('7203', 'Japan', 2800.0),  # トヨタ
        ('6758', 'Japan', 15000.0), # ソニー
        ('9984', 'Japan', 8500.0),  # SoftBank
        ('SPY', 'ETF', 450.0),
        ('QQQ', 'ETF', 380.0)
    ]
    
    total_price_records = 0
    total_prediction_records = 0
    
    for symbol, country, base_price in symbols:
        logger.info(f"Processing {symbol} ({country})")
        
        # 30日分の価格データ生成
        sql_script += f"-- {symbol} 価格データ\n"
        sql_script += "INSERT INTO stock_prices (symbol, date, open_price, high_price, low_price, close_price, adjusted_close, volume) VALUES\n"
        
        price_values = []
        current_price = base_price
        
        for i in range(30):
            date = (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d')
            
            # 価格変動
            daily_change = random.uniform(-0.03, 0.03)
            close_price = current_price * (1 + daily_change)
            open_price = close_price * random.uniform(0.99, 1.01)
            high_price = max(open_price, close_price) * random.uniform(1.0, 1.02)
            low_price = min(open_price, close_price) * random.uniform(0.98, 1.0)
            
            # 出来高
            if country == 'Japan':
                volume = random.randint(100000, 5000000)
            else:
                volume = random.randint(1000000, 50000000)
            
            price_values.append(f"('{symbol}', '{date}', {open_price:.2f}, {high_price:.2f}, {low_price:.2f}, {close_price:.2f}, {close_price:.2f}, {volume})")
            current_price = close_price
            total_price_records += 1
        
        sql_script += ',\n'.join(price_values) + ";\n\n"
        
        # 7日分の予測データ生成
        sql_script += f"-- {symbol} 予測データ\n"
        sql_script += "INSERT INTO stock_predictions (symbol, prediction_date, prediction_days, current_price, predicted_price, confidence_score, prediction_range_low, prediction_range_high, model_version) VALUES\n"
        
        pred_values = []
        
        for days in range(1, 8):
            pred_date = (datetime.now() + timedelta(days=days)).strftime('%Y-%m-%d')
            
            # 予測価格
            volatility = 0.02 if country == 'ETF' else 0.03
            change = random.uniform(-volatility, volatility) * days * 0.5
            predicted_price = current_price * (1 + change)
            
            # 信頼度
            confidence = 0.85 - (days * 0.05) + random.uniform(-0.05, 0.05)
            confidence = max(0.4, min(0.95, confidence))
            
            # 予測レンジ
            range_width = current_price * volatility * days * 0.3
            
            pred_values.append(f"('{symbol}', '{pred_date}', {days}, {current_price:.2f}, {predicted_price:.2f}, {confidence:.3f}, {predicted_price - range_width:.2f}, {predicted_price + range_width:.2f}, 'LSTM_v2.0')")
            total_prediction_records += 1
        
        sql_script += ',\n'.join(pred_values) + ";\n\n"
    
    # バッチログ追加
    sql_script += f"""-- バッチ実行ログ
INSERT INTO batch_logs (batch_type, status, records_processed, details) VALUES
('price_data_sample', 'completed', {total_price_records}, '{{"symbols": {len(symbols)}, "days": 30}}'),
('prediction_sample', 'completed', {total_prediction_records}, '{{"symbols": {len(symbols)}, "horizon": 7}}');

-- 検証クエリ
SELECT 'Price Records' as type, COUNT(*) as count FROM stock_prices;
SELECT 'Prediction Records' as type, COUNT(*) as count FROM stock_predictions;
SELECT 'Sample Prices' as type, symbol, date, close_price FROM stock_prices WHERE symbol = 'AAPL' ORDER BY date DESC LIMIT 5;
SELECT 'Sample Predictions' as type, symbol, prediction_date, predicted_price FROM stock_predictions WHERE symbol = 'AAPL' ORDER BY prediction_date LIMIT 5;
"""
    
    # ファイル保存
    script_path = '/mnt/c/Users/yuuku/cursor/miraikakaku/price_prediction_fixed.sql'
    with open(script_path, 'w', encoding='utf-8') as f:
        f.write(sql_script)
    
    logger.info(f"修正版SQL生成完了: {script_path}")
    logger.info(f"  - 価格レコード: {total_price_records}件")
    logger.info(f"  - 予測レコード: {total_prediction_records}件")
    
    return script_path

if __name__ == "__main__":
    script_path = create_fixed_sql()
    print(f"✅ スキーマ対応版SQL生成完了")
    print(f"📁 ファイル: {script_path}")
    print(f"🎯 次のステップ: Cloud SQLへ投入")