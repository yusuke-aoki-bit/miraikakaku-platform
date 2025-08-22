/**
 * マジックナンバー定数定義
 * アプリケーション全体で使用される数値定数を集約
 */

// 株価関連
export const STOCK_CONSTANTS = {
  // 価格範囲
  BASE_PRICE: 150,
  PRICE_VARIATION: 50,
  MIN_PRICE: 0.01,
  MAX_PRICE: 10000,
  
  // 変動率
  MAX_CHANGE_PERCENT: 10,
  EXTREME_CHANGE_THRESHOLD: 5,
  
  // 出来高
  BASE_VOLUME: 10000000, // 1千万
  MIN_VOLUME: 100000,    // 10万
  MAX_VOLUME: 1000000000, // 10億
  
  // 時価総額
  BASE_MARKET_CAP: 1000000000000, // 1兆
  MIN_MARKET_CAP: 1000000000,     // 10億
  
  // PER
  BASE_PE_RATIO: 15,
  PE_RATIO_VARIATION: 25,
  HIGH_PE_THRESHOLD: 30,
  LOW_PE_THRESHOLD: 5,
} as const;

// 予測・AI関連
export const PREDICTION_CONSTANTS = {
  // 信頼度
  MIN_CONFIDENCE: 70,
  MAX_CONFIDENCE: 95,
  CONFIDENCE_VARIATION: 25,
  HIGH_CONFIDENCE_THRESHOLD: 85,
  
  // 精度
  BASE_ACCURACY: 75,
  ACCURACY_VARIATION: 20,
  HIGH_ACCURACY_THRESHOLD: 90,
  
  // 予測期間
  SHORT_TERM_DAYS: 7,
  MEDIUM_TERM_DAYS: 30,
  LONG_TERM_DAYS: 90,
  
  // 予測範囲
  PREDICTION_VARIANCE: 0.2,  // 20%
  UPPER_BOUND_MULTIPLIER: 1.002,
  LOWER_BOUND_MULTIPLIER: 0.998,
} as const;

// 為替関連
export const CURRENCY_CONSTANTS = {
  // 主要通貨ペアのベースレート
  BASE_RATES: {
    'USD/JPY': 150.25,
    'EUR/USD': 1.0845,
    'GBP/USD': 1.2715,
    'EUR/JPY': 162.90,
    'AUD/USD': 0.6523,
    'USD/CHF': 0.8834,
    'USD/CAD': 1.3598,
    'NZD/USD': 0.6145,
  },
  
  // 変動幅
  RATE_VARIATION: 0.01,     // 1%
  DAILY_VOLATILITY: 0.02,   // 2%
  TREND_FACTOR: 0.002,      // 0.2%
  VOLATILITY_RANGE: 0.001,  // 0.1%
  
  // スプレッド
  DEFAULT_SPREAD: 0.0002,   // 2pips
  BID_ASK_SPREAD: 0.0001,   // 1pip
} as const;

// チャート・UI関連
export const UI_CONSTANTS = {
  // チャートサイズ
  CHART_HEIGHT: {
    THUMBNAIL: 120,
    SMALL: 200,
    MEDIUM: 300,
    LARGE: 400,
  },
  
  // データポイント数
  CHART_DATA_POINTS: 30,
  MAX_DATA_POINTS: 100,
  MIN_DATA_POINTS: 7,
  
  // アニメーション
  ANIMATION_DURATION: 300,
  LOADING_DELAY: 800,
  ALERT_TIMEOUT: 5000,
  
  // ページネーション
  ITEMS_PER_PAGE: 20,
  MAX_ITEMS_PER_PAGE: 100,
  
  // しきい値
  RATING_THRESHOLDS: {
    EXCELLENT: 85,
    GOOD: 70,
    FAIR: 50,
    POOR: 30,
  },
} as const;

