export interface StockPrice {
  date: string;
  close_price: number;
  open_price?: number;
  high_price?: number;
  low_price?: number;
  volume?: number;
}

export interface StockPrediction {
  prediction_date: string;
  predicted_price: number;
  confidence?: number;
  model?: string;
}

export interface HistoricalPrediction {
  prediction_date: string;
  predicted_price: number;
  actual_price?: number;
  error_percentage?: number;
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
  sector?: string;
  industry?: string;
  quoteType?: string;
}

export interface ChartData {
  date: string;
  actual?: number;
  predicted?: number;
  historicalPrediction?: number;
}