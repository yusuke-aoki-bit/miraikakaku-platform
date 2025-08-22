/**
 * Application Configuration Constants
 * Centralizes all magic numbers and configuration values
 */

// ===== API Configuration =====
export const API_CONFIG = {
  DEFAULT_BASE_URL: 'http://localhost:8000', // Data Feed Service統一
  DEFAULT_TIMEOUT: 30000, // 30 seconds
  RETRY_ATTEMPTS: 3,
  RETRY_DELAY: 1000, // 1 second
} as const;

// ===== Search Configuration =====
export const SEARCH_CONFIG = {
  MIN_QUERY_LENGTH: 2,
  DEBOUNCE_DELAY: 300, // milliseconds
  DEFAULT_LIMIT: 10,
  MAX_RESULTS: 50,
} as const;

// ===== Pagination & Limits =====
export const PAGINATION = {
  DEFAULT_PAGE_SIZE: 10,
  SECTOR_STOCKS_LIMIT: 20,
  RANKING_LIMIT: 10,
  TRENDING_STOCKS_LIMIT: 10,
  MAX_NEWS_ITEMS: 4,
} as const;

// ===== Time Periods =====
export const TIME_PERIODS = {
  DEFAULT_PRICE_HISTORY_DAYS: 30,
  DEFAULT_PREDICTION_DAYS: 7,
  HISTORICAL_PREDICTIONS_DAYS: 30,
  LOADING_DELAY: 800, // milliseconds
  ALERT_TIMEOUT: 5000, // milliseconds
} as const;

// ===== WebSocket Configuration =====
export const WEBSOCKET_CONFIG = {
  MAX_RECONNECT_ATTEMPTS: 5,
  RECONNECT_DELAY: 1000, // milliseconds
  CONNECTION_TIMEOUT: 10000, // 10 seconds
  HEARTBEAT_INTERVAL: 30000, // 30 seconds
} as const;

// ===== UI Configuration =====
export const UI_CONFIG = {
  SKELETON_ITEMS: 3,
  MAX_DROPDOWN_HEIGHT: 60, // vh units would be applied separately
  ANIMATION_DURATION: 300, // milliseconds
  HOVER_TRANSITION: 150, // milliseconds
  SCALE_HOVER: 1.05,
} as const;

// ===== Chart Configuration =====
export const CHART_CONFIG = {
  // Chart heights
  DEFAULT_HEIGHT: 400, // pixels
  CANDLESTICK_HEIGHT: 500,
  THUMBNAIL_HEIGHT: 200,
  CHART_HEIGHT: {
    THUMBNAIL: 40,
    SMALL: 192,
    MEDIUM: 300,
    LARGE: 400,
  },
  
  // Animation and styling
  ANIMATION_DURATION: 750,
  GRID_STROKE_WIDTH: 1,
  LINE_STROKE_WIDTH: 2,
  
  // Mock data generation
  CHART_DATA_POINTS: 30,
  CHART_SIN_FREQUENCY: 5,
  CHART_SIN_AMPLITUDE: 5,
  CHART_NOISE_RANGE: 8,
  LSTM_PREDICTION_VARIANCE: 3,
  VERTEX_PREDICTION_VARIANCE: 4,
  
  // Financial calculations
  MAE_BASE: {
    LSTM: 2,
    VERTEX: 1.8,
  },
  MAE_VARIANCE: {
    LSTM: 3,
    VERTEX: 3.5,
  },
  
  // Rating thresholds (for display colors)
  RATING_THRESHOLDS: {
    EXCELLENT: 85,
    GOOD: 70,
  },
  
  // Chart trend calculation
  TREND_CALCULATION: {
    SIN_MULTIPLIER: 0.1,
    VOLATILITY_RANGE: 0.05,
    PRICE_VARIATION: 0.02,
    HIGH_MULTIPLIER: 1.02,
    LOW_MULTIPLIER: 0.98,
  },
  
  // Volume generation
  VOLUME: {
    MIN: 500000,
    MAX: 1000000,
  },
} as const;

