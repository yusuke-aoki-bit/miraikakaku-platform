// API エンドポイント
export const API_ENDPOINTS = {
  STOCKS: {
    SEARCH: '/api/finance/stocks/search',
    PRICE: '/api/finance/stocks/{symbol}/price',
    PREDICTIONS: '/api/finance/stocks/{symbol}/predictions',
    CREATE_PREDICTION: '/api/finance/stocks/{symbol}/predict',
  },
  AUTH: {
    LOGIN: '/api/auth/login',
    LOGOUT: '/api/auth/logout',
    REFRESH: '/api/auth/refresh',
    PROFILE: '/api/auth/profile',
  },
  HEALTH: '/health',
} as const;

// チャート設定
export const CHART_COLORS = {
  PRIMARY: 'rgb(59, 130, 246)',
  SECONDARY: 'rgb(16, 185, 129)',
  WARNING: 'rgb(245, 158, 11)',
  ERROR: 'rgb(239, 68, 68)',
  BACKGROUND: 'rgba(59, 130, 246, 0.1)',
} as const;

export const TIME_RANGES = {
  '1D': { days: 1, label: '1日' },
  '1W': { days: 7, label: '1週間' },
  '1M': { days: 30, label: '1ヶ月' },
  '3M': { days: 90, label: '3ヶ月' },
  '6M': { days: 180, label: '6ヶ月' },
  '1Y': { days: 365, label: '1年' },
} as const;

// 株式市場
export const EXCHANGES = {
  NASDAQ: 'NASDAQ',
  NYSE: 'NYSE',
  TSE: 'TSE', // Tokyo Stock Exchange
  LSE: 'LSE', // London Stock Exchange
} as const;

// 予測モデル
export const ML_MODELS = {
  SIMPLE_MA: 'simple_ma',
  RANDOM_FOREST: 'random_forest',
  LSTM: 'lstm',
  PROPHET: 'prophet',
  XGBOOST: 'xgboost',
} as const;

// ユーザーロール
export const USER_ROLES = {
  ADMIN: 'admin',
  USER: 'user',
  ANALYST: 'analyst',
} as const;

// WebSocket イベント
export const WS_EVENTS = {
  PRICE_UPDATE: 'price_update',
  PREDICTION_UPDATE: 'prediction_update',
  SYSTEM_ALERT: 'system_alert',
  CONNECTION: 'connection',
  DISCONNECTION: 'disconnection',
} as const;