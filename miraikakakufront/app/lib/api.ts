import axios, { AxiosError, AxiosResponse } from 'axios';
import {
  StockPrice,
  StockPrediction,
  HistoricalPrediction,
  StockDetails,
  AIDecisionFactor,
  SearchResult,
  DualPredictionResponse,
  SinglePrediction
} from '../types';
import {
  ApiError,
  StockSearchResponse,
  HealthCheckResponse,
  API_ENDPOINTS,
  isApiError
} from '../types/api.types';

const API_BASE_URL = (() => {
  const url = process.env.NEXT_PUBLIC_API_URL;
  if (!url) {
    return 'http://localhost:8080';
  }
  return url;
})();
const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000, // Increased timeout to 30 seconds
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
  },
  paramsSerializer: (params) => {
    return Object.keys(params)
      .map(key => `${encodeURIComponent(key)}=${encodeURIComponent(params[key])}`)
      .join('&');
  }
});
// Request interceptor for logging
api.interceptors.request.use(
  (config) => {
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);
// Response interceptor for logging and error handling
api.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    return Promise.reject(error);
  }
);
/**
 * API接続エラーハンドリング（エラーを投げる）
 * API connection error handling (throws errors)
 */
const handleApiError = (error: unknown): never => {
  if (axios.isAxiosError(error)) {
    const axiosError = error as AxiosError<ApiError>;

    if (axiosError.response) {
      const { status, data } = axiosError.response;
      const errorMessage = isApiError(data) ? data.error : '不明なAPIエラーが発生しました';
      console.error(`API Response Error (${status}):`, errorMessage);
      // 特定のステータスコードに基づく詳細なログ
      if (status >= 500) {
        throw new Error(`サーバーエラー (${status}): ${errorMessage}`);
      } else if (status === 404) {
        throw new Error(`データが見つかりません: ${errorMessage}`);
      } else if (status === 429) {
        throw new Error(`レート制限エラー: ${errorMessage}`);
      } else {
        throw new Error(`APIエラー (${status}): ${errorMessage}`);
      }
    } else if (axiosError.request) {
      throw new Error('接続エラー: サーバーに接続できません');
    } else {
      throw new Error(`リクエストエラー: ${axiosError.message}`);
    }
  } else {
    throw new Error('予期しないエラーが発生しました');
  }
};

/**
 * リトライ機能付きAPIコール実行（エラー時は例外を投げる）
 * API call execution with retry functionality (throws on error)
 */
const makeApiCallWithRetry = async <T>(
  requestFn: () => Promise<AxiosResponse<T>>,
  maxRetries: number = 3,
  retryDelay: number = 1000
): Promise<T> => {
  let lastError: unknown;

  for (let attempt = 1; attempt <= maxRetries; attempt++) {
    try {
      const response = await requestFn();
      // レスポンスの妥当性を検証
      if (!response.data) {
        throw new Error('API レスポンスにデータが含まれていません');
      }

      return response.data;
    } catch (error) {
      lastError = error;

      // 最後の試行でない場合はリトライ
      if (attempt < maxRetries) {
        const delay = retryDelay * Math.pow(2, attempt - 1); // エクスポネンシャルバックオフ
        if (process.env.NODE_ENV === 'development') {
          console.log(`API call failed, retrying in ${delay}ms...`);
        }
        await new Promise(resolve => setTimeout(resolve, delay));
      }
    }
  }

  handleApiError(lastError);
  throw new Error('All retry attempts failed'); // This should never be reached
};

/**
 * APIコール実行（エラー時は例外を投げる）
 * API call execution (throws on error)
 */
const makeApiCall = async <T>(
  requestFn: () => Promise<AxiosResponse<T>>
): Promise<T> => {
  return makeApiCallWithRetry(requestFn, 2, 500);
};


/**
 * システム関連API（型安全）
 * System-related APIs with type safety
 */
export const systemAPI = {
  getMetrics: async (): Promise<Record<string, unknown> | null> => {
    try {
      return await makeApiCall(() => api.get<Record<string, unknown>>(API_ENDPOINTS.SYSTEM_METRICS));
    } catch (error) {
      throw error;
    }
  },
  getJobs: async (): Promise<unknown[]> => {
    try {
      return await makeApiCall(() => api.get<unknown[]>('/api/system/jobs'));
    } catch (error) {
      throw error;
    }
  },
  getHealth: async (): Promise<HealthCheckResponse> => {
    try {
      return await makeApiCall(() => api.get<HealthCheckResponse>(API_ENDPOINTS.HEALTH));
    } catch (error) {
      throw error;
    }
  },
  getStatus: async (): Promise<Record<string, unknown> | null> => {
    try {
      return await makeApiCall(() => api.get<Record<string, unknown>>(API_ENDPOINTS.SYSTEM_STATUS));
    } catch (error) {
      throw error;
    }
  }
} as const;

