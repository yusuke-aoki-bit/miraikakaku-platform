// 統一APIクライアント

import { API_CONFIG, PAGINATION, TIME_PERIODS } from '@/config/constants';

// User Management Types
interface UserProfile {
  id: string;
  email: string;
  nickname: string;
  avatar_url?: string;
  created_at: string;
  updated_at: string;
}

interface NotificationSettings {
  email: {
    enabled: boolean;
    news_updates: boolean;
    weekly_reports: boolean;
    watchlist_news: boolean;
    security_alerts: boolean;
  };
  push: {
    enabled: boolean;
    price_alerts: boolean;
    ai_signals: boolean;
    volume_alerts: boolean;
    market_hours: boolean;
  };
}

interface LoginHistoryItem {
  id: string;
  ip_address: string;
  location: string;
  device: string;
  browser: string;
  login_time: string;
  is_current: boolean;
}

interface Subscription {
  plan: 'free' | 'pro';
  status: 'active' | 'cancelled' | 'past_due';
  next_billing_date?: string;
  amount?: number;
  currency: string;
}

interface BillingHistory {
  id: string;
  date: string;
  amount: number;
  currency: string;
  status: 'paid' | 'pending' | 'failed';
  invoice_url?: string;
  description: string;
}

interface APIResponse<T = any> {
  success: boolean;
  data?: T;
  error?: string;
  message?: string;
}

// Helper function to ensure array response
function ensureArray<T = any>(data: any): T[] {
  if (Array.isArray(data)) return data;
  if (data && typeof data === 'object' && data.length !== undefined) return Array.from(data);
  return [];
}

// Helper function to check if response has valid array data
function hasArrayData(response: APIResponse<any>): boolean {
  return response.success === true && 
         response.data !== undefined && 
         response.data !== null;
}

class APIClient {
  private baseURL: string;
  private cache: Map<string, { data: any; timestamp: number }>;
  private cacheTimeout: number = 60000; // 1分間のキャッシュ

