export interface StockPrice {
  id?: number;
  symbol: string;
  date: string;
  open_price: number | null;
  high_price: number | null;
  low_price: number | null;
  close_price: number | null;
  volume: number | null;
  created_at?: string;
  updated_at?: string;
  normalized_price?: number;
}

export interface StockPrediction {
  id?: string;
  symbol: string;
  prediction_date: string;
  predicted_price: number;
  confidence_score?: number;
  model_name?: string;
  created_at?: string;
  // Legacy fields for backward compatibility
  confidence?: number | null;
  model_version?: string;
}

// New dual prediction system types
export interface DualPredictionSystem {
  lstm: SinglePrediction;
  vertex_ai: SinglePrediction;
}

export interface SinglePrediction {
  predicted_price: number;
  confidence_score: number;
  model_type: string;
  prediction_date: string;
  market_conditions: MarketConditions;
  features_used?: string[];
  vertex_ai_status?: string;
}

export interface MarketConditions {
  volatility: number;
  rsi: number;
  macd_signal: string;
  trend: string;
  volume_analysis: string;
  bollinger_position: number;
}

export interface DualPredictionResponse {
  symbol: string;
  timeframe: string;
  timestamp: string;
  predictions: DualPredictionSystem;
  comparison: PredictionComparison;
}

export interface PredictionComparison {
  price_difference: number;
  difference_percentage: number;
  average_predicted_price: number;
  higher_prediction: 'lstm' | 'vertex_ai';
  confidence_winner: 'lstm' | 'vertex_ai';
  consensus: boolean;
}

export interface HistoricalPrediction {
  id?: string;
  symbol: string;
  predicted_price: number;
  actual_price?: number | null;
  actual_date?: string;
  target_date?: string;  // New API field
  prediction_date?: string;
  prediction_made_date?: string;
  accuracy_percentage?: number;
  accuracy_score?: number;  // New API field
  model_name?: string;
  confidence_score?: number;
  created_at?: string;
  is_validated?: boolean;  // New API field
  // Legacy fields for backward compatibility
  accuracy?: number | null;
}

export interface StockDetails {
  symbol: string;
  longName?: string;
  shortName?: string;
  sector?: string;
  industry?: string;
  country?: string;
  website?: string;
  longBusinessSummary?: string;
  marketCap?: number;
  previousClose?: number;
  dayHigh?: number;
  dayLow?: number;
  volume?: number;
  averageVolume?: number;
  fiftyTwoWeekHigh?: number;
  fiftyTwoWeekLow?: number;
  dividendYield?: number;
  beta?: number;
  trailingPE?: number;
  forwardPE?: number;
}

export interface AIDecisionFactor {
  factor: string;
  reason: string;
  impact?: 'positive' | 'negative' | 'neutral';
  weight?: number;
}

export interface SearchResult {
  symbol: string;
  longName?: string;
  shortName?: string;
  name?: string;
  type?: string;
  sector?: string;
  industry?: string;
  quoteType?: string;
  price?: number;
  change?: number;
  changePercent?: number;
  volume?: number;
  marketCap?: number;
  currentPrice?: number;
  market?: string;
  relevanceScore?: number;
}

export interface ChartData {
  date: string;
  actual?: number;
  predicted?: number;
  historicalPrediction?: number;
}

// User Profile Interfaces
export interface UserProfile {
  id: number;
  user_id: string;
  username?: string;
  email?: string;
  investment_style?: 'conservative' | 'moderate' | 'aggressive' | 'growth' | 'value';
  risk_tolerance?: 'low' | 'medium' | 'high';
  investment_experience?: 'beginner' | 'intermediate' | 'advanced' | 'expert';
  preferred_sectors?: any; // JSON
  investment_goals?: string;
  total_portfolio_value?: number;
  created_at: string;
  updated_at: string;
}

export interface UserWatchlist {
  id: number;
  user_id: string;
  symbol: string;
  added_at: string;
  alert_threshold_up?: number;
  alert_threshold_down?: number;
  notes?: string;
  priority?: 'high' | 'medium' | 'low';
}

export interface UserPortfolio {
  id: number;
  user_id: string;
  symbol: string;
  shares: number;
  average_cost: number;
  purchase_date?: string;
  portfolio_weight?: number;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface AiDecisionFactor {
  id: number;
  prediction_id: number;
  factor_type: 'technical' | 'fundamental' | 'sentiment' | 'news' | 'pattern';
  factor_name: string;
  influence_score: number;
  description?: string;
  confidence?: number;
  created_at: string;
}

export interface PredictionContest {
  id: number;
  contest_name: string;
  symbol: string;
  contest_start_date: string;
  prediction_deadline: string;
  target_date: string;
  actual_price?: number;
  status: 'active' | 'closed' | 'completed';
  prize_description?: string;
  created_at: string;
}

export interface UserContestPrediction {
  id: number;
  contest_id: number;
  user_id: string;
  predicted_price: number;
  confidence_level: 'low' | 'medium' | 'high';
  reasoning?: string;
  accuracy_score?: number;
  rank_position?: number;
  submitted_at: string;
}

export interface ThemeInsight {
  id: number;
  theme_name: string;
  theme_category: 'technology' | 'energy' | 'finance' | 'healthcare' | 'consumer' | 'industrial' | 'materials';
  insight_date: string;
  title: string;
  summary: string;
  key_metrics?: any; // JSON
  related_symbols?: any; // JSON
  trend_direction: 'bullish' | 'bearish' | 'neutral';
  impact_score?: number;
  created_at: string;
}

export interface StockDetailsResponse {
  success: boolean;
  stock_info: {
    symbol: string;
    company_name: string;
    latest_price: number;
    price_change: number;
    price_change_percent: number;
    high_52w: number;
    low_52w: number;
  };
  price_history: Array<{
    date: string;
    open: number;
    high: number;
    low: number;
    close: number;
    volume: number;
  }>;
  predictions: Array<{
    prediction_date: string;
    predicted_price: number;
    confidence_score: number;
    prediction_days: number;
    current_price: number;
    model_type: string;
    created_at: string;
  }>;
  timestamp: string;
}