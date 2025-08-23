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

-- ユーザープロファイルテーブル
CREATE TABLE IF NOT EXISTS user_profiles (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    user_id VARCHAR(100) UNIQUE NOT NULL,
    username VARCHAR(50),
    email VARCHAR(100),
    investment_style ENUM('conservative', 'moderate', 'aggressive', 'growth', 'value') DEFAULT 'moderate',
    risk_tolerance ENUM('low', 'medium', 'high') DEFAULT 'medium',
    investment_experience ENUM('beginner', 'intermediate', 'advanced', 'expert') DEFAULT 'beginner',
    preferred_sectors JSON,
    investment_goals TEXT,
    total_portfolio_value DECIMAL(15,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_user_id (user_id),
    INDEX idx_investment_style (investment_style)
);

-- ユーザーウォッチリストテーブル
CREATE TABLE IF NOT EXISTS user_watchlists (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    user_id VARCHAR(100) NOT NULL,
    symbol VARCHAR(10) NOT NULL,
    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    alert_threshold_up DECIMAL(5,2),
    alert_threshold_down DECIMAL(5,2),
    notes TEXT,
    priority ENUM('high', 'medium', 'low') DEFAULT 'medium',
    FOREIGN KEY (symbol) REFERENCES stock_master(symbol),
    FOREIGN KEY (user_id) REFERENCES user_profiles(user_id),
    UNIQUE KEY unique_user_symbol (user_id, symbol),
    INDEX idx_user_id (user_id)
);

-- AI判断根拠テーブル
CREATE TABLE IF NOT EXISTS ai_decision_factors (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    prediction_id BIGINT NOT NULL,
    factor_type ENUM('technical', 'fundamental', 'sentiment', 'news', 'pattern') NOT NULL,
    factor_name VARCHAR(100) NOT NULL,
    influence_score DECIMAL(5,2) NOT NULL,
    description TEXT,
    confidence DECIMAL(5,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (prediction_id) REFERENCES stock_predictions(id),
    INDEX idx_prediction_id (prediction_id),
    INDEX idx_factor_type (factor_type)
);

-- ユーザーポートフォリオテーブル
CREATE TABLE IF NOT EXISTS user_portfolios (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    user_id VARCHAR(100) NOT NULL,
    symbol VARCHAR(10) NOT NULL,
    shares DECIMAL(10,4) NOT NULL,
    average_cost DECIMAL(12,4) NOT NULL,
    purchase_date DATE,
    portfolio_weight DECIMAL(5,2),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES user_profiles(user_id),
    FOREIGN KEY (symbol) REFERENCES stock_master(symbol),
    INDEX idx_user_portfolio (user_id, symbol),
    INDEX idx_user_active (user_id, is_active)
);

-- コミュニティ予測コンテストテーブル
CREATE TABLE IF NOT EXISTS prediction_contests (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    contest_name VARCHAR(100) NOT NULL,
    symbol VARCHAR(10) NOT NULL,
    contest_start_date DATE NOT NULL,
    prediction_deadline DATETIME NOT NULL,
    target_date DATE NOT NULL,
    actual_price DECIMAL(12,4),
    status ENUM('active', 'closed', 'completed') DEFAULT 'active',
    prize_description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (symbol) REFERENCES stock_master(symbol),
    INDEX idx_contest_status (status),
    INDEX idx_target_date (target_date)
);

-- ユーザー予測コンテスト参加テーブル
CREATE TABLE IF NOT EXISTS user_contest_predictions (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    contest_id BIGINT NOT NULL,
    user_id VARCHAR(100) NOT NULL,
    predicted_price DECIMAL(12,4) NOT NULL,
    confidence_level ENUM('low', 'medium', 'high') DEFAULT 'medium',
    reasoning TEXT,
    accuracy_score DECIMAL(5,2),
    rank_position INT,
    submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (contest_id) REFERENCES prediction_contests(id),
    FOREIGN KEY (user_id) REFERENCES user_profiles(user_id),
    UNIQUE KEY unique_contest_user (contest_id, user_id),
    INDEX idx_contest_accuracy (contest_id, accuracy_score DESC)
);

-- テーマ別インサイトテーブル
CREATE TABLE IF NOT EXISTS theme_insights (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    theme_name VARCHAR(50) NOT NULL,
    theme_category ENUM('technology', 'energy', 'finance', 'healthcare', 'consumer', 'industrial', 'materials') NOT NULL,
    insight_date DATE NOT NULL,
    title VARCHAR(200) NOT NULL,
    summary TEXT NOT NULL,
    key_metrics JSON,
    related_symbols JSON,
    trend_direction ENUM('bullish', 'bearish', 'neutral') DEFAULT 'neutral',
    impact_score DECIMAL(3,1),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_theme_date (theme_name, insight_date),
    INDEX idx_category (theme_category),
    INDEX idx_trend (trend_direction)
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