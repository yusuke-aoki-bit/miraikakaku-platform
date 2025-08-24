// 統一APIクライアント

import { API_CONFIG, PAGINATION, TIME_PERIODS } from '@/config/constants';

interface APIResponse<T = any> {
  data?: T;
  error?: string;
  message?: string;
  status: 'success' | 'error';
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
            status: 'success',
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
          status: 'error',
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
        status: 'success',
        data,
      };
    } catch (error) {
      return {
        status: 'error',
        error: error instanceof Error ? error.message : '不明なエラー',
      };
    }
  }

  // Enhanced stock search - align with production API
  async searchStocks(query: string, limit: number = PAGINATION.DEFAULT_PAGE_SIZE) {
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

  // テーマ洞察取得 - production API endpoint  
  async getThemeInsights() {
    return this.request('/api/insights/themes');
  }

  // 特定テーマの洞察取得 - production API endpoint
  async getThemeInsightByName(themeName: string, limit: number = PAGINATION.DEFAULT_PAGE_SIZE) {
    return this.request(`/api/insights/themes/${encodeURIComponent(themeName)}?limit=${limit}`);
  }

  // ユーザープロファイル取得（モック実装）- production API endpoint
  async getUserProfile(userId: string) {
    return this.request(`/api/users/${userId}/profile`);
  }

  // 成長ポテンシャルランキング（動的生成）- updated for production API
  async getGrowthPotentialRankings(limit: number = PAGINATION.RANKING_LIMIT) {
    try {
      // まず人気銘柄のリストを取得
      const popularSymbols = ['AAPL', 'GOOGL', 'MSFT', 'TSLA', 'AMZN', 'NVDA', 'META', '7203', '6758', '9984'];
      const stocks = [];
      
      for (const symbol of popularSymbols.slice(0, limit)) {
        try {
          const priceResponse = await this.getStockPrice(symbol, 1);
          const predictionResponse = await this.getStockPredictions(symbol, undefined, 1);
          
          if (priceResponse.status === 'success' && predictionResponse.status === 'success') {
            const priceData = (priceResponse as any).data?.[0];
            const predictionData = (predictionResponse as any).data?.[0];
            
            if (priceData && predictionData) {
              const currentPrice = priceData.close_price;
              const predictedPrice = predictionData.predicted_price;
              const growthPotential = ((predictedPrice - currentPrice) / currentPrice) * 100;
              
              stocks.push({
                symbol,
                company_name: priceData.symbol || symbol,
                current_price: currentPrice,
                predicted_price: predictedPrice,
                growth_potential: growthPotential,
                confidence: predictionData.confidence_score || 0.75,
                prediction_count: 1
              });
            }
          }
        } catch (error) {
          console.warn(`Failed to get data for ${symbol}:`, error);
        }
      }
      
      // 成長ポテンシャルでソート
      stocks.sort((a, b) => b.growth_potential - a.growth_potential);
      
      return {
        status: 'success' as const,
        data: stocks
      };
    } catch (error) {
      return {
        status: 'error' as const,
        error: error instanceof Error ? error.message : '成長ポテンシャル取得エラー'
      };
    }
  }

  // 総合ランキング（動的生成）
  async getCompositeRankings(limit: number = PAGINATION.RANKING_LIMIT) {
    return this.getGrowthPotentialRankings(limit);
  }

  // 精度ランキング（動的生成）
  async getAccuracyRankings(limit: number = PAGINATION.RANKING_LIMIT) {
    return this.getGrowthPotentialRankings(limit);
  }

  // 株式詳細情報取得（株価と予測を組み合わせ）
  async getStockDetails(symbol: string) {
    try {
      const [priceResponse, predictionResponse] = await Promise.all([
        this.getStockPrice(symbol, 30),
        this.getStockPredictions(symbol, undefined, 10)
      ]);
      
      return {
        status: 'success' as const,
        data: {
          symbol,
          prices: priceResponse.status === 'success' ? priceResponse.data : [],
          predictions: predictionResponse.status === 'success' ? predictionResponse.data : []
        }
      };
    } catch (error) {
      return {
        status: 'error' as const,
        error: error instanceof Error ? error.message : '株式詳細取得エラー'
      };
    }
  }

  // マーケット概況（トレンド株）
  async getTrendingStocks(limit: number = PAGINATION.RANKING_LIMIT) {
    const response = await this.getGrowthPotentialRankings(limit);
    if (response.status === 'success' && response.data) {
      // 上位成長ポテンシャル銘柄をトレンドとして表示
      const trending = response.data.slice(0, limit);
      return { ...response, data: trending };
    }
    return response;
  }

  // 値上がりランキング
  async getGainersRankings(limit: number = PAGINATION.RANKING_LIMIT) {
    const response = await this.getGrowthPotentialRankings(limit * 2);
    if (response.status === 'success' && response.data) {
      // 成長ポテンシャルがプラスの銘柄を抽出
      const gainers = response.data
        .filter((stock: any) => stock.growth_potential > 0)
        .sort((a: any, b: any) => b.growth_potential - a.growth_potential)
        .slice(0, limit);
      return { ...response, data: gainers };
    }
    return response;
  }

  // 値下がりランキング  
  async getLosersRankings(limit: number = PAGINATION.RANKING_LIMIT) {
    const response = await this.getGrowthPotentialRankings(limit * 2);
    if (response.status === 'success' && response.data) {
      // 成長ポテンシャルが負の銘柄を抽出
      const losers = response.data
        .filter((stock: any) => stock.growth_potential < 0)
        .sort((a: any, b: any) => a.growth_potential - b.growth_potential)
        .slice(0, limit);
      return { ...response, data: losers };
    }
    return response;
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

  async getEconomicCalendar(date?: string, country?: string) {
    let url = '/api/forex/economic-calendar';
    const params = [];
    if (date) params.push(`date=${date}`);
    if (country) params.push(`country=${country}`);
    if (params.length > 0) url += '?' + params.join('&');
    return this.request(url);
  }

  // ヘルスチェック
  async healthCheck() {
    return this.request('/health', {}, false); // ヘルスチェックはキャッシュしない
  }
  
  // キャッシュクリア
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