-- Miraikakaku Database Schema for Cloud SQL
-- 株価データと予測結果を管理するためのテーブル設計

-- 株式マスターテーブル
CREATE TABLE IF NOT EXISTS stock_master (
    symbol VARCHAR(10) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    sector VARCHAR(100),
    market_cap BIGINT,
    currency VARCHAR(3) DEFAULT 'USD',
    exchange VARCHAR(50),
    country VARCHAR(50) DEFAULT 'US',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- 株価履歴テーブル
CREATE TABLE IF NOT EXISTS stock_prices (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    symbol VARCHAR(10) NOT NULL,
    date DATE NOT NULL,
    open_price DECIMAL(12,4),
    high_price DECIMAL(12,4),
    low_price DECIMAL(12,4),
    close_price DECIMAL(12,4) NOT NULL,
    volume BIGINT,
    adjusted_close DECIMAL(12,4),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (symbol) REFERENCES stock_master(symbol),
    UNIQUE KEY unique_symbol_date (symbol, date),
    INDEX idx_symbol_date (symbol, date),
    INDEX idx_date (date)
);

-- AI予測結果テーブル
CREATE TABLE IF NOT EXISTS stock_predictions (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    symbol VARCHAR(10) NOT NULL,
    prediction_date DATE NOT NULL,
    prediction_days INT NOT NULL,
    current_price DECIMAL(12,4) NOT NULL,
    predicted_price DECIMAL(12,4) NOT NULL,
    confidence_score DECIMAL(5,2),
    prediction_range_low DECIMAL(12,4),
    prediction_range_high DECIMAL(12,4),
    model_version VARCHAR(50) DEFAULT 'LSTM_v1.0',
    model_accuracy DECIMAL(5,2),
    features_used JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (symbol) REFERENCES stock_master(symbol),
    INDEX idx_symbol_pred_date (symbol, prediction_date),
    INDEX idx_prediction_date (prediction_date)
);

-- 市場指標テーブル
CREATE TABLE IF NOT EXISTS market_indices (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    index_symbol VARCHAR(10) NOT NULL,
    index_name VARCHAR(100) NOT NULL,
    date DATE NOT NULL,
    value DECIMAL(12,4) NOT NULL,
    change_percent DECIMAL(5,2),
    volume BIGINT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY unique_index_date (index_symbol, date),
    INDEX idx_index_date (index_symbol, date)
);

-- バッチ処理ログテーブル
CREATE TABLE IF NOT EXISTS batch_logs (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    batch_type VARCHAR(50) NOT NULL,
    status ENUM('started', 'running', 'completed', 'failed') NOT NULL,
    start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    end_time TIMESTAMP NULL,
    records_processed INT DEFAULT 0,
    error_message TEXT,
    details JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_batch_type_status (batch_type, status),
    INDEX idx_start_time (start_time)
);

-- 分析レポートテーブル
CREATE TABLE IF NOT EXISTS analysis_reports (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    report_type VARCHAR(50) NOT NULL,
    report_date DATE NOT NULL,
    symbols_analyzed JSON,
    market_sentiment VARCHAR(20),
    top_performers JSON,
    predictions_accuracy DECIMAL(5,2),
    key_insights JSON,
    report_data JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_report_date (report_date),
    INDEX idx_report_type (report_type)
);

-- ユーザーウォッチリストテーブル（将来拡張用）
CREATE TABLE IF NOT EXISTS user_watchlists (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    user_id VARCHAR(100) NOT NULL,
    symbol VARCHAR(10) NOT NULL,
    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    alert_threshold_up DECIMAL(5,2),
    alert_threshold_down DECIMAL(5,2),
    FOREIGN KEY (symbol) REFERENCES stock_master(symbol),
    UNIQUE KEY unique_user_symbol (user_id, symbol),
    INDEX idx_user_id (user_id)
);

-- 初期データ挿入
INSERT IGNORE INTO stock_master (symbol, name, sector, market_cap, exchange, country) VALUES
('AAPL', 'Apple Inc.', 'Technology', 3000000000000, 'NASDAQ', 'US'),
('GOOGL', 'Alphabet Inc.', 'Technology', 2000000000000, 'NASDAQ', 'US'),
('MSFT', 'Microsoft Corporation', 'Technology', 2800000000000, 'NASDAQ', 'US'),
('AMZN', 'Amazon.com Inc.', 'Consumer Discretionary', 1500000000000, 'NASDAQ', 'US'),
('TSLA', 'Tesla Inc.', 'Automotive', 800000000000, 'NASDAQ', 'US'),
('META', 'Meta Platforms Inc.', 'Technology', 900000000000, 'NASDAQ', 'US'),
('NVDA', 'NVIDIA Corporation', 'Technology', 2200000000000, 'NASDAQ', 'US'),
('JPM', 'JPMorgan Chase & Co.', 'Financial Services', 500000000000, 'NYSE', 'US'),
('V', 'Visa Inc.', 'Financial Services', 450000000000, 'NYSE', 'US'),
('JNJ', 'Johnson & Johnson', 'Healthcare', 400000000000, 'NYSE', 'US');

INSERT IGNORE INTO market_indices (index_symbol, index_name) VALUES
('^GSPC', 'S&P 500'),
('^IXIC', 'NASDAQ Composite'),
('^DJI', 'Dow Jones Industrial Average'),
('^N225', 'Nikkei 225');