// ===== Stock Market Constants =====
export const MARKET_CONFIG = {
  TRADING_HOURS: {
    MARKET_OPEN: 9, // 9:00 AM
    MARKET_CLOSE: 15, // 3:00 PM
    LUNCH_START: 11.5, // 11:30 AM
    LUNCH_END: 12.5, // 12:30 PM
  },
  PRICE_PRECISION: 2,
  PERCENTAGE_PRECISION: 2,
  VOLUME_ABBREVIATION_THRESHOLD: 1000000, // 1M
} as const;

// ===== Ranking & Analysis =====
export const ANALYSIS_CONFIG = {
  CONFIDENCE_THRESHOLD: {
    HIGH: 0.8,
    MEDIUM: 0.6,
    LOW: 0.4,
  },
  GROWTH_THRESHOLD: {
    STRONG_POSITIVE: 5.0, // %
    POSITIVE: 2.0,
    NEUTRAL: -2.0,
    NEGATIVE: -5.0,
  },
  ACCURACY_THRESHOLD: {
    EXCELLENT: 90, // %
    GOOD: 75,
    FAIR: 60,
    POOR: 40,
  },
} as const;

// ===== Investment Analysis Constants =====
export const INVESTMENT_CONFIG = {
  LSTM_ACCURACY: {
    BASE: 75,
    VARIANCE: 20,
  },
  VERTEX_ACCURACY: {
    BASE: 70,
    VARIANCE: 25,
  },
  PROFITABILITY_MULTIPLIER: {
    LSTM: 0.12,
    VERTEX: 0.11,
  },
  RISK_LEVELS: {
    LOW_THRESHOLD: 85,
    MEDIUM_THRESHOLD: 70,
  },
  RECOMMENDATION_THRESHOLDS: {
    STRONG_BUY: 85,
    BUY: 75,
    HOLD: 60,
  },
  PRICE_VARIANCE: {
    MAX_POSITIVE: 0.25,
    MIN_NEGATIVE: -0.08,
    STOP_LOSS_BASE: 0.93,
    STOP_LOSS_VARIANCE: 0.07,
  },
  EXPECTED_RETURN: {
    LSTM: 15,
    VERTEX: 18,
  },
} as const;

// ===== Form Validation =====
export const VALIDATION = {
  MIN_PASSWORD_LENGTH: 8,
  MAX_PASSWORD_LENGTH: 128,
  MIN_USERNAME_LENGTH: 3,
  MAX_USERNAME_LENGTH: 50,
  MAX_COMMENT_LENGTH: 500,
  MAX_SYMBOL_LENGTH: 10,
} as const;

// ===== Cache Configuration =====
export const CACHE_CONFIG = {
  DEFAULT_TTL: 300000, // 5 minutes
  PRICE_DATA_TTL: 60000, // 1 minute
  NEWS_TTL: 900000, // 15 minutes
  RANKING_TTL: 600000, // 10 minutes
  MAX_CACHE_SIZE: 100,
} as const;

// ===== Error Configuration =====
export const ERROR_CONFIG = {
  MAX_ERROR_MESSAGE_LENGTH: 200,
  ERROR_DISPLAY_DURATION: 5000,
  RETRY_EXPONENTIAL_BASE: 2,
  MAX_RETRY_DELAY: 30000, // 30 seconds
} as const;

// ===== Responsive Breakpoints (matching Tailwind) =====
export const BREAKPOINTS = {
  SM: 640,
  MD: 768,
  LG: 1024,
  XL: 1280,
  '2XL': 1536,
} as const;

// ===== Z-Index Layers =====
export const Z_INDEX = {
  DROPDOWN: 10,
  MODAL: 50,
  TOAST: 100,
  TOOLTIP: 1000,
} as const;

// ===== Feature Flags =====
export const FEATURES = {
  ENABLE_WEBSOCKET: true,
  ENABLE_DARK_MODE: true,
  ENABLE_NOTIFICATIONS: true,
  ENABLE_ADVANCED_CHARTS: true,
  ENABLE_EXPORT: false,
} as const;

// ===== Type Definitions =====
export type ApiConfig = typeof API_CONFIG;
export type SearchConfig = typeof SEARCH_CONFIG;
export type TimePeriodsConfig = typeof TIME_PERIODS;
export type UiConfig = typeof UI_CONFIG;
export type MarketConfig = typeof MARKET_CONFIG;
export type AnalysisConfig = typeof ANALYSIS_CONFIG;