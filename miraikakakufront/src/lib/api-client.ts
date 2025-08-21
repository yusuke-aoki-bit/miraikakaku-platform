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

  constructor() {
    this.baseURL = process.env.NEXT_PUBLIC_API_BASE_URL || API_CONFIG.DEFAULT_BASE_URL;
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<APIResponse<T>> {
    try {
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

  // Enhanced stock search with currency filter
  async searchStocks(query: string, limit: number = PAGINATION.DEFAULT_PAGE_SIZE, currency?: string) {
    let url = `/api/finance/stocks/search?query=${encodeURIComponent(query)}&limit=${limit}`;
    if (currency) {
      url += `&currency=${currency}`;
    }
    return this.request(url);
  }

  // Get all available sectors
  async getSectors() {
    return this.request('/api/finance/stocks/sectors');
  }

  // Get stocks by sector
  async getStocksBySector(sectorId: string, limit: number = PAGINATION.SECTOR_STOCKS_LIMIT, currency: string = 'JPY') {
    return this.request(`/api/finance/stocks/sector/${encodeURIComponent(sectorId)}?limit=${limit}&currency=${currency}`);
  }

  // 株価履歴取得
  async getStockPrice(symbol: string, days: number = TIME_PERIODS.DEFAULT_PRICE_HISTORY_DAYS) {
    return this.request(`/api/finance/stocks/${symbol}/price?days=${days}`);
  }

  // 株価予測取得
  async getStockPredictions(symbol: string, modelType?: string, days: number = TIME_PERIODS.DEFAULT_PREDICTION_DAYS) {
    let url = `/api/finance/stocks/${symbol}/predictions?days=${days}`;
    if (modelType) {
      url += `&model_type=${encodeURIComponent(modelType)}`;
    }
    return this.request(url);
  }

  // 予測生成
  async createPrediction(symbol: string) {
    return this.request(`/api/finance/stocks/${symbol}/predict`, {
      method: 'POST',
    });
  }

  // 成長ポテンシャルランキング
  async getGrowthPotentialRankings(limit: number = PAGINATION.RANKING_LIMIT) {
    return this.request(`/api/finance/rankings/growth-potential?limit=${limit}`);
  }

  // 総合ランキング
  async getCompositeRankings(limit: number = PAGINATION.RANKING_LIMIT) {
    return this.request(`/api/finance/rankings/composite?limit=${limit}`);
  }

  // 精度ランキング
  async getAccuracyRankings(limit: number = PAGINATION.RANKING_LIMIT) {
    return this.request(`/api/finance/rankings/accuracy?limit=${limit}`);
  }

  // 過去予測データと実績の比較
  async getHistoricalPredictions(symbol: string, days: number = TIME_PERIODS.HISTORICAL_PREDICTIONS_DAYS) {
    return this.request(`/api/finance/stocks/${symbol}/historical-predictions?days=${days}`);
  }

  // マーケット概況（トレンド株）
  async getTrendingStocks(limit: number = PAGINATION.RANKING_LIMIT) {
    return this.getGrowthPotentialRankings(limit);
  }

  // 値上がりランキング
  async getGainersRankings(limit: number = PAGINATION.RANKING_LIMIT) {
    return this.getGrowthPotentialRankings(limit);
  }

  // 値下がりランキング  
  async getLosersRankings(limit: number = PAGINATION.RANKING_LIMIT) {
    return this.request(`/api/finance/rankings/growth-potential?limit=${limit * 2}`)
      .then(response => {
        if (response.status === 'success' && response.data && Array.isArray(response.data)) {
          // 成長ポテンシャルが負の銘柄を抽出
          const losers = response.data
            .filter((stock: any) => stock.growth_potential < 0)
            .sort((a: any, b: any) => a.growth_potential - b.growth_potential)
            .slice(0, limit);
          return { ...response, data: losers };
        }
        return response;
      });
  }

  // 出来高ランキング（総合ランキングをベースに）
  async getVolumeRankings(limit: number = PAGINATION.RANKING_LIMIT) {
    return this.getCompositeRankings(limit);
  }

  // ヘルスチェック
  async healthCheck() {
    return this.request('/health');
  }
}

export const apiClient = new APIClient();
export default apiClient;