export const stockAPI = {
  search: async (
    query: string,
    limit: number = 10,
    market?: string,
    sortBy?: string
  ): Promise<SearchResult[]> => {
    // 入力検証
    if (!query || typeof query !== 'string' || query.trim().length === 0) {
      return [];
    }

    if (limit <= 0 || limit > 50) {
      return [];
    }

    const companyNameMap: Record<string, string> = {
      'アップル': 'AAPL', 'apple': 'AAPL',
      'マイクロソフト': 'MSFT', 'microsoft': 'MSFT',
      'グーグル': 'GOOGL', 'google': 'GOOGL', 'alphabet': 'GOOGL',
      'アマゾン': 'AMZN', 'amazon': 'AMZN',
      'テスラ': 'TSLA', 'tesla': 'TSLA',
      'エヌビディア': 'NVDA', 'nvidia': 'NVDA',
      'メタ': 'META', 'meta': 'META', 'フェイスブック': 'META', 'facebook': 'META',
      'ネットフリックス': 'NFLX', 'netflix': 'NFLX',
      'トヨタ': '7203.T', 'トヨタ自動車': '7203.T', 'toyota': '7203.T',
      'ソニー': '6758.T', 'ソニーグループ': '6758.T', 'sony': '6758.T'
    } as const;

    const normalizedQuery = query.toLowerCase().trim();
    const mappedSymbol = companyNameMap[query] || companyNameMap[normalizedQuery];
    const searchQuery = mappedSymbol || query;

    // 日本語クエリでマッピングが見つからない場合は空配列を返す
    if (/[\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FAF]/.test(query) && !mappedSymbol) {
      return [];
    }

    // Enhanced search parameters
    const params: Record<string, any> = { q: searchQuery, limit };
    if (market && market !== 'all') {
      params.market = market;
    }
    if (sortBy) {
      params.sort_by = sortBy;
    }

    try {
      const result = await makeApiCall(
        () => api.get<StockSearchResponse>(API_ENDPOINTS.STOCK_SEARCH, { params })
      );
      return result.results || [];
    } catch (error) {
      throw error;
    }
  },
  // New enhanced search methods
  searchSuggestions: async (query: string): Promise<{symbol: string, display: string, type: string}[]> => {
    if (!query || query.length < 1) return [];

    try {
      const result = await makeApiCall(
        () => api.get('/api/finance/stocks/search/suggestions', { params: { q: query } })
      );
      return result.suggestions || [];
    } catch (error) {
      return [];
    }
  },
  getPopularStocks: async (): Promise<SearchResult[]> => {
    try {
      const result = await makeApiCall(
        () => api.get('/api/finance/stocks/search/popular')
      );
      return result.popular_stocks || [];
    } catch (error) {
      return [];
    }
  },
  getMarketsSummary: async (): Promise<Record<string, any>> => {
    try {
      const result = await makeApiCall(
        () => api.get('/api/finance/markets/summary')
      );
      return result;
    } catch (error) {
      throw error;
    }
  },
  getPriceHistory: async (symbol: string, days: number = 90): Promise<StockPrice[]> => {
    let response;
    try {
      response = await makeApiCallWithRetry(
        () => api.get(`/api/finance/stocks/${symbol}/price`, { params: { days } }),
        3, // 重要なデータのため3回リトライ
        1000
      );
    } catch (error) {
      console.error(`Failed to get price history for ${symbol}:`, error);
      // API接続エラーの場合はサンプルデータを返さずにエラーを投げる
      throw error;
    }
    // Handle case where API returns error object instead of array
    if (Array.isArray(response) && response.length > 0) {
      // Transform API response to ensure all required fields
      const transformedPrices: StockPrice[] = response.map((item: any, index: number) => ({
        id: item.id || `price_${symbol}_${item.date}_${index}`,
        symbol: item.symbol || symbol,
        date: item.date,
        open_price: item.open_price,
        high_price: item.high_price,
        low_price: item.low_price,
        close_price: item.close_price,
        volume: item.volume,
        created_at: item.created_at
      }));
      return transformedPrices;
    } else if (response && typeof response === 'object' && 'detail' in response) {
      console.warn(`API returned error for ${symbol}:`, response);
    }

    // API接続エラーの場合は空配列を返す
    return [];
  },
  // New dual prediction system - LSTM + VertexAI
  getDualPredictions: async (symbol: string, timeframe: string = '1d'): Promise<DualPredictionResponse | null> => {
    try {
      const response = await makeApiCallWithRetry(
        () => api.get(`/api/finance/stocks/${symbol}/dual-predictions`, { params: { timeframe } }),
        3,
        1000
      );
      return response as DualPredictionResponse;
    } catch (error) {
      console.error(`Failed to get dual predictions for ${symbol}:`, error);
      return null;
    }
  },
  // LSTM only predictions
  getLSTMPredictions: async (symbol: string, timeframe: string = '1d'): Promise<SinglePrediction | null> => {
    try {
      const response = await makeApiCallWithRetry(
        () => api.get(`/api/finance/stocks/${symbol}/lstm-predictions`, { params: { timeframe } }),
        3,
        1000
      );
      return response as SinglePrediction;
    } catch (error) {
      console.error(`Failed to get LSTM predictions for ${symbol}:`, error);
      return null;
    }
  },
  // VertexAI only predictions
  getVertexAIPredictions: async (symbol: string, timeframe: string = '1d'): Promise<SinglePrediction | null> => {
    try {
      const response = await makeApiCallWithRetry(
        () => api.get(`/api/finance/stocks/${symbol}/vertexai-predictions`, { params: { timeframe } }),
        3,
        1000
      );
      return response as SinglePrediction;
    } catch (error) {
      console.error(`Failed to get VertexAI predictions for ${symbol}:`, error);
      return null;
    }
  },
  // Legacy function - now uses dual predictions system
  getPredictions: async (symbol: string): Promise<StockPrediction[]> => {
    try {
      // Use dual prediction system and convert to legacy format
      const response = await makeApiCallWithRetry(
        () => api.get(`/api/finance/stocks/${symbol}/dual-predictions`, { params: { timeframe: '1d' } }),
        3,
        1000
      );
      const dualPredictions = response as DualPredictionResponse;
      if (!dualPredictions) {
        return [];
      }

      // Convert dual predictions to legacy format for compatibility
      const predictions: StockPrediction[] = [
        {
          id: `${symbol}_lstm_${Date.now()}`,
          symbol: symbol,
          prediction_date: dualPredictions.predictions.lstm.prediction_date?.split('T')[0] || '',
          predicted_price: dualPredictions.predictions.lstm.predicted_price,
          confidence_score: dualPredictions.predictions.lstm.confidence_score,
          model_name: 'LSTM',
          created_at: dualPredictions.timestamp?.split('T')[0] || '',
          confidence: dualPredictions.predictions.lstm.confidence_score,
          model_version: dualPredictions.predictions.lstm.model_type
        },
        {
          id: `${symbol}_vertex_${Date.now()}`,
          symbol: symbol,
          prediction_date: dualPredictions.predictions.vertex_ai.prediction_date?.split('T')[0] || '',
          predicted_price: dualPredictions.predictions.vertex_ai.predicted_price,
          confidence_score: dualPredictions.predictions.vertex_ai.confidence_score,
          model_name: 'VertexAI',
          created_at: dualPredictions.timestamp?.split('T')[0] || '',
          confidence: dualPredictions.predictions.vertex_ai.confidence_score,
          model_version: dualPredictions.predictions.vertex_ai.model_type
        }
      ];

      return predictions;
    } catch (error) {
      console.error(`Failed to get predictions for ${symbol}:`, error);
      return [];
    }
  },
  getHistoricalPredictions: async (symbol: string, days: number = 90): Promise<HistoricalPrediction[]> => {
    let response;
    try {
      response = await makeApiCall(
        () => api.get(`/api/finance/stocks/${symbol}/historical-predictions`, { params: { days } })
      );
    } catch (error) {
      console.error(`Failed to get historical predictions for ${symbol}:`, error);
      // API接続エラーの場合は空配列を返す
      return [];
    }

    // Transform API response to match frontend interface
    if (Array.isArray(response) && response.length > 0) {
      const transformedHistoricalPredictions: HistoricalPrediction[] = response.map((item: any) => ({
        id: item.id || `hist_pred_${symbol}_${item.date}`,
        symbol: symbol,
        predicted_price: item.predicted || item.predicted_price,
        actual_price: item.actual || item.actual_price,
        target_date: item.date, // Map 'date' field to 'target_date'
        actual_date: item.date, // Also map to actual_date for compatibility
        prediction_date: item.prediction_made_date || item.date,
        accuracy_percentage: item.accuracy_percentage,
        accuracy_score: item.was_accurate ? 1.0 : 0.0,
        model_name: item.model_name || 'Historical Model',
        confidence_score: item.confidence || item.confidence_score,
        created_at: item.created_at,
        is_validated: item.was_accurate !== undefined,
        // Legacy fields
        accuracy: item.accuracy || (item.was_accurate ? 100 : 0)
      }));
      return transformedHistoricalPredictions;
    }

    if (!response || response.length === 0) {
      return [];
    }

    return [];
  },
  getAIFactors: async (symbol: string): Promise<AIDecisionFactor[]> => {
    let response;
    try {
      response = await makeApiCall(
        () => api.get(`/api/finance/stocks/${symbol}/analysis/ai`)
      );
    } catch (error) {
      console.error(`Failed to get AI factors for ${symbol}:`, error);
      return [];
    }
    // Handle case where API returns AI analysis object with decision_factors
    if (response && 'decision_factors' in response && Array.isArray(response.decision_factors)) {
      return response.decision_factors;
    } else if (Array.isArray(response)) {
      return response;
    } else if (response && typeof response === 'object' && 'detail' in response) {
      return [];
    }
    return [];
  },
  getFinancialAnalysis: async (symbol: string): Promise<any> => {
    try {
      const response = await makeApiCall(
        () => api.get(`/api/finance/stocks/${symbol}/analysis/financial`)
      );
      return response;
    } catch (error) {
      console.error(`Failed to get financial analysis for ${symbol}:`, error);
      throw error;
    }
  },
  getRiskAnalysis: async (symbol: string): Promise<any> => {
    try {
      const response = await makeApiCall(
        () => api.get(`/api/finance/stocks/${symbol}/analysis/risk`)
      );
      return response;
    } catch (error) {
      console.error(`Failed to get risk analysis for ${symbol}:`, error);
      throw error;
    }
  },
  // Prediction rankings endpoint
  getPredictionRankings: async (
    timeframe: string = '7d',
    limit: number = 20,
    type: string = 'best_predictions'
  ): Promise<any[]> => {
    try {
      const result = await makeApiCall(
        () => api.get(`/api/finance/rankings/predictions`, { params: { timeframe, limit, type } })
      );
      return result.predictions_ranking || result.predictions || [];
    } catch (error) {
      throw error;
    }
  },
  // Database status endpoint
  getDatabaseStatus: async (): Promise<any> => {
    try {
      const result = await makeApiCall(
        () => api.get(`/api/system/database/status`)
      );
      return result.status || {};
    } catch (error) {
      throw error;
    }
  },

  // Stock details endpoint
  getStockDetails: async (symbol: string): Promise<StockDetails | null> => {
    try {
      const result = await makeApiCall(
        () => api.get(`/api/finance/stocks/${symbol}/details`)
      );
      return result || null;
    } catch (error) {
      console.error(`Failed to get stock details for ${symbol}:`, error);
      // Return minimal details based on symbol
      return {
        symbol: symbol.toUpperCase(),
        longName: symbol.toUpperCase(),
        shortName: symbol.toUpperCase(),
        sector: 'Unknown',
        industry: 'Unknown',
        country: 'Unknown'
      };
    }
  },

  // Get all stock data (combines multiple endpoints)
  getAllStockData: async (symbol: string): Promise<any> => {
    try {
      const [
        priceHistory,
        predictions,
        historicalPredictions,
        details,
        aiFactors,
        financialAnalysis,
        riskAnalysis
      ] = await Promise.allSettled([
        stockAPI.getPriceHistory(symbol),
        stockAPI.getPredictions(symbol),
        stockAPI.getHistoricalPredictions(symbol),
        stockAPI.getStockDetails(symbol),
        stockAPI.getAIFactors(symbol),
        stockAPI.getFinancialAnalysis(symbol),
        stockAPI.getRiskAnalysis(symbol)
      ]);

      return {
        priceHistory: priceHistory.status === 'fulfilled' ? priceHistory.value : [],
        predictions: predictions.status === 'fulfilled' ? predictions.value : [],
        historicalPredictions: historicalPredictions.status === 'fulfilled' ? historicalPredictions.value : [],
        details: details.status === 'fulfilled' ? details.value : null,
        aiFactors: aiFactors.status === 'fulfilled' ? aiFactors.value : [],
        financialAnalysis: financialAnalysis.status === 'fulfilled' ? financialAnalysis.value : null,
        riskAnalysis: riskAnalysis.status === 'fulfilled' ? riskAnalysis.value : null
      };
    } catch (error) {
      console.error(`Failed to get all stock data for ${symbol}:`, error);
      throw error;
    }
  }
};