  constructor() {
    this.baseURL = process.env.NEXT_PUBLIC_API_BASE_URL || API_CONFIG.DEFAULT_BASE_URL;
    this.cache = new Map();
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {},
    useCache: boolean = true
  ): Promise<APIResponse<T>> {
    try {
      // GETリクエストの場合のみキャッシュを使用
      if (useCache && options.method === undefined) {
        const cacheKey = `${endpoint}`;
        const cached = this.cache.get(cacheKey);
        
        if (cached && Date.now() - cached.timestamp < this.cacheTimeout) {
          return {
            success: true,
            data: cached.data,
          };
        }
      }

      const url = `${this.baseURL}${endpoint}`;
      const response = await fetch(url, {
        headers: {
          'Content-Type': 'application/json',
          ...options.headers,
        },
        ...options,
      });

      if (!response.ok) {
        return {
          success: false,
          error: `HTTP ${response.status}: ${response.statusText}`,
        };
      }

      const data = await response.json();
      
      // 成功したGETリクエストをキャッシュに保存
      if (useCache && options.method === undefined) {
        const cacheKey = `${endpoint}`;
        this.cache.set(cacheKey, {
          data,
          timestamp: Date.now(),
        });
        
        // キャッシュサイズ制限（最大100エントリ）
        if (this.cache.size > 100) {
          const firstKey = this.cache.keys().next().value;
          if (firstKey) {
            this.cache.delete(firstKey);
          }
        }
      }
      
      return {
        success: true,
        data,
      };
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : '不明なエラー',
      };
    }
  }

  // Enhanced stock search - align with production API
  async searchStocksBasic(query: string, limit: number = PAGINATION.DEFAULT_PAGE_SIZE) {
    const url = `/api/finance/stocks/search?query=${encodeURIComponent(query)}&limit=${limit}`;
    return this.request(url);
  }

  // 株価履歴取得 - production API uses 'limit' not 'days'
  async getStockPrice(symbol: string, limit: number = TIME_PERIODS.DEFAULT_PRICE_HISTORY_DAYS) {
    return this.request(`/api/finance/stocks/${symbol}/price?limit=${limit}`);
  }

  // 株価予測取得 - production API uses 'limit' and 'model_version' not 'model_type'
  async getStockPredictions(symbol: string, modelVersion?: string, limit: number = TIME_PERIODS.DEFAULT_PREDICTION_DAYS) {
    let url = `/api/finance/stocks/${symbol}/predictions?limit=${limit}`;
    if (modelVersion) {
      url += `&model_version=${encodeURIComponent(modelVersion)}`;
    }
    return this.request(url);
  }

  // 予測生成
  async createPrediction(symbol: string) {
    return this.request(`/api/finance/stocks/${symbol}/predict`, {
      method: 'POST',
    });
  }

  // AI決定要因取得 - production API endpoint
  async getAIFactors(limit: number = PAGINATION.DEFAULT_PAGE_SIZE, offset: number = 0) {
    return this.request(`/api/ai-factors/all?limit=${limit}&offset=${offset}`);
  }


  // 特定テーマの洞察取得 - production API endpoint
  async getThemeInsightByName(themeName: string, limit: number = PAGINATION.DEFAULT_PAGE_SIZE) {
    return this.request(`/api/insights/themes/${encodeURIComponent(themeName)}?limit=${limit}`);
  }


  // 成長ポテンシャルランキング - use universal rankings API
  async getGrowthPotentialRankings(limit: number = PAGINATION.RANKING_LIMIT) {
    const endpoint = `/api/finance/rankings/universal?ranking_type=growth-potential&limit=${limit}`;
    return this.request(endpoint, {
      method: 'GET'
    });
  }


  // 精度ランキング - use universal rankings API
  async getAccuracyRankings(limit: number = PAGINATION.RANKING_LIMIT) {
    const endpoint = `/api/finance/rankings/universal?ranking_type=accuracy&limit=${limit}`;
    return this.request(endpoint, {
      method: 'GET'
    });
  }

  // 株式詳細情報取得（株価と予測を組み合わせ）
  async getStockDetails(symbol: string) {
    try {
      const [priceResponse, predictionResponse] = await Promise.all([
        this.getStockPrice(symbol, 30),
        this.getStockPredictions(symbol, undefined, 10)
      ]);
      
      return {
        success: true,
        data: {
          symbol,
          prices: priceResponse.success ? priceResponse.data : [],
          predictions: predictionResponse.success ? predictionResponse.data : []
        }
      };
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : '株式詳細取得エラー'
      };
    }
  }

  // マーケット概況（トレンド株）
  async getTrendingStocks(limit: number = PAGINATION.RANKING_LIMIT) {
    const endpoint = `/api/finance/rankings/universal?limit=${limit}`;
    return this.request(endpoint, {
      method: 'GET'
    });
  }




  // 出来高データ取得 - 実装済みエンドポイント
  async getVolumeData(symbol: string, limit: number = TIME_PERIODS.DEFAULT_PRICE_HISTORY_DAYS) {
    return this.request(`/api/finance/stocks/${symbol}/volume?limit=${limit}`);
  }

  // 出来高予測 - 実装済みエンドポイント
  async getVolumePredictions(symbol: string, days: number = 7) {
    return this.request(`/api/finance/stocks/${symbol}/volume-predictions?days=${days}`);
  }

  // 出来高ランキング - 実装済みエンドポイント
  async getVolumeRankings(limit: number = PAGINATION.RANKING_LIMIT) {
    return this.request(`/api/finance/volume-rankings?limit=${limit}`);
  }

  // 為替・通貨関連API - 実装済み
  async getCurrencyPairs() {
    return this.request('/api/forex/currency-pairs');
  }

  async getCurrencyRate(pair: string) {
    return this.request(`/api/forex/currency-rate/${encodeURIComponent(pair)}`);
  }

  async getCurrencyHistory(pair: string, days: number = 30) {
    return this.request(`/api/forex/currency-history/${encodeURIComponent(pair)}?days=${days}`);
  }

  async getCurrencyPredictions(pair: string, timeframe: string = '1D', limit: number = 7) {
    return this.request(`/api/forex/currency-predictions/${encodeURIComponent(pair)}?timeframe=${timeframe}&limit=${limit}`);
  }

  async getCurrencyInsights(pair: string) {
    return this.request(`/api/forex/currency-insights/${encodeURIComponent(pair)}`);
  }

  async getEconomicCalendar(date?: string, country?: string) {
    let url = '/api/forex/economic-calendar';
    const params = [];
    if (date) params.push(`date=${date}`);
    if (country) params.push(`country=${country}`);
    if (params.length > 0) url += '?' + params.join('&');
    return this.request(url);
  }

  // 過去の予測データ取得（履歴）
  async getHistoricalPredictions(symbol: string, limit: number = 30) {
    return this.request(`/api/finance/stocks/${symbol}/predictions/history?limit=${limit}`);
  }



  // 高度な検索（フィルター付き）- 既存のエンドポイントを使用
  async searchStocksAdvanced(query: string = '', filters: any = {}) {
    const params = new URLSearchParams();
    if (query) params.append('query', query);
    
    // 基本的なパラメータのみ追加（既存APIに合わせる）
    if (filters.limit) params.append('limit', filters.limit.toString());
    
    const url = `/api/finance/stocks/search?${params.toString()}`;
    
    // 既存のAPIレスポンスを拡張フォーマットに変換
    const response = await this.request(url);
    if (response.success && response.data && Array.isArray(response.data)) {
      // データを拡張フォーマットに変換
      const enhancedData = response.data.map((stock: any) => ({
        ...stock,
        market: stock.exchange || '不明',
        current_price: stock.current_price || 0,
        change_percent: stock.change_percent || 0,
        ai_score: stock.ai_score || 0,
        market_cap: stock.market_cap || 0,
        per: stock.per || 0,
        pbr: stock.pbr || 0,
        dividend_yield: stock.dividend_yield || 0
      }));
      
      // フィルター適用（フロントエンドサイド）
      let filteredData = enhancedData;
      
      if (filters.markets && filters.markets.length > 0) {
        filteredData = filteredData.filter((stock: any) => {
          return filters.markets.some((market: string) => {
            if (market === 'jp') return stock.exchange?.includes('TSE') || stock.exchange?.includes('TYO');
            if (market === 'us') return stock.exchange?.includes('NASDAQ') || stock.exchange?.includes('NYSE');
            return true;
          });
        });
      }
      
      if (filters.sectors && filters.sectors.length > 0) {
        filteredData = filteredData.filter((stock: any) => 
          filters.sectors.includes(stock.sector?.toLowerCase())
        );
      }
      
      if (filters.aiScoreMin !== undefined) {
        filteredData = filteredData.filter((stock: any) => stock.ai_score >= filters.aiScoreMin);
      }
      
      if (filters.aiScoreMax !== undefined) {
        filteredData = filteredData.filter((stock: any) => stock.ai_score <= filters.aiScoreMax);
      }
      
      return {
        success: true,
        data: filteredData.slice(0, filters.limit || 20)
      };
    }
    
    return response;
  }

  // オートコンプリート検索 - 既存の検索エンドポイントを使用
  async searchStocksAutocomplete(query: string, limit: number = 10) {
    const response = await this.request(`/api/finance/stocks/search?query=${encodeURIComponent(query)}&limit=${limit}`);
    
    if (response.success && response.data && Array.isArray(response.data)) {
      // オートコンプリート形式に変換
      const suggestions = response.data.map((stock: any) => ({
        symbol: stock.symbol,
        company_name: stock.company_name || stock.symbol,
        market: stock.exchange || '不明',
        current_price: stock.current_price || 0,
        change_percent: stock.change_percent || 0
      }));
      
      return {
        success: true,
        data: suggestions
      };
    }
    
    return response;
  }

  // バッチチャートデータ取得 - 個別APIを並列呼び出し
  async getBatchStockChartData(symbols: string[], chartTypes: string[] = ['price', 'prediction']) {
    try {
      const results = await Promise.all(
        symbols.map(async (symbol) => {
          const [priceData, predictionData] = await Promise.all([
            chartTypes.includes('price') ? this.getStockPrice(symbol, 30) : null,
            chartTypes.includes('prediction') ? this.getStockPredictions(symbol) : null
          ]);
          return { symbol, priceData, predictionData };
        })
      );
      
      const data: { [key: string]: any } = {};
      results.forEach(({ symbol, priceData, predictionData }) => {
        data[symbol] = {
          historical: priceData?.data || [],
          future_prediction: predictionData?.data || []
        };
      });
      
      return {
        success: true,
        data
      };
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Batch data fetch failed'
      };
    }
  }

  // 財務指標データ取得 - indicators APIを使用
  async getStockFinancials(symbol: string) {
    return this.request(`/api/finance/stocks/${symbol}/indicators`);
  }

  // バッチ財務指標データ取得 - 個別APIを並列呼び出し
  async getBatchStockFinancials(symbols: string[]) {
    try {
      const results = await Promise.all(
        symbols.map(symbol => this.getStockFinancials(symbol))
      );
      
      const data: { [key: string]: any } = {};
      results.forEach((result, index) => {
        if (result.success) {
          data[symbols[index]] = result.data;
        }
      });
      
      return {
        success: true,
        data
      };
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Batch financials fetch failed'
      };
    }
  }

  // セクター関連のAPI追加
  
  // セクター履歴パフォーマンス取得
  async getSectorHistoricalPerformance(sectorId: string, period: string = '1Y') {
    // Use sector details API 
    return this.request(`/api/sectors/${sectorId}?period=${period}`);
  }

  // AIセクター見通し取得
  async getAISectorOutlook(sectorId: string) {
    // Use insights themes API as fallback
    return this.request(`/api/insights/themes?sector=${sectorId}`);
  }

  // セクター用に拡張されたgetSectors
  async getSectorsWithPerformance() {
    // Just use the regular sectors API
    return this.getSectors();
  }

  // AIモデル パフォーマンス取得
  async getModelPerformance(symbol: string) {
    return this.request(`/api/ai-factors/symbol/${symbol}`);
  }

  // AI出来高インサイト取得
  async getAIVolumeInsights(symbol: string) {
    return this.request(`/api/finance/stocks/${symbol}/volume-predictions`);
  }

  // ウォッチリスト関連API
  async getWatchlist(userId?: string) {
    return this.request(`/api/user/watchlist`);
  }

  async addToWatchlist(symbol: string, userId?: string) {
    return this.request(`/api/user/watchlist`, {
      method: 'POST',
      body: JSON.stringify({ symbol })
    });
  }

  async removeFromWatchlist(symbol: string, userId?: string) {
    return this.request(`/api/user/watchlist/${encodeURIComponent(symbol)}`, {
      method: 'DELETE'
    });
  }

  async getBatchStockDetails(symbols: string[]) {
    if (symbols.length === 0) {
      return {
        success: true,
        data: {}
      };
    }

    try {
      // 並列でデータを取得（効率化）
      const batchPromises = symbols.map(async (symbol) => {
        const [priceResponse, predictionResponse, financialResponse] = await Promise.all([
          this.getStockPrice(symbol, 30),
          this.getStockPredictions(symbol, undefined, 10),
          this.getStockFinancials(symbol)
        ]);

        let stockData: any = {
          symbol,
          error: null,
          prices: [],
          predictions: [],
          financials: {}
        };

        if (priceResponse.success) {
          stockData.prices = priceResponse.data || [];
          if (stockData.prices.length > 0) {
            const latest = stockData.prices[stockData.prices.length - 1];
            stockData.current_price = latest.close_price;
            stockData.change_percent = latest.change_percent || 0;
            stockData.volume = latest.volume;
            stockData.last_updated = latest.timestamp;
          }
        }

        if (predictionResponse.success) {
          stockData.predictions = predictionResponse.data || [];
          if (stockData.predictions.length > 0) {
            stockData.ai_score = Math.round(stockData.predictions[0].confidence_score * 100);
            stockData.prediction_trend = stockData.predictions[0].predicted_price > stockData.current_price ? 'up' : 'down';
          }
        }

        if (financialResponse.success) {
          stockData.financials = financialResponse.data || {};
          stockData.market_cap = stockData.financials.market_cap;
          stockData.per = stockData.financials.per;
          stockData.pbr = stockData.financials.pbr;
          stockData.dividend_yield = stockData.financials.dividend_yield;
        }

        // 会社名を設定（模擬データ）
        const companyNames: { [key: string]: string } = {
          'AAPL': 'Apple Inc.',
          'GOOGL': 'Alphabet Inc.',
          'MSFT': 'Microsoft Corporation',
          'TSLA': 'Tesla, Inc.',
          'AMZN': 'Amazon.com Inc.',
          'NVDA': 'NVIDIA Corporation',
          'META': 'Meta Platforms Inc.',
          '7203': 'トヨタ自動車',
          '6758': 'ソニーグループ',
          '9984': 'ソフトバンクグループ'
        };
        stockData.company_name = companyNames[symbol] || symbol;

        return stockData;
      });

      const results = await Promise.all(batchPromises);
      
      // シンボルをキーとしたオブジェクトに変換
      const batchData: { [key: string]: any } = {};
      results.forEach(stock => {
        batchData[stock.symbol] = stock;
      });

      return {
        success: true,
        data: batchData
      };
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'バッチデータ取得エラー'
      };
    }
  }

  // ウォッチリストの並び順を保存
  async updateWatchlistOrder(symbols: string[], userId?: string) {
    if (!userId) {
      localStorage.setItem('watchlist', JSON.stringify(symbols));
      return {
        success: true,
        data: { order_updated: true }
      };
    }
    return this.request(`/api/users/${userId}/watchlist/order`, {
      method: 'PUT',
      body: JSON.stringify({ symbols })
    }, false);
  }

  // ヘルスチェック
  async healthCheck() {
    return this.request('/health', {}, false); // ヘルスチェックはキャッシュしない
  }
  
  // User Management API Methods
  
  // プロフィール取得
  async getUserProfile(): Promise<APIResponse<UserProfile>> {
    return this.request('/api/user/profile');
  }

  // プロフィール更新
  async updateUserProfile(data: Partial<UserProfile>): Promise<APIResponse<UserProfile>> {
    return this.request('/api/user/profile', {
      method: 'PUT',
      body: JSON.stringify(data)
    }, false);
  }

  // アバター画像アップロード
  async uploadAvatar(file: File): Promise<APIResponse<{ avatar_url: string }>> {
    const formData = new FormData();
    formData.append('avatar', file);
    
    return this.request('/api/user/avatar', {
      method: 'POST',
      body: formData,
      headers: {} // Content-Typeを自動設定させる
    }, false);
  }

  // メールアドレス変更
  async changeEmail(newEmail: string, password: string): Promise<APIResponse<{ email: string }>> {
    return this.request('/api/user/email', {
      method: 'PUT',
      body: JSON.stringify({
        new_email: newEmail,
        password: password
      })
    }, false);
  }

  // パスワード変更
  async changePassword(currentPassword: string, newPassword: string): Promise<APIResponse<void>> {
    return this.request('/api/user/password', {
      method: 'PUT',
      body: JSON.stringify({
        current_password: currentPassword,
        new_password: newPassword
      })
    }, false);
  }

  // 二要素認証有効化
  async enable2FA(): Promise<APIResponse<{ qr_code: string; backup_codes: string[] }>> {
    return this.request('/api/user/2fa/enable', {
      method: 'POST'
    }, false);
  }

  // 二要素認証確認
  async verify2FA(code: string): Promise<APIResponse<{ enabled: boolean }>> {
    return this.request('/api/user/2fa/verify', {
      method: 'POST',
      body: JSON.stringify({ code })
    }, false);
  }

  // 二要素認証無効化
  async disable2FA(): Promise<APIResponse<{ disabled: boolean }>> {
    return this.request('/api/user/2fa/disable', {
      method: 'POST'
    }, false);
  }

  // ログイン履歴取得
  async getLoginHistory(): Promise<APIResponse<LoginHistoryItem[]>> {
    return this.request('/api/user/login-history');
  }

  // 通知設定取得
  async getNotificationSettings(): Promise<APIResponse<NotificationSettings>> {
    return this.request('/api/user/notifications');
  }

  // 通知設定更新
  async updateNotificationSettings(settings: NotificationSettings): Promise<APIResponse<NotificationSettings>> {
    return this.request('/api/user/notifications', {
      method: 'PUT',
      body: JSON.stringify(settings)
    }, false);
  }

  // サブスクリプション情報取得
  async getSubscriptionPlan(): Promise<APIResponse<Subscription>> {
    return this.request('/api/user/subscription');
  }

  // プロプランにアップグレード
  async upgradeToProPlan(): Promise<APIResponse<{ checkout_url: string }>> {
    return this.request('/api/user/upgrade', {
      method: 'POST'
    }, false);
  }

  // 請求履歴取得
  async getBillingHistory(): Promise<APIResponse<BillingHistory[]>> {
    return this.request('/api/user/billing-history');
  }

  // Stripe顧客ポータルURL取得
  async getBillingPortalUrl(): Promise<APIResponse<{ portal_url: string }>> {
    return this.request('/api/user/billing-portal', {
      method: 'POST'
    }, false);
  }

  // アカウント削除
  async deleteAccount(password: string, confirmation: string): Promise<APIResponse<{ deleted: boolean }>> {
    return this.request('/api/user/delete', {
      method: 'DELETE',
      body: JSON.stringify({
        password,
        confirmation
      })
    }, false);
  }

  // ゲストデータ移行
  async migrateGuestData(watchlist: any[], settings: any): Promise<APIResponse<{ migrated: boolean }>> {
    return this.request('/api/user/migrate-guest-data', {
      method: 'POST',
      body: JSON.stringify({
        watchlist,
        settings
      })
    }, false);
  }

  // Portfolio Management API Methods

  // ポートフォリオ一覧取得
  async listPortfolios(): Promise<APIResponse<any[]>> {
    return this.request('/api/portfolios');
  }

  // ポートフォリオ作成
  async createPortfolio(name: string): Promise<APIResponse<any>> {
    return this.request('/api/portfolios', {
      method: 'POST',
      body: JSON.stringify({ name })
    }, false);
  }

  // ポートフォリオ詳細取得
  async getPortfolio(portfolioId: string): Promise<APIResponse<any>> {
    return this.request(`/api/portfolios/${portfolioId}`);
  }

  // ポートフォリオ更新
  async updatePortfolio(portfolioId: string, data: any): Promise<APIResponse<any>> {
    return this.request(`/api/portfolios/${portfolioId}`, {
      method: 'PUT',
      body: JSON.stringify(data)
    }, false);
  }

  // ポートフォリオ削除
  async deletePortfolio(portfolioId: string): Promise<APIResponse<{ deleted: boolean }>> {
    return this.request(`/api/portfolios/${portfolioId}`, {
      method: 'DELETE'
    }, false);
  }

  // 取引追加
  async addTransaction(portfolioId: string, transactionData: {
    type: 'buy' | 'sell';
    symbol: string;
    quantity: number;
    price: number;
    date: string;
    fees?: number;
  }): Promise<APIResponse<any>> {
    return this.request(`/api/portfolios/${portfolioId}/transactions`, {
      method: 'POST',
      body: JSON.stringify(transactionData)
    }, false);
  }

  // 取引履歴取得
  async getTransactionHistory(portfolioId: string, symbol?: string): Promise<APIResponse<any[]>> {
    const endpoint = symbol 
      ? `/api/portfolios/${portfolioId}/transactions?symbol=${encodeURIComponent(symbol)}`
      : `/api/portfolios/${portfolioId}/transactions`;
    return this.request(endpoint);
  }

  // 取引更新
  async updateTransaction(portfolioId: string, transactionId: string, data: any): Promise<APIResponse<any>> {
    return this.request(`/api/portfolios/${portfolioId}/transactions/${transactionId}`, {
      method: 'PUT',
      body: JSON.stringify(data)
    }, false);
  }

  // 取引削除
  async deleteTransaction(portfolioId: string, transactionId: string): Promise<APIResponse<{ deleted: boolean }>> {
    return this.request(`/api/portfolios/${portfolioId}/transactions/${transactionId}`, {
      method: 'DELETE'
    }, false);
  }

  // ポートフォリオパフォーマンス履歴取得
  async getPortfolioPerformanceHistory(portfolioId: string, period: string = '6M'): Promise<APIResponse<any[]>> {
    return this.request(`/api/portfolios/${portfolioId}/performance?period=${period}`);
  }

  // ポートフォリオサマリー取得
  async getPortfolioSummary(portfolioId?: string): Promise<APIResponse<any>> {
    if (portfolioId) {
      return this.request(`/api/portfolios/${portfolioId}/summary`);
    } else {
      return this.request('/api/portfolios/summary');
    }
  }

  // 保有銘柄一覧取得
  async getPortfolioHoldings(portfolioId: string): Promise<APIResponse<any[]>> {
    return this.request(`/api/portfolios/${portfolioId}/holdings`);
  }

  // ポートフォリオ分析取得
  async getPortfolioAnalysis(portfolioId: string): Promise<APIResponse<{
    risk_metrics: any;
    diversification_score: number;
    sector_allocation: any[];
    recommendations: string[];
  }>> {
    return this.request(`/api/portfolios/${portfolioId}/analysis`);
  }

  // ポートフォリオリバランス提案取得
  async getRebalanceRecommendations(portfolioId: string, targetAllocation?: any): Promise<APIResponse<{
    current_allocation: any[];
    target_allocation: any[];
    rebalance_actions: any[];
  }>> {
    const body = targetAllocation ? JSON.stringify({ target_allocation: targetAllocation }) : undefined;
    return this.request(`/api/portfolios/${portfolioId}/rebalance`, {
      method: 'POST',
      body
    }, false);
  }

  // ポートフォリオベンチマーク比較
  async compareWithBenchmark(portfolioId: string, benchmarkId: string, period: string = '1Y'): Promise<APIResponse<{
    portfolio_return: number;
    benchmark_return: number;
    alpha: number;
    beta: number;
    sharpe_ratio: number;
    performance_data: any[];
  }>> {
    return this.request(`/api/portfolios/${portfolioId}/benchmark/${benchmarkId}?period=${period}`);
  }

  // 保有銘柄更新（数量・平均取得価格の手動調整）
  async updateHolding(portfolioId: string, symbol: string, data: {
    quantity?: number;
    average_cost?: number;
  }): Promise<APIResponse<any>> {
    return this.request(`/api/portfolios/${portfolioId}/holdings/${encodeURIComponent(symbol)}`, {
      method: 'PUT',
      body: JSON.stringify(data)
    }, false);
  }

  // 保有銘柄削除
  async deleteHolding(portfolioId: string, symbol: string): Promise<APIResponse<{ deleted: boolean }>> {
    return this.request(`/api/portfolios/${portfolioId}/holdings/${encodeURIComponent(symbol)}`, {
      method: 'DELETE'
    }, false);
  }

  // Market Index API Methods - for Home screen
  async getMarketIndices(): Promise<APIResponse<any[]>> {
    return this.request('/api/market/indices', {
      method: 'GET'
    });
  }

  async getFeaturedPredictions(limit: number = 3): Promise<APIResponse<any[]>> {
    return this.request(`/api/predictions/featured?limit=${limit}`, {
      method: 'GET'
    });
  }

  // Rankings API Methods - Complete set
  async getGainersRankings(params?: {
    market?: string;
    sector?: string;
    market_cap?: string;
    period?: string;
    limit?: number;
  }): Promise<APIResponse<any[]>> {
    const queryParams = new URLSearchParams();
    if (params?.market) queryParams.append('market', params.market);
    if (params?.sector) queryParams.append('sector', params.sector);
    if (params?.market_cap) queryParams.append('market_cap', params.market_cap);
    if (params?.period) queryParams.append('period', params.period);
    if (params?.limit) queryParams.append('limit', params.limit.toString());

    const endpoint = `/api/finance/rankings/universal${queryParams.toString() ? `?${queryParams.toString()}` : ''}`;
    return this.request(endpoint, {
      method: 'GET'
    });
  }

  async getLosersRankings(params?: {
    market?: string;
    sector?: string;
    market_cap?: string;
    period?: string;
    limit?: number;
  }): Promise<APIResponse<any[]>> {
    const queryParams = new URLSearchParams();
    if (params?.market) queryParams.append('market', params.market);
    if (params?.sector) queryParams.append('sector', params.sector);
    if (params?.market_cap) queryParams.append('market_cap', params.market_cap);
    if (params?.period) queryParams.append('period', params.period);
    if (params?.limit) queryParams.append('limit', params.limit.toString());

    const endpoint = `/api/finance/rankings/universal${queryParams.toString() ? `?${queryParams.toString()}` : ''}`;
    return this.request(endpoint, {
      method: 'GET'
    });
  }

  async getCompositeRankings(params?: {
    ranking_type?: string;
    market?: string;
    sector?: string;
    market_cap?: string;
    period?: string;
    limit?: number;
  }): Promise<APIResponse<any[]>> {
    const queryParams = new URLSearchParams();
    if (params?.ranking_type) queryParams.append('ranking_type', params.ranking_type);
    if (params?.market) queryParams.append('market', params.market);
    if (params?.sector) queryParams.append('sector', params.sector);
    if (params?.market_cap) queryParams.append('market_cap', params.market_cap);
    if (params?.period) queryParams.append('period', params.period);
    if (params?.limit) queryParams.append('limit', params.limit.toString());

    const endpoint = `/api/finance/rankings/universal${queryParams.toString() ? `?${queryParams.toString()}` : ''}`;
    return this.request(endpoint, {
      method: 'GET'
    });
  }

  // Enhanced Search API Methods - with filter support
  async searchStocks(params: {
    query?: string;
    market?: string;
    sector?: string;
    market_cap_min?: number;
    market_cap_max?: number;
    per_min?: number;
    per_max?: number;
    pbr_min?: number;
    pbr_max?: number;
    ai_score_min?: number;
    ai_score_max?: number;
    dividend_yield_min?: number;
    dividend_yield_max?: number;
    limit?: number;
    offset?: number;
  }): Promise<APIResponse<any[]>> {
    const queryParams = new URLSearchParams();
    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined && value !== null && value !== '') {
        queryParams.append(key, value.toString());
      }
    });

    const endpoint = `/api/stocks/search${queryParams.toString() ? `?${queryParams.toString()}` : ''}`;
    return this.request(endpoint, {
      method: 'GET'
    });
  }

  // Sectors API Methods - Complete specification compliance
  async getSectors(): Promise<APIResponse<any[]>> {
    return this.request('/api/sectors', {
      method: 'GET'
    });
  }

  async getStocksBySector(sectorId: string, params?: {
    limit?: number;
    sort_by?: string;
    sort_order?: 'asc' | 'desc';
  }): Promise<APIResponse<any[]>> {
    const queryParams = new URLSearchParams();
    if (params?.limit) queryParams.append('limit', params.limit.toString());
    if (params?.sort_by) queryParams.append('sort_by', params.sort_by);
    if (params?.sort_order) queryParams.append('sort_order', params.sort_order);

    const endpoint = `/api/sectors/${sectorId}/stocks${queryParams.toString() ? `?${queryParams.toString()}` : ''}`;
    return this.request(endpoint, {
      method: 'GET'
    });
  }

  // News API Methods
  async getNewsArticle(articleId: string): Promise<APIResponse<any>> {
    return this.request(`/api/news/${articleId}`, {
      method: 'GET'
    });
  }

  async getRelatedNews(articleId: string, limit: number = 5): Promise<APIResponse<any[]>> {
    return this.request(`/api/news/${articleId}/related?limit=${limit}`, {
      method: 'GET'
    });
  }

  async getNewsArticles(params?: {
    category?: string;
    source?: string;
    limit?: number;
    offset?: number;
  }): Promise<APIResponse<any[]>> {
    const queryParams = new URLSearchParams();
    if (params?.category) queryParams.append('category', params.category);
    if (params?.source) queryParams.append('source', params.source);
    if (params?.limit) queryParams.append('limit', params.limit.toString());
    if (params?.offset) queryParams.append('offset', params.offset.toString());

    const endpoint = `/api/news${queryParams.toString() ? `?${queryParams.toString()}` : ''}`;
    return this.request(endpoint, {
      method: 'GET'
    });
  }

  // キャッシュクリア
  // Password Reset API Methods
  async sendPasswordResetLink(email: string): Promise<APIResponse<any>> {
    return this.request('/api/auth/password-reset/request', {
      method: 'POST',
      body: JSON.stringify({ email })
    }, false);
  }

  async validatePasswordResetToken(token: string): Promise<APIResponse<any>> {
    return this.request(`/api/auth/password-reset/validate/${token}`, {
      method: 'GET'
    }, false);
  }

  async resetPassword(token: string, newPassword: string): Promise<APIResponse<any>> {
    return this.request('/api/auth/password-reset/confirm', {
      method: 'POST',
      body: JSON.stringify({ 
        token, 
        new_password: newPassword 
      })
    }, false);
  }

  // AI Decision Factors API Methods
  async getAIDecisionFactors(predictionId: string): Promise<APIResponse<any>> {
    return this.request(`/api/predictions/${predictionId}/factors`, {
      method: 'GET'
    });
  }

  async getAllAIFactors(): Promise<APIResponse<any[]>> {
    return this.request('/api/ai-factors/all', {
      method: 'GET'
    });
  }

  async getAIFactorsBySymbol(symbol: string): Promise<APIResponse<any[]>> {
    return this.request(`/api/ai-factors/symbol/${symbol}`, {
      method: 'GET'
    });
  }

  async getEnhancedPredictions(symbol: string, params?: {
    days?: number;
    model_type?: string;
    include_factors?: boolean;
  }): Promise<APIResponse<any[]>> {
    const queryParams = new URLSearchParams();
    if (params?.days) queryParams.append('days', params.days.toString());
    if (params?.model_type) queryParams.append('model_type', params.model_type);
    if (params?.include_factors) queryParams.append('include_factors', 'true');

    const endpoint = `/api/stocks/${symbol}/predictions/enhanced${queryParams.toString() ? `?${queryParams.toString()}` : ''}`;
    return this.request(endpoint, {
      method: 'GET'
    });
  }

  // Theme Insights API Methods
  async getThemeInsights(): Promise<APIResponse<string[]>> {
    return this.request('/api/insights/themes', {
      method: 'GET'
    });
  }

  async getThemeInsightsByName(themeName: string): Promise<APIResponse<any[]>> {
    return this.request(`/api/insights/themes/${themeName}`, {
      method: 'GET'
    });
  }

  // Themes API - Extended Methods
  async getThemes(): Promise<APIResponse<any[]>> {
    return this.request('/api/insights/themes', {
      method: 'GET'
    });
  }

  async getThemeDetails(themeId: string): Promise<APIResponse<any>> {
    return this.request(`/api/insights/themes/${themeId}`, {
      method: 'GET'
    });
  }

  async getThemeNews(themeId: string): Promise<APIResponse<any[]>> {
    return this.request(`/api/insights/themes/${themeId}/news`, {
      method: 'GET'
    });
  }

  async getThemeAIInsights(themeId: string): Promise<APIResponse<any[]>> {
    return this.request(`/api/insights/themes/${themeId}/ai-insights`, {
      method: 'GET'
    });
  }

  async followTheme(themeId: string): Promise<APIResponse<any>> {
    return this.request(`/api/insights/themes/${themeId}/follow`, {
      method: 'POST'
    }, false);
  }

  async unfollowTheme(themeId: string): Promise<APIResponse<any>> {
    return this.request(`/api/insights/themes/${themeId}/follow`, {
      method: 'DELETE'
    }, false);
  }

  async getAllInsights(): Promise<APIResponse<any[]>> {
    return this.request('/api/insights/all', {
      method: 'GET'
    });
  }

  async getLatestInsights(): Promise<APIResponse<any[]>> {
    return this.request('/api/insights/latest', {
      method: 'GET'
    });
  }

  async getInsightsByCategory(category: string): Promise<APIResponse<any[]>> {
    return this.request(`/api/insights/categories/${category}`, {
      method: 'GET'
    });
  }

  // Contests API Methods
  async getContestStats(): Promise<APIResponse<any>> {
    return this.request('/api/contests/stats', {
      method: 'GET'
    });
  }

  async getActiveContests(): Promise<APIResponse<any[]>> {
    return this.request('/api/contests/active', {
      method: 'GET'
    });
  }

  async getPastContests(): Promise<APIResponse<any[]>> {
    return this.request('/api/contests/past', {
      method: 'GET'
    });
  }

  async getLeaderboard(timeFrame: string = 'all_time'): Promise<APIResponse<any[]>> {
    return this.request(`/api/contests/leaderboard?time_frame=${timeFrame}`, {
      method: 'GET'
    });
  }

  async getContestDetails(contestId: string): Promise<APIResponse<any>> {
    return this.request(`/api/contests/${contestId}`, {
      method: 'GET'
    });
  }

  async getContestRanking(contestId: string): Promise<APIResponse<any[]>> {
    return this.request(`/api/contests/${contestId}/ranking`, {
      method: 'GET'
    });
  }

  async submitPrediction(contestId: string, prediction: number, confidence?: number): Promise<APIResponse<any>> {
    return this.request(`/api/contests/${contestId}/predict`, {
      method: 'POST',
      body: JSON.stringify({ 
        prediction,
        confidence 
      })
    }, false);
  }

  async updatePrediction(contestId: string, prediction: number, confidence?: number): Promise<APIResponse<any>> {
    return this.request(`/api/contests/${contestId}/predict`, {
      method: 'PUT',
      body: JSON.stringify({ 
        prediction,
        confidence 
      })
    }, false);
  }

  async getUserContestHistory(userId?: string): Promise<APIResponse<any[]>> {
    const endpoint = userId ? `/api/users/${userId}/contests` : '/api/user/contests';
    return this.request(endpoint, {
      method: 'GET'
    });
  }

  async getUserById(userId: string): Promise<APIResponse<any>> {
    return this.request(`/api/users/${userId}`, {
      method: 'GET'
    });
  }

  async getUserBadges(userId: string): Promise<APIResponse<any[]>> {
    return this.request(`/api/users/${userId}/badges`, {
      method: 'GET'
    });
  }

  async getUserRankingHistory(userId: string): Promise<APIResponse<any[]>> {
    return this.request(`/api/users/${userId}/ranking-history`, {
      method: 'GET'
    });
  }

  // News API Methods
  async getNews(params?: {
    category?: string;
    search?: string;
    sort?: string;
    page?: number;
    limit?: number;
  }): Promise<APIResponse<any[]>> {
    const queryParams = new URLSearchParams();
    if (params?.category && params.category !== 'all') queryParams.append('category', params.category);
    if (params?.search) queryParams.append('search', params.search);
    if (params?.sort) queryParams.append('sort', params.sort);
    if (params?.page) queryParams.append('page', params.page.toString());
    if (params?.limit) queryParams.append('limit', params.limit.toString());

    const endpoint = `/api/news${queryParams.toString() ? `?${queryParams.toString()}` : ''}`;
    return this.request(endpoint, {
      method: 'GET'
    });
  }

  async getNewsDetails(newsId: string): Promise<APIResponse<any>> {
    return this.request(`/api/news/${newsId}`, {
      method: 'GET'
    });
  }

  async toggleNewsBookmark(newsId: string): Promise<APIResponse<any>> {
    return this.request(`/api/news/${newsId}/bookmark`, {
      method: 'POST'
    }, false);
  }

  async getBookmarkedNews(): Promise<APIResponse<any[]>> {
    return this.request('/api/news/bookmarked', {
      method: 'GET'
    });
  }

  // User Rankings API Methods
  async getUserRankings(params?: {
    period?: string;
    category?: string;
    level?: string;
    page?: number;
    limit?: number;
  }): Promise<APIResponse<any[]>> {
    const queryParams = new URLSearchParams();
    if (params?.period) queryParams.append('period', params.period);
    if (params?.category) queryParams.append('category', params.category);
    if (params?.level && params.level !== 'all') queryParams.append('level', params.level);
    if (params?.page) queryParams.append('page', params.page.toString());
    if (params?.limit) queryParams.append('limit', params.limit.toString());

    const endpoint = `/api/user-rankings${queryParams.toString() ? `?${queryParams.toString()}` : ''}`;
    return this.request(endpoint, {
      method: 'GET'
    });
  }

  // Authentication API Methods
  async login(credentials: {
    email: string;
    password: string;
  }): Promise<APIResponse<any>> {
    return this.request('/api/auth/login', {
      method: 'POST',
      body: JSON.stringify(credentials)
    }, false);
  }

  async register(userData: {
    email: string;
    password: string;
    displayName: string;
  }): Promise<APIResponse<any>> {
    return this.request('/api/auth/register', {
      method: 'POST',
      body: JSON.stringify(userData)
    }, false);
  }

  // Current User API
  async getCurrentUser(): Promise<APIResponse<any>> {
    return this.request('/api/user/profile', {
      method: 'GET'
    });
  }


  // AI Predictions API
  async getAIPredictions(params: {
    category?: string;
    limit?: number;
  }): Promise<APIResponse<any[]>> {
    const queryParams = new URLSearchParams();
    if (params.category) queryParams.append('category', params.category);
    if (params.limit) queryParams.append('limit', params.limit.toString());

    const endpoint = `/api/ai/predictions${queryParams.toString() ? `?${queryParams.toString()}` : ''}`;
    return this.request(endpoint, {
      method: 'GET'
    });
  }

  // Detailed Analysis API
  async getDetailedAnalysis(symbol: string): Promise<APIResponse<any>> {
    return this.request(`/api/analysis/${symbol}/detailed`, {
      method: 'GET'
    });
  }

  // Realtime API Methods
  async getRealtimeStocks(params: {
    category?: string;
    limit?: number;
  }): Promise<APIResponse<any[]>> {
    const queryParams = new URLSearchParams();
    if (params.category) queryParams.append('category', params.category);
    if (params.limit) queryParams.append('limit', params.limit.toString());

    const endpoint = `/api/realtime/stocks${queryParams.toString() ? `?${queryParams.toString()}` : ''}`;
    return this.request(endpoint, {
      method: 'GET'
    });
  }

  async getMarketStatus(): Promise<APIResponse<any>> {
    return this.request('/api/realtime/market-status', {
      method: 'GET'
    });
  }

  async getRealtimeAlerts(params: {
    limit?: number;
  }): Promise<APIResponse<any[]>> {
    const queryParams = new URLSearchParams();
    if (params.limit) queryParams.append('limit', params.limit.toString());

    const endpoint = `/api/realtime/alerts${queryParams.toString() ? `?${queryParams.toString()}` : ''}`;
    return this.request(endpoint, {
      method: 'GET'
    });
  }

  // Stock News API
  async getStockNews(symbol: string, params?: {
    limit?: number;
  }): Promise<APIResponse<any[]>> {
    const queryParams = new URLSearchParams();
    if (params?.limit) queryParams.append('limit', params.limit.toString());

    const endpoint = `/api/stocks/${symbol}/news${queryParams.toString() ? `?${queryParams.toString()}` : ''}`;
    return this.request(endpoint, {
      method: 'GET'
    });
  }

  // AI Stock Decision Factors API - matches existing pattern
  async getAIStockDecisionFactors(symbol: string): Promise<APIResponse<any>> {
    return this.getAIDecisionFactors(symbol);
  }


  async getUserRankingStats(): Promise<APIResponse<any>> {
    return this.request('/api/user-rankings/stats', {
      method: 'GET'
    });
  }

  async getUserDetailedRanking(userId: string): Promise<APIResponse<any>> {
    return this.request(`/api/user-rankings/users/${userId}`, {
      method: 'GET'
    });
  }

  clearCache() {
    this.cache.clear();
  }
  
  // 特定エンドポイントのキャッシュクリア
  clearCacheForEndpoint(endpoint: string) {
    this.cache.delete(endpoint);
  }
}

export const apiClient = new APIClient();
export default apiClient;