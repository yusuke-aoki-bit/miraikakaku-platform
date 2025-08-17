// 統一APIクライアント

interface APIResponse<T = any> {
  data?: T;
  error?: string;
  message?: string;
  status: 'success' | 'error';
}

class APIClient {
  private baseURL: string;

  constructor() {
    this.baseURL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000';
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

  // 株式検索
  async searchStocks(query: string, limit: number = 10) {
    return this.request(`/api/finance/stocks/search?query=${encodeURIComponent(query)}&limit=${limit}`);
  }

  // 株価履歴取得
  async getStockPrice(symbol: string, days: number = 30) {
    return this.request(`/api/finance/stocks/${symbol}/price?days=${days}`);
  }

  // 株価予測取得
  async getStockPredictions(symbol: string, modelName?: string, days: number = 7) {
    let url = `/api/finance/stocks/${symbol}/predictions?days=${days}`;
    if (modelName) {
      url += `&model_name=${encodeURIComponent(modelName)}`;
    }
    return this.request(url);
  }

  // 予測生成
  async createPrediction(symbol: string) {
    return this.request(`/api/finance/stocks/${symbol}/predict`, {
      method: 'POST',
    });
  }

  // ヘルスチェック
  async healthCheck() {
    return this.request('/health');
  }
}

export const apiClient = new APIClient();
export default apiClient;