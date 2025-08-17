// 株式関連の型定義
export interface Stock {
  symbol: string;
  company_name: string;
  exchange: string;
  sector?: string;
  industry?: string;
  market_cap?: string;
  currency?: string;
  country?: string;
  is_active?: boolean;
}

export interface StockPrice {
  symbol: string;
  date: string;
  open_price?: number;
  high_price?: number;
  low_price?: number;
  close_price: number;
  adjusted_close?: number;
  volume?: number;
  data_source: string;
}

export interface StockPrediction {
  symbol: string;
  prediction_date: string;
  target_date: string;
  predicted_price: number;
  confidence_score?: number;
  prediction_type: 'daily' | 'weekly' | 'monthly';
  model_name: string;
  model_version?: string;
  actual_price?: number;
  accuracy_score?: number;
}

// API応答型
export interface APIResponse<T = any> {
  data?: T;
  error?: string;
  message?: string;
  status: 'success' | 'error';
}

export interface PaginatedResponse<T> extends APIResponse<T[]> {
  total: number;
  page: number;
  limit: number;
  pages: number;
}

// 認証関連
export interface User {
  id: string;
  email: string;
  name: string;
  role: 'admin' | 'user' | 'analyst';
  created_at: string;
  last_login?: string;
}

export interface AuthToken {
  access_token: string;
  token_type: string;
  expires_in: number;
  refresh_token?: string;
}

// WebSocket メッセージ型
export interface WebSocketMessage {
  type: 'price_update' | 'prediction_update' | 'system_alert';
  data: any;
  timestamp: string;
}

export interface PriceUpdateMessage extends WebSocketMessage {
  type: 'price_update';
  data: {
    symbol: string;
    price: number;
    change: number;
    change_percent: number;
  };
}

// チャート設定
export interface ChartConfig {
  type: 'line' | 'candlestick' | 'area';
  timeframe: '1d' | '1w' | '1m' | '3m' | '6m' | '1y';
  indicators: string[];
  theme: 'light' | 'dark';
}