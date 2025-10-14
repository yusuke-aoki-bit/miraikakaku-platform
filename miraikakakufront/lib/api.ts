// 本番環境では常にproduction APIを使用
const API_BASE_URL = process.env.NODE_ENV === 'production'
  ? (process.env.NEXT_PUBLIC_API_URL || 'https://miraikakaku-api-465603676610.us-central1.run.app')
  : (process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8080');

export interface StockInfo {
  symbol: string;
  company_name: string;
  exchange: string;
  is_active?: boolean;
}

export interface StockPrice {
  date: string;
  open_price: number | null;
  high_price: number | null;
  low_price: number | null;
  close_price: number | null;
  volume: number | null;
}

export interface StockPrediction {
  prediction_date: string;
  predicted_price: number;
  current_price?: number;
  actual_price?: number;
  prediction_days?: number;
  confidence_score: number;
  model_type: string;
  created_at?: string;
}

export interface PredictionRanking {
  rank: number;
  symbol: string;
  company_name: string;
  predicted_change_percent: number;
  confidence_score: number;
}

export interface SearchResult {
  symbol: string;
  company_name: string;
  exchange: string;
}

export interface MarketSummary {
  total_symbols: number;
  symbols_with_prices: number;
  coverage_percent: number;
}

class APIClient {
  private baseURL: string;

  constructor(baseURL: string = API_BASE_URL) {
    this.baseURL = baseURL;
  }

  private async request<T>(endpoint: string): Promise<T> {
    const url = `${this.baseURL}${endpoint}`;
    console.log('API Request:', url);
    const response = await fetch(url);
    if (!response.ok) {
      throw new Error(`API Error: ${response.statusText}`);
    }
    return response.json();
  }

  async health(): Promise<{ status: string; timestamp: string; version: string }> {
    return this.request('/health');
  }

  async searchStocks(query: string): Promise<{ results: SearchResult[]; count: number }> {
    return this.request(`/api/stocks/search?q=${encodeURIComponent(query)}`);
  }

  async getStockInfo(symbol: string): Promise<{
    symbol: string;
    company_name: string;
    exchange: string;
    price_history: StockPrice[];
  }> {
    return this.request(`/api/stocks/${symbol}`);
  }

  async getPriceHistory(symbol: string, days: number = 30): Promise<StockPrice[]> {
    return this.request(`/api/stocks/${symbol}/price?days=${days}`);
  }

  async getPredictions(
    symbol: string,
    days: number = 365,
    page: number = 1,
    limit: number = 50,
    modelType?: string,
    sort?: string
  ): Promise<{
    symbol: string;
    pagination: {
      page: number;
      limit: number;
      total: number;
      total_pages: number;
    };
    predictions: StockPrediction[];
  }> {
    let url = `/api/stocks/${symbol}/predictions?days=${days}&page=${page}&limit=${limit}`;
    if (modelType) url += `&model_type=${modelType}`;
    if (sort) url += `&sort=${sort}`;
    return this.request(url);
  }

  async getPredictionRankings(limit: number = 10): Promise<{
    rankings: PredictionRanking[];
  }> {
    return this.request(`/api/predictions/rankings?limit=${limit}`);
  }

  async getMarketSummary(): Promise<{ market_summary: MarketSummary }> {
    return this.request('/api/market/summary');
  }

  async getAllPredictions(limit: number = 50): Promise<{
    predictions: (StockPrediction & { symbol: string; company_name: string })[];
    count: number;
  }> {
    return this.request(`/api/predictions?limit=${limit}`);
  }

  async getAllStocks(limit: number = 100, exchange?: string): Promise<{
    stocks: StockInfo[];
    count: number;
  }> {
    const query = exchange ? `?limit=${limit}&exchange=${exchange}` : `?limit=${limit}`;
    return this.request(`/api/stocks${query}`);
  }

  async getPredictionAccuracy(symbol: string, days_back: number = 365): Promise<{
    symbol: string;
    evaluation_available: boolean;
    sample_size?: number;
    evaluation_period_days?: number;
    metrics?: {
      mae: number;
      mape: number;
      direction_accuracy: number;
      std_deviation: number;
      reliability: 'excellent' | 'good' | 'fair' | 'poor';
      reliability_score: number;
    };
    recent_predictions?: any[];
    message?: string;
  }> {
    return this.request(`/api/predictions/accuracy/${symbol}?days_back=${days_back}`);
  }

  async getAccuracyRankings(limit: number = 50): Promise<{
    rankings: Array<{
      symbol: string;
      company_name: string;
      sample_size: number;
      mae: number;
      mape: number;
      direction_accuracy: number;
      reliability: string;
      reliability_score: number;
    }>;
    count: number;
  }> {
    return this.request(`/api/predictions/accuracy/rankings?limit=${limit}`);
  }

  async getModelAccuracySummary(): Promise<{
    evaluated_symbols: number;
    total_predictions: number;
    overall_mae: number;
    overall_mape: number;
    overall_direction_accuracy: number;
    evaluation_period: string;
  }> {
    return this.request('/api/predictions/accuracy/summary');
  }

  // Authentication methods
  async register(email: string, username: string, password: string): Promise<{
    user: {
      id: number;
      email: string;
      username: string;
      created_at: string;
    };
    message: string;
  }> {
    const url = `${this.baseURL}/api/auth/register`;
    const response = await fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, username, password }),
    });
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Registration failed');
    }
    return response.json();
  }

  async login(email: string, password: string): Promise<{
    user: {
      id: number;
      email: string;
      username: string;
    };
    access_token: string;
  }> {
    const url = `${this.baseURL}/api/auth/login`;
    const response = await fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password }),
    });
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Login failed');
    }
    return response.json();
  }

  async getUser(token: string): Promise<{
    id: number;
    email: string;
    username: string;
    created_at: string;
    is_active: boolean;
  }> {
    const url = `${this.baseURL}/api/auth/me`;
    const response = await fetch(url, {
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    });
    if (!response.ok) {
      throw new Error('Failed to get user info');
    }
    return response.json();
  }

  // Watchlist methods
  async getWatchlist(token: string): Promise<Array<{
    id: number;
    symbol: string;
    company_name: string;
    exchange: string;
    added_at: string;
    notes?: string;
    current_price?: number;
    prediction_change?: number;
  }>> {
    const url = `${this.baseURL}/api/watchlist`;
    const response = await fetch(url, {
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    });
    if (!response.ok) {
      throw new Error('Failed to get watchlist');
    }
    return response.json();
  }

  async addToWatchlist(token: string, symbol: string, notes?: string): Promise<{
    message: string;
    id: number;
    symbol: string;
    company_name: string;
    exchange: string;
    added_at: string;
  }> {
    const url = `${this.baseURL}/api/watchlist`;
    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`,
      },
      body: JSON.stringify({ symbol, notes }),
    });
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to add to watchlist');
    }
    return response.json();
  }

  async removeFromWatchlist(token: string, symbol: string): Promise<{
    message: string;
    symbol: string;
  }> {
    const url = `${this.baseURL}/api/watchlist/${symbol}`;
    const response = await fetch(url, {
      method: 'DELETE',
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    });
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to remove from watchlist');
    }
    return response.json();
  }

  async checkInWatchlist(token: string, symbol: string): Promise<{
    symbol: string;
    in_watchlist: boolean;
  }> {
    const url = `${this.baseURL}/api/watchlist/check/${symbol}`;
    const response = await fetch(url, {
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    });
    if (!response.ok) {
      throw new Error('Failed to check watchlist');
    }
    return response.json();
  }

  async getWatchlistCount(token: string): Promise<{ count: number }> {
    const url = `${this.baseURL}/api/watchlist/count`;
    const response = await fetch(url, {
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    });
    if (!response.ok) {
      throw new Error('Failed to get watchlist count');
    }
    return response.json();
  }

  // Home page rankings
  async getTopGainers(limit: number = 10): Promise<{
    gainers: Array<{
      symbol: string;
      company_name: string;
      exchange: string;
      current_price: number;
      previous_price: number;
      change_percent: number;
      price_date: string;
    }>;
    count: number;
    updated_at: string;
  }> {
    const data = await this.request<Array<{symbol: string; name: string; price: number; change: number}>>(`/api/home/rankings/gainers?limit=${limit}`);
    return {
      gainers: data.map(item => ({
        symbol: item.symbol,
        company_name: item.name,
        exchange: (item as any).exchange || '',
        current_price: item.price,
        previous_price: 0,
        change_percent: item.change,
        price_date: new Date().toISOString()
      })),
      count: data.length,
      updated_at: new Date().toISOString()
    };
  }

  async getTopLosers(limit: number = 10): Promise<{
    losers: Array<{
      symbol: string;
      company_name: string;
      exchange: string;
      current_price: number;
      previous_price: number;
      change_percent: number;
      price_date: string;
    }>;
    count: number;
    updated_at: string;
  }> {
    const data = await this.request<Array<{symbol: string; name: string; price: number; change: number}>>(`/api/home/rankings/losers?limit=${limit}`);
    return {
      losers: data.map(item => ({
        symbol: item.symbol,
        company_name: item.name,
        exchange: (item as any).exchange || '',
        current_price: item.price,
        previous_price: 0,
        change_percent: item.change,
        price_date: new Date().toISOString()
      })),
      count: data.length,
      updated_at: new Date().toISOString()
    };
  }

  async getTopVolume(limit: number = 10): Promise<{
    volume_leaders: Array<{
      symbol: string;
      company_name: string;
      exchange: string;
      current_price: number;
      volume: number;
      price_date: string;
    }>;
    count: number;
    updated_at: string;
  }> {
    const data = await this.request<Array<{symbol: string; name: string; price: number; volume: number}>>(`/api/home/rankings/volume?limit=${limit}`);
    return {
      volume_leaders: data.map(item => ({
        symbol: item.symbol,
        company_name: item.name,
        exchange: (item as any).exchange || '',
        current_price: item.price,
        volume: item.volume,
        price_date: new Date().toISOString()
      })),
      count: data.length,
      updated_at: new Date().toISOString()
    };
  }

  async getTopPredictions(limit: number = 10): Promise<{
    top_predictions: Array<{
      symbol: string;
      company_name: string;
      exchange: string;
      current_price: number;
      predicted_price: number;
      confidence_score: number;
      predicted_change: number;
      prediction_date: string;
    }>;
    count: number;
    updated_at: string;
  }> {
    const data = await this.request<Array<{symbol: string; name: string; currentPrice: number; predictedPrice: number; confidence: number; predictedChange: number}>>(`/api/home/rankings/predictions?limit=${limit}`);
    return {
      top_predictions: data.map(item => ({
        symbol: item.symbol,
        company_name: item.name,
        exchange: (item as any).exchange || '',
        current_price: item.currentPrice,
        predicted_price: item.predictedPrice,
        confidence_score: item.confidence,
        predicted_change: item.predictedChange,
        prediction_date: new Date().toISOString()
      })),
      count: data.length,
      updated_at: new Date().toISOString()
    };
  }

  async getMarketSummaryStats(): Promise<{
    total_symbols: number;
    symbols_with_prices: number;
    total_predictions: number;
    last_update: string | null;
    avg_confidence: number;
    coverage_percent: number;
  }> {
    const data = await this.request<{totalSymbols: number; activePredictions: number; avgAccuracy: number; modelsRunning: number}>('/api/home/stats/summary');
    return {
      total_symbols: data.totalSymbols || 0,
      symbols_with_prices: data.activePredictions || 0,
      total_predictions: data.activePredictions || 0,
      last_update: new Date().toISOString(),
      avg_confidence: data.avgAccuracy / 100 || 0,
      coverage_percent: 95.0
    };
  }

  async getFeaturedStocks(limit: number = 6): Promise<{
    featured: Array<{
      symbol: string;
      company_name: string;
      exchange: string;
      current_price: number;
      volume: number;
      predicted_price?: number;
      confidence_score?: number;
      predicted_change?: number;
    }>;
    count: number;
  }> {
    return this.request(`/api/home/featured/stocks?limit=${limit}`);
  }

  // Phase 4-1: Stock Details endpoint
  async getStockDetails(symbol: string): Promise<any> {
    return this.request(`/api/stocks/${symbol}/details`);
  }

  // Phase 4-2: Sector methods
  async getSectors(): Promise<{
    sectors: Array<{
      name: string;
      count: number;
    }>;
    total_sectors: number;
  }> {
    return this.request('/api/rankings/sectors');
  }

  async getSectorRankings(
    sector: string,
    rankingType: 'gainers' | 'losers' | 'volume' | 'predictions' = 'gainers',
    limit: number = 50
  ): Promise<{
    rankings: any[];
    sector: string;
    ranking_type: string;
    count: number;
  }> {
    const encodedSector = encodeURIComponent(sector);
    return this.request(`/api/rankings/sectors/${encodedSector}/${rankingType}?limit=${limit}`);
  }
}

export const apiClient = new APIClient();
