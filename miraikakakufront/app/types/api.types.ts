/**
 * API関連の型定義
 * APIレスポンスとリクエストの厳格な型定義
 */

// エラーレスポンス型
export interface ApiError {
  error: string;
  error_code: string;
  category: 'validation' | 'database' | 'external_api' | 'cache' |
           'authentication' | 'authorization' | 'rate_limit' |
           'system' | 'business_logic';
  details?: Record<string, unknown>;
  suggestion?: string;
  timestamp?: string;
}

// APIレスポンスの基本型
export interface ApiResponse<T> {
  data?: T;
  status: 'success' | 'error';
  message?: string;
  error?: ApiError;
}

// ページネーション情報
export interface PaginationInfo {
  page: number;
  limit: number;
  total: number;
  totalPages: number;
  hasNext: boolean;
  hasPrev: boolean;
}

// ページネーション付きレスポンス
export interface PaginatedResponse<T> extends ApiResponse<T> {
  pagination?: PaginationInfo;
}

// 株価データレスポンス
export interface StockPriceResponse {
  symbol: string;
  days_requested: number;
  data_points: number;
  data: import('./index').StockPrice[];
  status: 'success' | 'error';
}

// 株式検索レスポンス
export interface StockSearchResponse {
  query: string;
  limit: number;
  results_count: number;
  results: import('./index').SearchResult[];
  status: 'success' | 'error';
}

// 株価予測レスポンス
export interface StockPredictionResponse {
  symbol: string;
  days_requested: number;
  predictions: import('./index').StockPrediction[];
  model_info?: {
    version: string;
    accuracy: number;
    last_trained: string;
  };
  status: 'success' | 'error';
}

// ヘルスチェックレスポンス
export interface HealthCheckResponse {
  status: 'healthy' | 'degraded' | 'unhealthy';
  version: string;
  database?: {
    status: string;
    response_time_ms?: number;
    error?: string;
  };
  cache?: {
    status: string;
    response_time_ms?: number;
    error?: string;
  };
  system?: {
    status: string;
    cpu_percent?: number;
    memory?: {
      total: number;
      available: number;
      percent: number;
    };
  };
  api?: {
    status: string;
    uptime?: string;
  };
  overall?: {
    status: string;
    checks_passed: number;
    total_checks: number;
    failed_checks?: string[];
  };
  timestamp: string;
}

// APIリクエストパラメータ型
export interface StockPriceParams {
  symbol: string;
  days?: number;
}

export interface StockSearchParams {
  q: string;
  limit?: number;
}

export interface StockPredictionParams {
  symbol: string;
  days?: number;
  model?: string;
}

// 型ガード関数
export function isApiError(error: unknown): error is ApiError {
  return (
    typeof error === 'object' &&
    error !== null &&
    'error' in error &&
    'error_code' in error &&
    'category' in error
}

export function isStockPriceResponse(data: unknown): data is StockPriceResponse {
  return (
    typeof data === 'object' &&
    data !== null &&
    'symbol' in data &&
    'data' in data &&
    Array.isArray((data as any).data)
}

// APIエンドポイント定数
export const API_ENDPOINTS = {
  // 株式関連
  STOCK_PRICE: (symbol: string) => `/api/finance/stocks/${symbol}/price` as const
  STOCK_SEARCH: '/api/finance/stocks/search' as const
  STOCK_PREDICTIONS: (symbol: string) => `/api/finance/stocks/${symbol}/predictions` as const
  STOCK_DETAILS: (symbol: string) => `/api/finance/stocks/${symbol}` as const
  // AI関連
  AI_FACTORS: (symbol: string) => `/api/ai/factors/${symbol}` as const
  AI_ANALYSIS: (symbol: string) => `/api/ai/analysis/${symbol}` as const
  // システム関連
  HEALTH: '/health' as const
  SYSTEM_STATUS: '/api/system/status' as const
  SYSTEM_METRICS: '/api/system/metrics' as const
  // 認証関連
  AUTH_LOGIN: '/api/auth/login' as const
  AUTH_LOGOUT: '/api/auth/logout' as const
  AUTH_REFRESH: '/api/auth/refresh' as const
} as const;

// HTTPメソッド型
export type HttpMethod = 'GET' | 'POST' | 'PUT' | 'DELETE' | 'PATCH';

// リクエスト設定型
export interface RequestConfig {
  method?: HttpMethod;
  headers?: Record<string, string>;
  params?: Record<string, unknown>;
  data?: unknown;
  timeout?: number;
  withCredentials?: boolean;
}

// レスポンスインターセプター型
export type ResponseInterceptor<T = unknown> = (response: T) => T | Promise<T>;

// エラーインターセプター型
export type ErrorInterceptor = (error: unknown) => unknown | Promise<unknown>;

// Re-export existing types for backward compatibility
export type {
  StockPrice
  StockPrediction
  HistoricalPrediction
  StockDetails
  AIDecisionFactor
  SearchResult
} from '../types';