// 時間関連
export const TIME_CONSTANTS = {
  // 更新間隔 (ミリ秒)
  REALTIME_UPDATE_INTERVAL: 30000,  // 30秒
  PRICE_UPDATE_INTERVAL: 60000,     // 1分
  CHART_UPDATE_INTERVAL: 300000,    // 5分
  
  // キャッシュ期間 (ミリ秒)
  CACHE_DURATION: {
    SHORT: 5 * 60 * 1000,      // 5分
    MEDIUM: 30 * 60 * 1000,    // 30分
    LONG: 60 * 60 * 1000,      // 1時間
    DAILY: 24 * 60 * 60 * 1000, // 24時間
  },
  
  // デフォルト期間 (日数)
  DEFAULT_PERIODS: {
    PRICE_HISTORY: 30,
    PREDICTION: 7,
    HISTORICAL_ANALYSIS: 90,
  },
} as const;

// 数学的定数
export const MATH_CONSTANTS = {
  // 統計
  STANDARD_DEVIATION_MULTIPLIER: 2,
  CONFIDENCE_INTERVAL_95: 1.96,
  CORRELATION_THRESHOLD: 0.7,
  
  // フィルタリング
  OUTLIER_THRESHOLD: 3,        // 3σ
  NOISE_FILTER: 0.01,         // 1%
  SMOOTHING_FACTOR: 0.1,      // 10%
  
  // 計算精度
  DECIMAL_PLACES: {
    PRICE: 2,
    PERCENTAGE: 2,
    CURRENCY: 4,
    RATIO: 3,
    VOLUME: 0,
  },
} as const;

// ビジネスロジック定数
export const BUSINESS_CONSTANTS = {
  // 推奨レベル
  RECOMMENDATION_THRESHOLDS: {
    STRONG_BUY: 85,
    BUY: 75,
    HOLD: 60,
    SELL: 40,
    STRONG_SELL: 25,
  },
  
  // リスクレベル
  RISK_LEVELS: {
    LOW_THRESHOLD: 80,
    MEDIUM_THRESHOLD: 60,
    HIGH_THRESHOLD: 40,
  },
  
  // アラート
  ALERT_THRESHOLDS: {
    PRICE_CHANGE: 5,      // 5%
    VOLUME_SPIKE: 200,    // 200%
    VOLATILITY_HIGH: 3,   // 3σ
  },
} as const;

// バリデーション定数
export const VALIDATION_CONSTANTS = {
  // 文字列長
  MAX_SYMBOL_LENGTH: 10,
  MAX_COMPANY_NAME_LENGTH: 100,
  MAX_DESCRIPTION_LENGTH: 500,
  
  // 数値範囲
  MIN_QUANTITY: 0.001,
  MAX_QUANTITY: 1000000,
  MIN_PRICE_ALERT: 0.01,
  MAX_PRICE_ALERT: 100000,
  
  // 配列サイズ
  MAX_WATCHLIST_ITEMS: 50,
  MAX_PORTFOLIO_ITEMS: 100,
  MAX_ALERTS: 20,
} as const;

// エラー関連
export const ERROR_CONSTANTS = {
  // リトライ
  MAX_RETRY_ATTEMPTS: 3,
  RETRY_DELAY_BASE: 1000,     // 1秒
  RETRY_DELAY_MULTIPLIER: 2,  // 指数バックオフ
  
  // タイムアウト
  API_TIMEOUT: 10000,         // 10秒
  CACHE_TIMEOUT: 30000,       // 30秒
  
  // HTTP ステータス
  SUCCESS_CODES: [200, 201, 202, 204],
  RETRY_CODES: [408, 429, 500, 502, 503, 504],
} as const;

// デバッグ・ログ関連
export const DEBUG_CONSTANTS = {
  // ログレベル
  LOG_LEVELS: {
    ERROR: 0,
    WARN: 1,
    INFO: 2,
    DEBUG: 3,
    TRACE: 4,
  },
  
  // パフォーマンス
  PERFORMANCE_THRESHOLDS: {
    SLOW_QUERY: 1000,      // 1秒
    MEMORY_WARNING: 100,   // 100MB
    CPU_WARNING: 80,       // 80%
  },
} as const;