-- Cloud SQL Database Schema Creation
-- Database: miraikakaku_prod

CREATE DATABASE IF NOT EXISTS miraikakaku_prod;
USE miraikakaku_prod;

-- Stock Master Table
CREATE TABLE IF NOT EXISTS stock_master (
    id INT AUTO_INCREMENT PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL UNIQUE,
    name VARCHAR(255) NOT NULL,
    sector VARCHAR(100),
    market VARCHAR(50),
    country VARCHAR(50) DEFAULT 'Japan',
    currency VARCHAR(10) DEFAULT 'JPY',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_symbol (symbol),
    INDEX idx_country (country),
    INDEX idx_market (market),
    INDEX idx_is_active (is_active)
);

-- Stock Prices Table
CREATE TABLE IF NOT EXISTS stock_prices (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL,
    date DATE NOT NULL,
    open_price DECIMAL(15,4),
    high_price DECIMAL(15,4),
    low_price DECIMAL(15,4),
    close_price DECIMAL(15,4),
    volume BIGINT,
    adjusted_close DECIMAL(15,4),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY unique_symbol_date (symbol, date),
    INDEX idx_symbol (symbol),
    INDEX idx_date (date),
    FOREIGN KEY (symbol) REFERENCES stock_master(symbol) ON DELETE CASCADE
);

-- Stock Predictions Table
CREATE TABLE IF NOT EXISTS stock_predictions (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL,
    prediction_date DATE NOT NULL,
    prediction_days INT DEFAULT 7,
    current_price DECIMAL(15,4),
    predicted_price DECIMAL(15,4),
    confidence_score DECIMAL(5,4),
    prediction_range_low DECIMAL(15,4),
    prediction_range_high DECIMAL(15,4),
    model_version VARCHAR(50),
    model_accuracy DECIMAL(5,4),
    features_used TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_symbol (symbol),
    INDEX idx_prediction_date (prediction_date),
    FOREIGN KEY (symbol) REFERENCES stock_master(symbol) ON DELETE CASCADE
);

-- Batch Logs Table
CREATE TABLE IF NOT EXISTS batch_logs (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    batch_type VARCHAR(50) NOT NULL,
    status VARCHAR(20) NOT NULL,
    start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    end_time TIMESTAMP NULL,
    records_processed INT DEFAULT 0,
    error_message TEXT,
    details JSON,
    INDEX idx_batch_type (batch_type),
    INDEX idx_status (status),
    INDEX idx_start_time (start_time)
);

-- Analysis Reports Table
CREATE TABLE IF NOT EXISTS analysis_reports (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    report_type VARCHAR(50) NOT NULL,
    report_date DATE NOT NULL,
    symbols_analyzed JSON,
    market_sentiment VARCHAR(20),
    top_performers JSON,
    predictions_accuracy DECIMAL(5,4),
    key_insights JSON,
    report_data JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_report_type (report_type),
    INDEX idx_report_date (report_date)
);

-- Show table status
SHOW TABLES;
SELECT 'Schema created successfully' AS status;